from fastapi import FastAPI
from .db import engine
import sqlalchemy

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/grants-test")
def test_grants():
    with engine.connect() as conn:
        # Run simple query test
        result = conn.execute(sqlalchemy.text("SELECT 1+1 AS calc"))
    return {"db_result": [dict(row._mapping) for row in result]}