import os, time, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

# Load .env at import time so env vars are available even without shell exports
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "change_this_secret_key")
JWT_ALG = os.getenv("JWT_ALG", "HS256")
# default: 7 days; override with JWT_TTL_SECONDS in .env if needed
JWT_TTL_SECONDS = int(os.getenv("JWT_TTL_SECONDS", str(60*60*24*7)))

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(raw: str) -> str:
    return pwd.hash(raw)

def verify_password(raw: str, hashed: str) -> bool:
    return pwd.verify(raw, hashed)

# auth.py
def make_jwt(sub: int, email: str, exp_seconds: int = 60*60*24*7) -> str:
    payload = {
        "sub": str(sub),
        "email": email,
        "exp": int(time.time()) + exp_seconds,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def decode_jwt(token: str):
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])