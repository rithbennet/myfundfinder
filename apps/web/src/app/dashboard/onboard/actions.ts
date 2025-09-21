'use server'

import { prisma } from "~/lib/prisma"
import { revalidatePath } from 'next/cache'

export async function createCompany(userId: string, formData: FormData) {
  try {
    const company = await prisma.company.create({
      data: {
        company_name: formData.get('company_name') as string,
        company_id: formData.get('company_id') as string || null, // Make it nullable
        sector: formData.get('sector') as string || null,
        location: formData.get('location') as string || null,
        revenue: formData.get('revenue') ? parseFloat(formData.get('revenue') as string) : null,
        employees: formData.get('employees') ? parseInt(formData.get('employees') as string) : null,
        created_at: new Date(),
        updated_at: new Date(),
        user_companies: {
          create: {
            user_id: userId,
            role: 'OWNER'
          }
        }
      },
    })

    // Update user onboarded status
    await prisma.user.update({
      where: { id: userId },
      data: { onboarded: true },
    })

    revalidatePath('/onboarding')
    return { success: true, data: company }
  } catch (error) {
    console.error('Error creating company:', error)
    return { success: false, error: 'Failed to create company' }
  }
}