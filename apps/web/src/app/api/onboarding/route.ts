/* eslint-disable @typescript-eslint/no-unsafe-member-access */
/* eslint-disable @typescript-eslint/no-unsafe-call */
/* eslint-disable @typescript-eslint/no-unsafe-assignment */
import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { z } from "zod";

const onboardingSchema = z.object({
  userId: z.string(),
  companyName: z.string(),
  companyId: z.string(),
  companyType: z.string(),
  incorporationDate: z.string(),
  shareholding: z.string(),
  industry: z.string(),
  yearsOperating: z.string(),
  annual_revenue: z.string(), // renamed from revenue
  employees: z.string(),
  exports: z.boolean(), // boolean instead of string
  address: z.string(),
  contact: z.string(),
  taxCompliance: z.string(),
  directors: z.array(z.string()).optional(), // optional, store as Json if needed
});

export async function POST(req: NextRequest) {
  try {
    const bodyRaw = await req.json();

    // Convert exports from "Yes"/"No" to boolean
    if (typeof bodyRaw.exports === "string") {
  bodyRaw.exports = bodyRaw.exports.toLowerCase() === "yes";
}

    // Map revenue to annual_revenue
    if (bodyRaw.revenue) {
      bodyRaw.annual_revenue = bodyRaw.revenue;
      delete bodyRaw.revenue;
    }

    const body = onboardingSchema.parse(bodyRaw);

    const company = await prisma.company.create({
      data: body,
    });

    return NextResponse.json({ success: true, company });
  } catch (err: any) {
    console.error("Onboarding error:", err);
    return NextResponse.json(
      { error: err?.message ?? "Internal Server Error" },
      { status: 400 }
    );
  }
}

