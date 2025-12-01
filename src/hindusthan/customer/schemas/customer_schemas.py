from pydantic import BaseModel,EmailStr
from typing import Optional
from datetime import datetime

# Schema for creating new Customer
class CustomerCreate(BaseModel):
    first_name: str
    middle_name: str
    last_name: str
    nick_name: str
    phone_number: str
    email: EmailStr
    district: str
    mandal: str
    village: str
    register_by: str
    user_id: str
    kyc_number: str
    kyc_url: str
    street: str
    city: str
    state: str
    postal_code: str
    country: str
    service: str
    sub_service: str

# Schema for updating Customer
class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    nick_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    district: Optional[str] = None
    mandal: Optional[str] = None
    village: Optional[str] = None
    register_by: Optional[str] = None
    user_id: Optional[str] = None
    kyc_number: Optional[str] = None
    kyc_url: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    service: Optional[str] = None
    sub_service: Optional[str] = None

# Schema for Customer response
class CustomerResponse(BaseModel):
    id: str
    first_name: str
    middle_name: str
    last_name: str
    nick_name: str
    phone_number: str
    email: EmailStr
    district: str
    mandal: str
    village: str
    register_by: str
    user_id: str
    kyc_number: str
    kyc_url: str
    street: str
    city: str
    state: str
    postal_code: str
    country: str
    service: str
    sub_service: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
