"""Document AI Service Database Models - Document Management and Extraction"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, Enum, JSON, UniqueConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

Base = declarative_base()


class DocumentType(str, enum.Enum):
    """Document Type"""
    PASSPORT = "passport"
    DRIVERS_LICENSE = "drivers_license"
    NATIONAL_ID = "national_id"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    TAX_RETURN = "tax_return"
    EMPLOYMENT_LETTER = "employment_letter"
    INCOME_VERIFICATION = "income_verification"
    BUSINESS_LICENSE = "business_license"
    OTHER = "other"


class DocumentStatus(str, enum.Enum):
    """Document Status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ExtractionStatus(str, enum.Enum):
    """Extraction Status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    """Document model"""
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), nullable=False, index=True)
    
    # Document Details
    document_type = Column(Enum(DocumentType), nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED)
    
    # File Information
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    
    # Metadata
    original_file_name = Column(String(255), nullable=True)
    upload_source = Column(String(50), nullable=True)  # e.g., "web", "mobile", "api"
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verified_by = Column(String(36), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    verification_notes = Column(Text, nullable=True)
    
    # Extraction
    has_been_extracted = Column(Boolean, default=False)
    extraction_confidence = Column(Float, nullable=True)  # 0-100
    
    # Expiration
    expiry_date = Column(DateTime, nullable=True)
    is_expired = Column(Boolean, default=False)
    
    # Dates
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    extractions = relationship("DocumentExtraction", back_populates="document", cascade="all, delete-orphan")
    validations = relationship("DocumentValidation", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(customer_id={self.customer_id}, type={self.document_type})>"


class DocumentExtraction(Base):
    """Document extraction result model"""
    __tablename__ = "document_extractions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey('documents.id'), nullable=False, index=True)
    
    # Extraction Details
    status = Column(Enum(ExtractionStatus), default=ExtractionStatus.PENDING)
    extraction_method = Column(String(50), nullable=False)  # e.g., "ocr", "ml", "manual"
    
    # Extracted Data
    extracted_data = Column(JSON, nullable=True)
    raw_text = Column(Text, nullable=True)
    
    # Confidence & Quality
    overall_confidence = Column(Float, nullable=True)  # 0-100
    quality_score = Column(Float, nullable=True)  # 0-100
    
    # Processing
    extraction_started_at = Column(DateTime, nullable=True)
    extraction_completed_at = Column(DateTime, nullable=True)
    processing_time_seconds = Column(Integer, nullable=True)
    
    # Results
    extraction_notes = Column(Text, nullable=True)
    error_message = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="extractions")
    fields = relationship("ExtractedField", back_populates="extraction", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DocumentExtraction(document_id={self.document_id}, status={self.status})>"


class ExtractedField(Base):
    """Extracted field model"""
    __tablename__ = "extracted_fields"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    extraction_id = Column(String(36), ForeignKey('document_extractions.id'), nullable=False, index=True)
    
    # Field Information
    field_name = Column(String(100), nullable=False)
    field_type = Column(String(50), nullable=False)  # e.g., "text", "date", "number"
    field_value = Column(String(500), nullable=True)
    
    # Quality
    confidence_score = Column(Float, nullable=True)  # 0-100
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    extraction = relationship("DocumentExtraction", back_populates="fields")

    def __repr__(self):
        return f"<ExtractedField(field_name={self.field_name}, value={self.field_value})>"


class DocumentValidation(Base):
    """Document validation result model"""
    __tablename__ = "document_validations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey('documents.id'), nullable=False, index=True)
    
    # Validation Details
    validation_type = Column(String(50), nullable=False)  # e.g., "authenticity", "format", "content"
    is_valid = Column(Boolean, default=False)
    
    # Validation Results
    validation_score = Column(Float, nullable=True)  # 0-100
    validation_notes = Column(Text, nullable=True)
    
    # Issues Found
    issues = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="validations")

    def __repr__(self):
        return f"<DocumentValidation(document_id={self.document_id}, valid={self.is_valid})>"


class DocumentTemplate(Base):
    """Document template model for standardized extraction"""
    __tablename__ = "document_templates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_type = Column(Enum(DocumentType), nullable=False, unique=True)
    
    # Template Details
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    
    # Expected Fields
    expected_fields = Column(JSON, nullable=False)
    extraction_rules = Column(JSON, nullable=True)
    
    # Configuration
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<DocumentTemplate(type={self.document_type})>"


class DocumentProcessingLog(Base):
    """Document processing log for tracking"""
    __tablename__ = "document_processing_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey('documents.id'), nullable=False, index=True)
    
    # Processing Details
    process_step = Column(String(100), nullable=False)  # e.g., "upload", "scan", "extract", "validate"
    status = Column(String(50), nullable=False)  # success, failed
    
    # Metadata
    duration_seconds = Column(Float, nullable=True)
    details = Column(JSON, nullable=True)
    error_message = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<DocumentProcessingLog(document_id={self.document_id}, step={self.process_step})>"


class AuditLog(Base):
    """Audit log for document service actions"""
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), nullable=True, index=True)
    document_id = Column(String(36), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=False)
    changes = Column(String(1000), nullable=True)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog(customer_id={self.customer_id}, document_id={self.document_id})>"
