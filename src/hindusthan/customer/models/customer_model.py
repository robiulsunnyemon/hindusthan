from beanie import Document, before_event, Replace, Save
from datetime import datetime, timezone
from pydantic import Field
import uuid


class CustomerModel(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    first_name: str = ""
    middle_name: str = ""
    last_name: str = ""
    nick_name: str = ""
    phone_number: str = ""
    email: str = ""
    district: str = ""
    mandal: str = ""
    village: str = ""
    register_by: str = ""
    user_id: str = ""
    kyc_number: str = ""
    kyc_url: str = ""
    street: str = ""
    city: str = ""
    state: str = ""
    postal_code: str = ""
    country: str = ""
    service: str = ""
    sub_service: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Auto-update "updated_at" on update
    @before_event([Save, Replace])
    def update_timestamp(self):
        self.updated_at = datetime.now(timezone.utc)

    class Settings:
        name = "customers"
