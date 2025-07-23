from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
import uuid
from uuid import UUID
from app.crypto import encrypt_secret, decrypt_secret
from app.db import SessionLocal, get_db
from sqlalchemy.orm import Session
from app import models
from datetime import datetime, timedelta, UTC
from typing import Optional
import bcrypt

router = APIRouter()
class SecretRequest(BaseModel):
    secret: str
    expire_after_minutes: Optional[int] = Field(
        default=None,
        ge=0,
        description="0 means expire immediately; None means never expire"
    )
    password: str | None = None


@router.post("/secret")
def create_secret(req: SecretRequest, db: Session = Depends(get_db)):
    secret_id = str(uuid.uuid4())
    print(req.password)
    encrypted_secret = encrypt_secret(req.secret)
    password_hash = None
    if req.password:
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(req.password.encode('utf-8'), salt).decode('utf-8')
    # Save to DB
    db_secret = models.Secret(
        id=secret_id,
        encrypted_secret=encrypted_secret,
        password_hash=password_hash,  
        expire_after_minutes=req.expire_after_minutes
    )
    db.add(db_secret)
    db.commit()
    return {"url": f"http://localhost:8000/secret/{secret_id}"}


class SecretAccessRequest(BaseModel):
    secret_id: str
    password: str

@router.post("/secret/access")
def access_secret(
    req: SecretAccessRequest,
    db: Session = Depends(get_db)
):
    secret = db.query(models.Secret).filter(models.Secret.id == req.secret_id).first()
    if not secret:
        raise HTTPException(status_code=404, detail="Secret not found")

    now = datetime.now(UTC)
    created_at = secret.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=UTC)

    if secret.expire_after_minutes is not None:
        if secret.expire_after_minutes == 0 or now - created_at > timedelta(minutes=secret.expire_after_minutes):
            db.delete(secret)
            db.commit()
            raise HTTPException(status_code=410, detail="Secret has expired")

    # Password verification
    if secret.password_hash:
        if not bcrypt.checkpw(req.password.encode('utf-8'), secret.password_hash.encode('utf-8')):
            raise HTTPException(status_code=403, detail="Incorrect password")

    try:
        plain_text = decrypt_secret(secret.encrypted_secret)
        db.delete(secret)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to decrypt secret: {str(e)}")

    return {
        "secret": plain_text
    }