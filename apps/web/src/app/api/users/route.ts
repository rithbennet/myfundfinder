import { NextResponse } from "next/server";
import { db } from "~/server/db";

export async function GET() {
  try {
    const users = await db.user.findMany({
      include: {
        company: true,
        chatSessions: true,
      },
    });
    return NextResponse.json({ users });
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch users" }, { status: 500 });
  }
}
