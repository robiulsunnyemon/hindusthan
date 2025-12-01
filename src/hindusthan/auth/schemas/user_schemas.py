from pydantic import BaseModel,EmailStr
from typing import Optional
from datetime import datetime
from src.hindusthan.auth.models.user_model import UserRole, AccountStatus


# Schema for creating new User
class UserCreate(BaseModel):
    email: EmailStr
    phone_number: Optional[str]=None
    role: Optional[UserRole] = UserRole.CUSTOMER
    password: str


# Schema for updating User
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    phone_number: Optional[str]=None
    google_id: Optional[str] = None
    image_url: Optional[str] = None

# Schema for User response
class UserResponse(BaseModel):
    id: str
    email: EmailStr
    password:Optional[str] = None
    google_id: Optional[str] = None
    image_url: Optional[str] = None
    phone_number: Optional[str]=None
    is_verified:bool
    account_status:AccountStatus ## new
    role:UserRole
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ResendOTP(BaseModel):
    email:EmailStr

class OTPVerify(BaseModel):
    email: EmailStr
    otp_code: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class GoogleLoginRequest(BaseModel):
    id_token: str