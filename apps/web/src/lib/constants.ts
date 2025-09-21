// constants/form.ts
import type { OnboardingField } from "~/types/form";


export const ONBOARDING_FIELDS: OnboardingField[] = [
  { name: "companyName", label: "Company Name" },
  { name: "companyId", label: "Company ID (SSM No.)" },
  { name: "companyType", label: "Company Type" },
  { name: "incorporationDate", label: "Incorporation Date", type: "date" },
  { name: "shareholding", label: "Shareholding Structure" },
  { name: "industry", label: "Industry & Business Activity" },
  { name: "yearsOperating", label: "Years Operating" },
  { name: "revenue", label: "Annual Revenue" },
  { name: "employees", label: "Employees" },
  { name: "exports", label: "Export Status" },
  { name: "address", label: "Business Address", type: "textarea" },
  { name: "taxCompliance", label: "Tax Compliance" },
]
