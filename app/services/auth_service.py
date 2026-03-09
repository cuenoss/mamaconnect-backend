from sqlmodel import Session, select
from app.models import User
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
import dotenv
import os

dotenv.load_dotenv(dotenv_path='.env')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

def hash_password(password: str):
    safe_password = password.encode("utf-8")[:72].decode("utf-8", "ignore")
    return pwd_context.hash(safe_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def sign_up(db: AsyncSession, name: str, email: str, password: str, role: str):

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user:
        raise ValueError("Email already registered")

    hashed_password = hash_password(password)

    is_verified = True if role == "pregnant_woman" else False

    new_user = User(
        name=name,
        email=email,
        password_hash=hashed_password,
        role=role,
        is_verified=is_verified
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    print("PASSWORD RECEIVED:", password)
    print("PASSWORD LENGTH:", len(password))
    return new_user

async def login(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise ValueError("Invalid email or password")
    if not user.is_verified:
        raise ValueError("Account not verified")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}
