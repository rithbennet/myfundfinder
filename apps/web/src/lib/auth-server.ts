import { cookies } from "next/headers";
import {
  CognitoIdentityProviderClient,
  GetUserCommand,
} from "@aws-sdk/client-cognito-identity-provider";

/* eslint-disable @typescript-eslint/no-unsafe-member-access */
/* eslint-disable @typescript-eslint/no-unsafe-assignment */
/* eslint-disable @typescript-eslint/prefer-optional-chain */
/* eslint-disable @typescript-eslint/no-unsafe-return */

const extractUserData = (userResult: any) => {
  const cognitoUserId = userResult.UserAttributes?.find(
    (attr: any) => attr.Name === "sub",
  )?.Value!;
  const email = userResult.UserAttributes?.find(
    (attr: any) => attr.Name === "email",
  )?.Value!;
  return {
    username: userResult.Username!,
    email,
    id: cognitoUserId,
  };
};

const client = new CognitoIdentityProviderClient({
  region: process.env.COGNITO_REGION!,
});

export async function getSessionUser() {
  const cookieStore = cookies();
  const accessToken = (await cookieStore).get("auth-token")?.value;
  
  console.log("🍪 All cookies:", (await cookieStore).getAll());
  console.log("🔑 Access token found:", !!accessToken);
  console.log("🔑 Access token value:", accessToken ? "present" : "missing");

  if (!accessToken) return null;

  try {
    const getUserCommand = new GetUserCommand({ AccessToken: accessToken });
    const userResult = await client.send(getUserCommand);
    return extractUserData(userResult);
  } catch (err) {
    console.error("❌ Error getting user from Cognito:", err);
    return null;
  }
}
