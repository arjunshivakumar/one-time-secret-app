import time
import os
import psycopg2
from psycopg2 import OperationalError
from fastapi import FastAPI
from .routes import router

from .db import engine, Base

def wait_for_postgres(host: str, user: str, password: str, db: str):
    while True:
        try:
            conn = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                dbname=db
            )
            conn.close()
            print("✅ PostgreSQL is available.")
            break
        except OperationalError:
            print("⏳ Waiting for PostgreSQL...")
            time.sleep(1)

# Wait for the DB
wait_for_postgres(
    host='db',
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    db=os.environ["POSTGRES_DB"]
)

# Init SQLAlchemy models
Base.metadata.create_all(bind=engine)

# ✅ Create the FastAPI app instance
app = FastAPI()
app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "API is running!"}
