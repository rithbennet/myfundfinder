import { NextRequest, NextResponse } from 'next/server';
import { 
  CognitoIdentityProviderClient, 
  SignUpCommand, 
  InitiateAuthCommand,
  ConfirmSignUpCommand,
  GetUserCommand,
  ForgotPasswordCommand,
  ConfirmForgotPasswordCommand
} from '@aws-sdk/client-cognito-identity-provider';
import { createHmac } from 'crypto';

const client = new CognitoIdentityProviderClient({ region: 'us-east-1' });
const CLIENT_ID = '1e4mq62922lj0qoepj7sckd9o1';
const CLIENT_SECRET = '1cj9i7t3hp6f7m01ctgcd9s644k50d06r7tc6saasl3hjpu9ib7m';

const calculateSecretHash = (username: string) => {
  return createHmac('sha256', CLIENT_SECRET)
    .update(username + CLIENT_ID)
    .digest('base64');
};

export async function POST(request: NextRequest) {
  try {
    const { action, email, password, code, accessToken, newPassword } = await request.json();

    switch (action) {
      case 'signUp':
        const signUpCommand = new SignUpCommand({
          ClientId: CLIENT_ID,
          Username: email,
          Password: password,
          SecretHash: calculateSecretHash(email),
          UserAttributes: [{ Name: 'email', Value: email }]
        });
        const signUpResponse = await client.send(signUpCommand);
        return NextResponse.json({ success: true, userSub: signUpResponse.UserSub });

      case 'confirmSignUp':
        const confirmCommand = new ConfirmSignUpCommand({
          ClientId: CLIENT_ID,
          Username: email,
          ConfirmationCode: code,
          SecretHash: calculateSecretHash(email)
        });
        await client.send(confirmCommand);
        return NextResponse.json({ success: true });

      case 'signIn':
        const signInCommand = new InitiateAuthCommand({
          ClientId: CLIENT_ID,
          AuthFlow: 'USER_PASSWORD_AUTH',
          AuthParameters: {
            USERNAME: email,
            PASSWORD: password,
            SECRET_HASH: calculateSecretHash(email)
          }
        });
        const signInResponse = await client.send(signInCommand);
        return NextResponse.json({ 
          success: true, 
          tokens: signInResponse.AuthenticationResult 
        });

      case 'getUser':
        const getUserCommand = new GetUserCommand({
          AccessToken: accessToken
        });
        const userResponse = await client.send(getUserCommand);
        const userInfo = {
          username: userResponse.Username,
          email: userResponse.UserAttributes?.find(attr => attr.Name === 'email')?.Value
        };
        return NextResponse.json({ success: true, user: userInfo });

      case 'forgotPassword':
        const forgotPasswordCommand = new ForgotPasswordCommand({
          ClientId: CLIENT_ID,
          Username: email,
          SecretHash: calculateSecretHash(email)
        });
        await client.send(forgotPasswordCommand);
        return NextResponse.json({ success: true });

      case 'confirmForgotPassword':
        const confirmForgotPasswordCommand = new ConfirmForgotPasswordCommand({
          ClientId: CLIENT_ID,
          Username: email,
          ConfirmationCode: code,
          Password: newPassword,
          SecretHash: calculateSecretHash(email)
        });
        await client.send(confirmForgotPasswordCommand);
        return NextResponse.json({ success: true });

      default:
        return NextResponse.json({ success: false, error: 'Invalid action' }, { status: 400 });
    }
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 400 });
  }
}
