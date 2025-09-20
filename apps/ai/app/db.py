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

# Accept either a full DATABASE_URL or individual PG* components
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Please add DATABASE_URL to your .env file")

engine = create_engine(DATABASE_URL)
metadata = MetaData(schema="public")
