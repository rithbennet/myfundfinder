/* eslint-disable @typescript-eslint/no-unsafe-member-access */
/* eslint-disable @typescript-eslint/no-unsafe-assignment */
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { ONBOARDING_FIELDS } from "~/lib/constants";
import type { OnboardingFormData } from "~/types/form";

export default function OnboardingForm() {
  const [file, setFile] = useState<File | null>(null);
  const initialFormData = Object.fromEntries(
    ONBOARDING_FIELDS.map((f) => [f.name, ""])
  ) as unknown as OnboardingFormData;
  const [formData, setFormData] = useState<OnboardingFormData>(initialFormData);
  const [loading, setLoading] = useState(false);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);

      // 🔹 Simulate NLP auto-fill with dummy data
      setTimeout(() => {
        setFormData((prev) => ({
          ...prev,
          companyName: "Green Valley Foods Sdn. Bhd.",
          companyId: "201987654321",
          companyType: "Private Limited (Sdn. Bhd.)",
          incorporationDate: "2018-03-15",
          shareholding: "70% Malaysian, 30% Foreign",
          industry: "Food & Beverage Manufacturing",
          yearsOperating: "6",
          revenue: "RM 12 million (FY 2023)",
          annual_revenue: "RM 12 million (FY 2023)", // optional duplication
          employees: "85",
          exports: true, // ✅ boolean
          address: "Lot 25, Industrial Park, Shah Alam, Selangor, Malaysia",
          contact: "+603-1234 5678 | info@greenvalleyfoods.com",
          taxCompliance: "In good standing (LHDN 2023)",
        }));
      }, 1500);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = e.target;

    if (name === "exports") {
      setFormData((prev) => ({
        ...prev,
        [name]: value.toLowerCase() === "yes",
      }));
    } else if (name === "directors") {
      setFormData((prev) => ({
        ...prev,
        [name]: value.split(",").map((s) => s.trim()),
      }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      alert("Please upload a business document first.");
      return;
    }

    setLoading(true);

    try {
      // Replace this with actual user ID from your auth
      const userId = "USER_ID_HERE";

      const body = { ...formData, userId };

      const res = await fetch("/api/onboarding", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await res.json();

      if (!res.ok) {
        alert(`Error: ${data.error}`);
        setLoading(false);
        return;
      }

      alert("✅ Form submitted successfully!");
      console.log("Saved company:", data.company);
    } catch (err) {
      console.error("Submission error:", err);
      alert("Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mx-auto max-w-3xl space-y-6">
      {/* Upload */}
      <div>
        <Label htmlFor="document">Upload Business Document</Label>
        <Input
          id="document"
          type="file"
          accept=".pdf,.doc,.docx"
          onChange={handleFileUpload}
        />
        {file && <p className="mt-2 text-sm">Uploaded: {file.name}</p>}
      </div>

     {ONBOARDING_FIELDS.map((field) => (
        <div key={field.name}>
          <Label>{field.label}</Label>
          {field.type === "textarea" ? (
            <Textarea
              name={field.name}
              value={
                field.name === "exports"
                  ? formData[field.name]
                    ? "Yes"
                    : "No" // convert boolean to string
                  : (formData[field.name] as string)
              }
              onChange={handleChange}
            />
          ) : (
            <Input
              type={field.type ?? "text"}
              name={field.name}
              value={
                field.name === "exports"
                  ? formData[field.name]
                    ? "Yes"
                    : "No"
                  : (formData[field.name] as string)
              }
              onChange={handleChange}
            />
          )}
        </div>
      ))}
      <Button type="submit" className="w-full" disabled={loading}>
        {loading ? "Submitting..." : "Submit"}
      </Button>
    </form>
  );
}
