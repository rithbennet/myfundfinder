from sqlalchemy import create_engine, MetaData
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the apps/ai directory (or parent dirs)
env_path = Path(__file__).resolve().parents[1] / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    # fallback to default load (will look for .env in CWD)
    load_dotenv()

# Database configuration - ready for AWS Aurora migration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # For AWS Aurora, you'll use a connection string like:
    # postgresql://username:password@aurora-cluster-endpoint.region.rds.amazonaws.com:5432/database_name
    raise RuntimeError("Please add DATABASE_URL to your .env file for AWS Aurora connection")

# Engine configuration optimized for AWS Aurora
engine_config = {
    "echo": os.getenv("DATABASE_ECHO", "false").lower() == "true",
    "pool_size": int(os.getenv("DATABASE_POOL_SIZE", "5")),
    "max_overflow": int(os.getenv("DATABASE_MAX_OVERFLOW", "10")),
    "pool_timeout": int(os.getenv("DATABASE_POOL_TIMEOUT", "30")),
    "pool_recycle": int(os.getenv("DATABASE_POOL_RECYCLE", "3600")),  # 1 hour
}

engine = create_engine(DATABASE_URL, **engine_config)
metadata = MetaData()
