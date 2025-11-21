"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Core domain models for Loan Utilization Tracker

class Beneficiary(BaseModel):
    phone: str = Field(..., description="Beneficiary mobile number (unique identifier)")
    name: str = Field(..., description="Beneficiary full name")
    state: Optional[str] = Field(None, description="State/UT")
    district: Optional[str] = Field(None, description="District")
    address: Optional[str] = Field(None, description="Full address")
    scheme: Optional[str] = Field(None, description="Scheme name under which loan is taken")
    bank: Optional[str] = Field(None, description="Bank/Financier name")
    loan_id: Optional[str] = Field(None, description="Loan account/reference ID")
    loan_amount: Optional[float] = Field(None, description="Sanctioned loan amount")

class Officer(BaseModel):
    phone: str = Field(..., description="Officer mobile number")
    name: str = Field(..., description="Officer name")
    role: str = Field("officer", description="Role: officer/reviewer/admin")
    organization: Optional[str] = Field(None, description="State Agency/Bank name")

class MediaUpload(BaseModel):
    beneficiary_phone: str = Field(..., description="Beneficiary mobile number")
    loan_id: Optional[str] = Field(None, description="Loan account/reference ID")
    file_name: str = Field(..., description="Original file name")
    mime_type: str = Field(..., description="MIME type of uploaded file")
    data_base64: str = Field(..., description="Base64-encoded image/video data")
    latitude: Optional[float] = Field(None, description="Captured latitude")
    longitude: Optional[float] = Field(None, description="Captured longitude")
    accuracy: Optional[float] = Field(None, description="GPS accuracy meters")
    captured_at: Optional[datetime] = Field(None, description="Device-captured timestamp in ISO format")
    notes: Optional[str] = Field(None, description="Notes/description of the asset")

class Review(BaseModel):
    upload_id: str = Field(..., description="Associated upload ID")
    reviewer_phone: str = Field(..., description="Reviewer mobile number")
    approved: bool = Field(..., description="Approval decision")
    comment: Optional[str] = Field(None, description="Reviewer comment")

class OTPRequest(BaseModel):
    phone: str

class OTPVerify(BaseModel):
    phone: str
    code: str

class SyncPayload(BaseModel):
    items: List[MediaUpload]

# Example schemas retained for reference (not used by app runtime)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
