from sqlalchemy import create_engine, MetaData

import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/mff_app"
)

engine = create_engine(DATABASE_URL)
metadata = MetaData()