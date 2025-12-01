from passlib.context import CryptContext
from datetime import datetime,timedelta,timezone
from typing import Optional
from jose import jwt

SECRET_KEY = "Hindusthan-prasad-restapi"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
GOOGLE_CLIENT_ID = "644874684247-f1e2uj3dbmjaoqaakt2fprnjcsgcar59.apps.googleusercontent.com"

pwd_context = CryptContext( schemes=["argon2"],deprecated="auto")


def hash_password(password: str) -> str:

    if not password:
        return ""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt