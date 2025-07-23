# app/main.py
import os
import time
import psycopg2
from psycopg2 import OperationalError
from fastapi import FastAPI
from .db import engine, Base

# -------------------------------------------------
# ❶  Detect test mode
IS_TEST = os.getenv("TESTING") == "1"
# -------------------------------------------------

def wait_for_postgres(host: str, user: str, password: str, db: str):
    while True:
        try:
            conn = psycopg2.connect(host=host, user=user, password=password, dbname=db)
            conn.close()
            print("✅ PostgreSQL is available.")
            break
        except OperationalError:
            print("⏳ Waiting for PostgreSQL...")
            time.sleep(1)

# -------------------------------------------------
# ❷  Only run these lines when NOT testing
if not IS_TEST:
    wait_for_postgres(
        host="db",
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        db=os.environ["POSTGRES_DB"],
    )
    Base.metadata.create_all(bind=engine)
# -------------------------------------------------

def create_app() -> FastAPI:
    from .routes import router
    app = FastAPI()
    app.include_router(router)
    return app

app = create_app()

@app.get("/")
def read_root():
    return {"message": "API is running!"}
