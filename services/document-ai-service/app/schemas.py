"""Document AI Service - Pydantic Schemas"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum

# Enums
class DocumentStatusEnum(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"

class DocumentTypeEnum(str, Enum):
    PASSPORT = "passport"
    DRIVERS_LICENSE = "drivers_license"
    NATIONAL_ID = "national_id"
    BANK_STATEMENT = "bank_statement"
    PAYSLIP = "payslip"
    TAX_RETURN = "tax_return"
    EMPLOYMENT_LETTER = "employment_letter"
    UTILITY_BILL = "utility_bill"
    PROOF_OF_ADDRESS = "proof_of_address"
    OTHER = "other"

class ExtractionStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    MANUAL_REVIEW = "manual_review"

class ExtractionMethodEnum(str, Enum):
    OCR = "ocr"
    ML = "ml"
    MANUAL = "manual"

# Document Schemas
class DocumentResponse(BaseModel):
    id: str
    customer_id: str
    document_type: DocumentTypeEnum
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    status: DocumentStatusEnum
    original_file_name: Optional[str]
    upload_source: Optional[str]
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DocumentDetailResponse(DocumentResponse):
    verified_by: Optional[str]
    verified_at: Optional[datetime]
    verification_notes: Optional[str]
    has_been_extracted: bool
    extraction_confidence: Optional[float]
    expiry_date: Optional[datetime]
    is_expired: bool

# Document Extraction Schemas
class ExtractedFieldResponse(BaseModel):
    id: str
    extraction_id: str
    field_name: str
    field_value: Optional[str]
    confidence_score: float
    field_type: str
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class DocumentExtractionResponse(BaseModel):
    id: str
    document_id: str
    status: ExtractionStatusEnum
    extraction_method: ExtractionMethodEnum
    overall_confidence: Optional[float]
    processing_time_seconds: Optional[int]
    extraction_completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class DocumentExtractionDetailResponse(DocumentExtractionResponse):
    raw_text: Optional[str]
    extraction_notes: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

# Document Validation Schemas
class DocumentValidationResponse(BaseModel):
    id: str
    document_id: str
    validation_type: str
    is_valid: bool
    validation_score: Optional[float]
    validation_notes: Optional[str]
    issues: Optional[Dict]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Document Template Schemas
class DocumentTemplateResponse(BaseModel):
    id: str
    document_type: DocumentTypeEnum
    name: str
    description: Optional[str]
    expected_fields: List[str]
    extraction_rules: Optional[Dict]
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Request Schemas
class DocumentUploadRequest(BaseModel):
    customer_id: str
    document_type: DocumentTypeEnum
    uploaded_by: Optional[str] = None

class DocumentExtractionRequest(BaseModel):
    document_id: str
    extraction_method: ExtractionMethodEnum = ExtractionMethodEnum.ML
    manual_override: Optional[bool] = False

class DocumentValidationRequest(BaseModel):
    document_id: str
    extraction_id: str
    validation_rules: Optional[Dict] = None

class DocumentTemplateCreateRequest(BaseModel):
    document_type: DocumentTypeEnum
    template_name: str
    description: Optional[str] = None
    required_fields: List[str]
    optional_fields: Optional[List[str]] = None
    extraction_rules: Optional[Dict] = None
    validation_rules: Optional[Dict] = None

# Summary & Analytics
class DocumentProcessingStatisticsResponse(BaseModel):
    total_documents: int
    documents_processed: int
    documents_pending: int
    documents_failed: int
    average_processing_time_ms: float
    success_rate: float
    extraction_success_rate: float
    validation_success_rate: float
    period_start: datetime
    period_end: datetime

class CustomerDocumentSummaryResponse(BaseModel):
    customer_id: str
    total_documents: int
    verified_documents: int
    pending_documents: int
    failed_documents: int
    last_document_upload: Optional[datetime]
    kyc_completion_status: str
    kyc_completion_percentage: float
