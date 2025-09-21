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
CREATE TABLE "public"."users" (
    "id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "name" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."company_profiles" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "sector" TEXT NOT NULL,
    "size" TEXT NOT NULL,
    "region" TEXT,
    "keywords" TEXT,

    CONSTRAINT "company_profiles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."grants" (
    "id" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "description" TEXT,
    "url" TEXT NOT NULL,
    "sector" TEXT,
    "deadline" TIMESTAMP(3),
    "amount" TEXT,
    "eligibility" TEXT,
    "provider" TEXT,
    "embedding" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "grants_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."chat_sessions" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "messages" JSONB[],
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "chat_sessions_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "public"."users"("email");

-- CreateIndex
CREATE UNIQUE INDEX "company_profiles_userId_key" ON "public"."company_profiles"("userId");

-- CreateIndex
CREATE INDEX "grants_sector_idx" ON "public"."grants"("sector");

-- CreateIndex
CREATE INDEX "grants_deadline_idx" ON "public"."grants"("deadline");

-- CreateIndex
CREATE INDEX "grants_provider_idx" ON "public"."grants"("provider");

-- CreateIndex
CREATE INDEX "chat_sessions_userId_idx" ON "public"."chat_sessions"("userId");

-- AddForeignKey
ALTER TABLE "public"."company_profiles" ADD CONSTRAINT "company_profiles_userId_fkey" FOREIGN KEY ("userId") REFERENCES "public"."users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."chat_sessions" ADD CONSTRAINT "chat_sessions_userId_fkey" FOREIGN KEY ("userId") REFERENCES "public"."users"("id") ON DELETE CASCADE ON UPDATE CASCADE;
