import { db } from "~/server/db";

// In-memory cache to avoid repeated DB calls within the same session
const userCache = new Map<string, boolean>();

export async function ensureUser(
  cognitoUserId: string,
  email: string,
  name?: string,
) {
  // Check cache first
  if (userCache.has(cognitoUserId)) {
    return;
  }

  try {
    await db.user.upsert({
      where: { id: cognitoUserId },
      update: {},
      create: {
        id: cognitoUserId,
        email,
        name,
      },
    });
    
    // Cache the user to avoid future DB calls
    userCache.set(cognitoUserId, true);
  } catch (error) {
    // If user already exists (race condition), cache it
    if (error instanceof Error && error.message.includes('unique constraint')) {
      userCache.set(cognitoUserId, true);
    } else {
      throw error;
    }
  }
}
