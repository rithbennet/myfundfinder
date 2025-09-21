from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from .routers import chat, companies, funding, auth

app = FastAPI(title="MyFundFinder AI API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(companies.router)
app.include_router(funding.router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "MyFundFinder AI API"}

# Lambda handler for AWS deployment
handler = Mangum(app)