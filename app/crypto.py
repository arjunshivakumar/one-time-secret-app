from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()
fernet = Fernet(os.getenv("ENCRYPTION_KEY").encode())

def encrypt_secret(secret: str) -> str:
    return fernet.encrypt(secret.encode()).decode()

def decrypt_secret(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
