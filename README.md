# 💰 MyFundFinder Monorepo

**MyFundFinder** is a **centralised SME fund finder platform** that helps small & medium enterprises discover and access funding opportunities (government, corporate, and private).

This repo is a **monorepo** that hosts the entire stack — frontend, backend, infra, and development tooling.

---

## 🌐 What We’re Using

### 🖥 Frontend

- **Next.js (React)** — core web client
- **AWS Amplify** — hosting client, auth (Cognito), and integration with AWS backend services

### ⚙️ Backend

- **FastAPI (Python)** — main API service
- Deployed as **serverless functions with AWS Lambda** + API Gateway
- Supports **AI features** (using embeddings/vector search via pgvector in Aurora)

### 🗄 Database

- **Aurora PostgreSQL (AWS)** — production DB
  - `pgvector` extension enabled (for AI/ML vector search)
- **Dockerized Postgres+pgvector** — local dev environment to mirror Aurora

### ☁️ AWS Integrations

- **S3** — file/object storage (documents, fund data, reports)
- **Amplify** — manages frontend deployment + environment configs
- **Lambda** — runs FastAPI backend code serverlessly
- **Aurora (Postgres+pgvector)** — main structured + vector DB
- **(Planned)** **BlackRock API integration** — ingest and normalise financial/fund data

### 🧩 Other

- **Turborepo + pnpm** — monorepo tooling & dependency management
- **Prisma + PgAdmin** — ORM + admin UI for database
- **Docker** — local dev DB & pgAdmin

---

## 🛠 Project Structure

```
myfundfinder/
│
├── apps/
│   ├── web/         # Next.js + Amplify frontend
│   └── ai/          # FastAPI backend (to be deployed via Lambda)
│
├── docker/
│   └── init.sql     # Local dev DB bootstrap (users, funds, pgvector docs)
│
├── docker-compose.yml   # Local Postgres + pgAdmin with pgvector
├── turbo.json           # Turborepo pipeline config
├── package.json
└── README.md
```

---

## ▶️ Local Development

### 1. Install dependencies

```bash
pnpm install
```

- Installs Node deps
- Creates `venv` in `apps/ai/` and installs FastAPI deps

### 2. Start local database (Postgres + pgAdmin)

```bash
docker compose up -d
```

- DB: `localhost:15432` → `mff_app`
- pgAdmin: [http://localhost:15433](http://localhost:15433)

### 3. Run web + backend simultaneously

```bash
pnpm dev
```

- Web frontend: [http://localhost:3000](http://localhost:3000)
- FastAPI backend: [http://localhost:8000](http://localhost:8000)

---

## 🐘 Database Strategy

- **Local dev**: Docker Postgres (with `pgvector`) mirrors Aurora schema
- **Production**: Aurora PostgreSQL (with `pgvector`)
- Reset dev DB:

```bash
docker compose down -v && docker compose up -d
```

---

## 📜 Common Commands

| Command                  | Description                         |
| ------------------------ | ----------------------------------- |
| `pnpm install`           | Install deps (JS + Python)          |
| `pnpm dev`               | Run frontend + backend in dev mode  |
| `docker compose up -d`   | Start local Postgres + pgAdmin      |
| `docker compose down`    | Stop containers (keep data)         |
| `docker compose down -v` | Stop + reset DB and pgAdmin volumes |

---

## 🚀 Deployment (Planned Pipeline)

1. **Frontend** → Deployed via AWS Amplify → served globally via CloudFront
2. **Backend (FastAPI)** → Containerized & deployed to AWS Lambda (via API Gateway)
3. **Database** → Aurora PostgreSQL with `pgvector` (scalable, ML-ready)
4. **Assets & documents** → S3 buckets (public/private access)
5. **Data ingestion** → Integrations with BlackRock + other APIs
6. **AI features** → Semantic vector search + recommendations using `pgvector`

---

## ✅ Vision

MyFundFinder is the **central place for SMEs to discover, search, and match with relevant funding**.

By combining **financial data (BlackRock & others)**, a structured DB (Aurora), and **AI-powered search/ranking** (via `pgvector`), the platform aims to **simplify fund discovery and improve access for small enterprises**.

---

📌 **Quickstart for Devs:**

1. `pnpm install`
2. `docker compose up -d`
3. `pnpm dev`  
   → You now have web (Next.js), backend (FastAPI), and DB (Postgres+pgvector) running locally, mirroring production Aurora.

---

✨ **Next Steps**

- Expand `init.sql` (schemas: users, funds, documents w/ embeddings)
- Integrate Amplify → Lambda FastAPI pipeline
- Hook S3 storage (fund docs, reports)
- Add BlackRock financial API source
- Prep Aurora migrations
