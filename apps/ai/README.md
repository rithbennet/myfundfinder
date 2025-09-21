# MyFundFinder AI API

Production-ready FastAPI backend for a Retrieval-Augmented Generation (RAG) system that helps SMEs in Malaysia discover relevant grants.

## 🏗️ Architecture

```
app/
├── main.py              # FastAPI app + Mangum handler
├── db.py               # SQLAlchemy session management
├── models/             # Database models
├── schemas/            # Pydantic DTOs
├── routers/            # API endpoints
├── services/           # Business logic (RAG, embeddings, chat)
└── utils/              # Utilities

seeds/                  # Database seeding & document processing
tests/                  # Essential tests
data/                   # Grant documents
```

## 🚀 Key Features

- **RAG Chat System**: Vector search + LLM for grant recommendations
- **Guardrails**: Focused on funding advice only
- **Document Processing**: PDF upload, text extraction, chunking, embeddings
- **Multi-tenant**: User-company access control
- **AWS Integration**: Bedrock (Llama 3 70B), S3, Aurora PostgreSQL with pgvector

## 🛠️ Setup

1. **Environment Variables**:
```bash
DATABASE_URL=postgresql://user:pass@aurora-endpoint:5432/mff
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
S3_BUCKET_NAME=myfundfinder-documents
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Database Setup**:
```bash
alembic upgrade head
python seeds/seed_database.py
```

4. **Process Documents**:
```bash
python seeds/process_single.py "Grant Program Name"
```

5. **Run Server**:
```bash
python run_dev.py
```

## 📡 API Endpoints

### Chat
- `POST /chat/` - Main RAG endpoint for grant recommendations
- `GET /chat/sessions` - Get user's chat history

### Companies
- `GET /companies/` - Get user's accessible companies

## 🧪 Testing

```bash
# Test guardrails
python tests/test_guardrails.py

# Test embeddings
python tests/test_embedding.py
```

## 🚀 Deployment

```bash
./deploy.sh
```

## 🛡️ Security Features

- Content guardrails (funding topics only)
- Company-level access control
- SQL injection protection
- File validation for uploads

## 💰 Cost Optimization

- Aurora Serverless V2 (0.5-16 ACUs)
- Efficient vector search with pgvector
- Optimized LLM usage with Llama 3 70B
