"""Customer Service Database Models - Customers and Profiles"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, Enum, UniqueConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

Base = declarative_base()


class KYCStatus(str, enum.Enum):
    """KYC (Know Your Customer) Status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class CustomerStatus(str, enum.Enum):
    """Customer Status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class Customer(Base):
    """Customer model"""
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, unique=True, index=True)  # Reference to auth service user
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    
    # Address
    street_address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Identification
    ssn = Column(String(20), nullable=True)  # Last 4 digits only in production
    national_id = Column(String(50), nullable=True)
    
    # Status & KYC
    status = Column(Enum(CustomerStatus), default=CustomerStatus.ACTIVE)
    kyc_status = Column(Enum(KYCStatus), default=KYCStatus.NOT_STARTED)
    kyc_verified_at = Column(DateTime, nullable=True)
    kyc_rejection_reason = Column(String(255), nullable=True)
    
    # Risk & Score
    risk_score = Column(Float, default=0.0)  # 0-100
    credit_score = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profiles = relationship("CustomerProfile", back_populates="customer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Customer(id={self.id}, email={self.email})>"


class CustomerProfile(Base):
    """Detailed customer profile information"""
    __tablename__ = "customer_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey('customers.id'), nullable=False, index=True)
    
    # Employment
    employer_name = Column(String(255), nullable=True)
    employment_status = Column(String(50), nullable=True)  # employed, self-employed, unemployed
    job_title = Column(String(100), nullable=True)
    years_employed = Column(Integer, nullable=True)
    annual_income = Column(Float, nullable=True)
    
    # Financial
    net_worth = Column(Float, nullable=True)
    total_assets = Column(Float, nullable=True)
    total_liabilities = Column(Float, nullable=True)
    
    # Additional Info
    marital_status = Column(String(50), nullable=True)
    number_of_dependents = Column(Integer, default=0)
    education_level = Column(String(100), nullable=True)
    
    # Compliance
    pep_status = Column(Boolean, default=False)  # Politically Exposed Person
    sanctions_check = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="profiles")

    def __repr__(self):
        return f"<CustomerProfile(customer_id={self.customer_id})>"


class CustomerDocument(Base):
    """Customer uploaded documents for KYC"""
    __tablename__ = "customer_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey('customers.id'), nullable=False, index=True)
    
    document_type = Column(String(100), nullable=False)  # passport, drivers_license, etc.
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    verification_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CustomerDocument(customer_id={self.customer_id}, doc_type={self.document_type})>"


class AuditLog(Base):
    """Audit log for customer service actions"""
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=False)
    changes = Column(String(1000), nullable=True)
    status = Column(String(20), nullable=False)  # success, failed
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog(customer_id={self.customer_id}, action={self.action})>"
