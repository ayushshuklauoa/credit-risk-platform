"""Customer Service - Pydantic Schemas"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from enum import Enum

# KYC & Status Enums
class KYCStatusEnum(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUSPENDED = "suspended"

class CustomerStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CLOSED = "closed"

# Customer Schemas
class CustomerCreateRequest(BaseModel):
    user_id: str
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    email: EmailStr
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None

class CustomerUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

class CustomerResponse(BaseModel):
    id: str
    user_id: str
    first_name: str
    last_name: str
    email: str
    status: CustomerStatusEnum
    kyc_status: KYCStatusEnum
    risk_score: float
    credit_score: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class CustomerDetailResponse(CustomerResponse):
    phone: Optional[str]
    street_address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]
    ssn: Optional[str]
    national_id: Optional[str]
    kyc_verified_at: Optional[datetime]
    kyc_rejection_reason: Optional[str]
    updated_at: datetime

# Customer Profile
class CustomerProfileResponse(BaseModel):
    id: str
    customer_id: str
    employer_name: Optional[str]
    employment_status: Optional[str]
    job_title: Optional[str]
    annual_income: Optional[float]
    net_worth: Optional[float]
    marital_status: Optional[str]
    number_of_dependents: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class CustomerProfileUpdateRequest(BaseModel):
    employer_name: Optional[str] = None
    employment_status: Optional[str] = None
    job_title: Optional[str] = None
    years_employed: Optional[int] = None
    annual_income: Optional[float] = None
    net_worth: Optional[float] = None
    marital_status: Optional[str] = None
    number_of_dependents: Optional[int] = None

# KYC
class KYCVerificationRequest(BaseModel):
    kyc_status: KYCStatusEnum
    rejection_reason: Optional[str] = None

# Documents
class CustomerDocumentResponse(BaseModel):
    id: str
    customer_id: str
    document_type: str
    file_name: str
    file_size: int
    is_verified: bool
    verified_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Risk & Scoring
class CustomerRiskResponse(BaseModel):
    customer_id: str
    risk_score: float
    credit_score: Optional[int]
    kyc_status: KYCStatusEnum
    status: CustomerStatusEnum
