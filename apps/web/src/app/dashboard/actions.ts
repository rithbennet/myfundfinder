'use server'

import { prisma } from "~/lib/prisma"

export async function getUserCompanies(userId: string) {
  try {
    const companies = await prisma.user_companies.findMany({
      where: {
        user_id: userId
      },
      include: {
        companies: true
      }
    })
    return { success: true, data: companies }
  } catch (error) {
    console.error('Error fetching companies:', error)
    return { success: false, error: 'Failed to fetch companies' }
  }
}