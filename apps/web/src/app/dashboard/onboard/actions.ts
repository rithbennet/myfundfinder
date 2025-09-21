'use server'

import { prisma } from '~/lib/prisma'
import { revalidatePath } from 'next/cache'

export async function createCompany(userId: string, formData: FormData) {
  try {
    const company = await prisma.company.create({
      data: {
        userId: userId,
        companyName: formData.get('companyName') as string,
        companyId: formData.get('companyId') as string,
        companyType: formData.get('companyType') as string,
        incorporationDate: formData.get('incorporationDate') as string,
        shareholding: formData.get('shareholding') as string,
        industry: formData.get('industry') as string,
        yearsOperating: formData.get('yearsOperating') as string,
        annual_revenue: formData.get('annual_revenue') as string,
        employees: formData.get('employees') as string,
        exports: formData.get('exports') === 'true',
        address: formData.get('address') as string,
        contact: formData.get('contact') as string,
        taxCompliance: formData.get('taxCompliance') as string,
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