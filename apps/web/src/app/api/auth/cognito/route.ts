import { NextRequest, NextResponse } from "next/server";
import {
  CognitoIdentityProviderClient,
  SignUpCommand,
  ConfirmSignUpCommand,
  InitiateAuthCommand,
  ForgotPasswordCommand,
  ConfirmForgotPasswordCommand,
  GetUserCommand,
} from "@aws-sdk/client-cognito-identity-provider";
import { createHmac } from "crypto";
import { ensureUser } from "~/feature/auth/api/user";

const client = new CognitoIdentityProviderClient({
  region: process.env.COGNITO_REGION!,
});

const CLIENT_ID = process.env.COGNITO_CLIENT_ID!;
const CLIENT_SECRET = process.env.COGNITO_CLIENT_SECRET!;

// Cache user data to avoid repeated Cognito API calls
const userDataCache = new Map<string, { username: string; email: string; id: string }>();

// Generate SECRET_HASH for Cognito requests
const generateSecretHash = (username: string): string => {
  return createHmac("sha256", CLIENT_SECRET)
    .update(username + CLIENT_ID)
    .digest("base64");
};

// Extract user data from Cognito response
const extractUserData = (userResult: any) => {
  const cognitoUserId = userResult.UserAttributes?.find((attr: any) => attr.Name === "sub")?.Value!;
  const email = userResult.UserAttributes?.find((attr: any) => attr.Name === "email")?.Value!;
  return {
    username: userResult.Username!,
    email,
    id: cognitoUserId,
  };
};

export async function POST(request: NextRequest) {
  try {
    const { action, ...data } = await request.json();

    switch (action) {
      case "signUp":
        const signUpCommand = new SignUpCommand({
          ClientId: CLIENT_ID,
          Username: data.email,
          Password: data.password,
          SecretHash: generateSecretHash(data.email),
          UserAttributes: [{ Name: "email", Value: data.email }],
        });
        const signUpResult = await client.send(signUpCommand);
        return NextResponse.json({
          success: true,
          userSub: signUpResult.UserSub,
        });

      case "confirmSignUp":
        const confirmCommand = new ConfirmSignUpCommand({
          ClientId: CLIENT_ID,
          Username: data.email,
          ConfirmationCode: data.code,
          SecretHash: generateSecretHash(data.email),
        });
        await client.send(confirmCommand);
        return NextResponse.json({ success: true });

      case "signIn":
        const authCommand = new InitiateAuthCommand({
          ClientId: CLIENT_ID,
          AuthFlow: "USER_PASSWORD_AUTH",
          AuthParameters: {
            USERNAME: data.email,
            PASSWORD: data.password,
            SECRET_HASH: generateSecretHash(data.email),
          },
        });
        const authResult = await client.send(authCommand);
        
        // Only get user details and ensure user exists once per session
        if (authResult.AuthenticationResult?.AccessToken) {
          const getUserCommand = new GetUserCommand({
            AccessToken: authResult.AuthenticationResult.AccessToken,
          });
          const userResult = await client.send(getUserCommand);
          const userData = extractUserData(userResult);
          
          // Cache user data and ensure user exists in DB
          userDataCache.set(userData.id, userData);
          await ensureUser(userData.id, userData.email);
        }
        
        return NextResponse.json({
          success: true,
          tokens: authResult.AuthenticationResult,
        });

      case "forgotPassword":
        const forgotCommand = new ForgotPasswordCommand({
          ClientId: CLIENT_ID,
          Username: data.email,
          SecretHash: generateSecretHash(data.email),
        });
        await client.send(forgotCommand);
        return NextResponse.json({ success: true });

      case "confirmForgotPassword":
        const confirmForgotCommand = new ConfirmForgotPasswordCommand({
          ClientId: CLIENT_ID,
          Username: data.email,
          ConfirmationCode: data.code,
          Password: data.newPassword,
          SecretHash: generateSecretHash(data.email),
        });
        await client.send(confirmForgotCommand);
        return NextResponse.json({ success: true });

      case "getUser":
        // Check cache first to avoid Cognito API call
        const cachedUser = Array.from(userDataCache.values()).find(user => 
          user.email === data.email || user.id === data.userId
        );
        
        if (cachedUser) {
          return NextResponse.json({ success: true, user: cachedUser });
        }

        const getUserCommand = new GetUserCommand({
          AccessToken: data.accessToken,
        });
        const userResult = await client.send(getUserCommand);
        const userData = extractUserData(userResult);
        
        // Cache user data and ensure user exists in DB
        userDataCache.set(userData.id, userData);
        await ensureUser(userData.id, userData.email);
        
        return NextResponse.json({ success: true, user: userData });

      default:
        return NextResponse.json(
          { success: false, error: "Invalid action" },
          { status: 400 },
        );
    }
  } catch (error: any) {
    return NextResponse.json(
      {
        success: false,
        error: error.message || "Authentication failed",
      },
      { status: 400 },
    );
  }
}
