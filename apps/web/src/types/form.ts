// types/form.ts

export type FieldType = "text" | "date" | "textarea"

// 1. Define the full form shape
export type OnboardingFormData = {
  companyName: string
  companyId: string
  companyType: string
  incorporationDate: string
  shareholding: string
  industry: string
  yearsOperating: string
  annual_revenue: string 
  employees: string
  exports: boolean
  address: string
  contact: string
  taxCompliance: string

}

// 2. Extract the keys (e.g. "companyName" | "companyId" | ...)
export type OnboardingFieldName = keyof OnboardingFormData

// 3. Use that type for the field config
export interface OnboardingField {
  name: OnboardingFieldName
  label: string
  type?: FieldType
}




