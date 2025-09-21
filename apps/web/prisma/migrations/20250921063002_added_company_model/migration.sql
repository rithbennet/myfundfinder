/*
  Warnings:

  - You are about to drop the `CompanyProfile` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `Grant` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `User` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropForeignKey
ALTER TABLE "public"."CompanyProfile" DROP CONSTRAINT "CompanyProfile_userId_fkey";

-- DropTable
DROP TABLE "public"."CompanyProfile";

-- DropTable
DROP TABLE "public"."Grant";

-- DropTable
DROP TABLE "public"."User";

-- CreateTable
CREATE TABLE "public"."chat_sessions" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "messages" JSONB[],
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "chat_sessions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."users" (
    "id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "name" TEXT,
    "onboarded" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."agency" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "contact" TEXT NOT NULL,
    "description" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "agency_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."Company" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "companyName" TEXT NOT NULL,
    "companyId" TEXT NOT NULL,
    "companyType" TEXT NOT NULL,
    "incorporationDate" TEXT NOT NULL,
    "shareholding" TEXT NOT NULL,
    "industry" TEXT NOT NULL,
    "yearsOperating" TEXT NOT NULL,
    "annual_revenue" TEXT NOT NULL,
    "employees" TEXT NOT NULL,
    "exports" BOOLEAN NOT NULL,
    "address" TEXT NOT NULL,
    "contact" TEXT NOT NULL,
    "taxCompliance" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Company_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."funding" (
    "id" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "description" TEXT,
    "url" TEXT NOT NULL,
    "sector" TEXT,
    "deadline" TIMESTAMP(3),
    "amount" TEXT,
    "eligibility" TEXT,
    "embedding" TEXT,
    "requiredDocs" TEXT[],
    "agencyId" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "funding_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "chat_sessions_userId_idx" ON "public"."chat_sessions"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "public"."users"("email");

-- CreateIndex
CREATE UNIQUE INDEX "Company_userId_key" ON "public"."Company"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "Company_companyId_key" ON "public"."Company"("companyId");

-- CreateIndex
CREATE INDEX "funding_deadline_idx" ON "public"."funding"("deadline");

-- CreateIndex
CREATE INDEX "funding_agencyId_idx" ON "public"."funding"("agencyId");

-- CreateIndex
CREATE INDEX "funding_sector_idx" ON "public"."funding"("sector");

-- AddForeignKey
ALTER TABLE "public"."chat_sessions" ADD CONSTRAINT "chat_sessions_userId_fkey" FOREIGN KEY ("userId") REFERENCES "public"."users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."Company" ADD CONSTRAINT "Company_userId_fkey" FOREIGN KEY ("userId") REFERENCES "public"."users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."funding" ADD CONSTRAINT "funding_agencyId_fkey" FOREIGN KEY ("agencyId") REFERENCES "public"."agency"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
