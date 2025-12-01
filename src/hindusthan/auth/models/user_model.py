from beanie import Document, before_event, Replace, Save
from datetime import datetime, timezone
from pydantic import Field,EmailStr
import uuid
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"
    FIELD_AGENT = "field_agent"
    MARKETER = "marketer"

class AccountStatus(str,Enum):
    ACTIVE="active",
    SUSPEND="suspend",
    PENDING="pending"



class UserModel(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    email: EmailStr
    password: Optional[str]=None
    google_id: Optional[str]=None
    image_url: Optional[str]=None
    is_verified: bool = False
    role: UserRole = UserRole.CUSTOMER
    account_status:AccountStatus=AccountStatus.ACTIVE
    phone_number: Optional[str]=None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Auto-update "updated_at" on update
    @before_event([Save, Replace])
    def update_timestamp(self):
        self.updated_at = datetime.now(timezone.utc)

    class Settings:
        name = "users"




class OTPModel(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    email: EmailStr
    otp_code: str = ""
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Auto-update "updated_at" on update
    @before_event([Save, Replace])
    def update_timestamp(self):
        self.updated_at = datetime.now(timezone.utc)

    class Settings:
        name = "otps"
