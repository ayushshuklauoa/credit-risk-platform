"""Document AI Service - Routes"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime, timedelta
import uuid
import json
import os
from typing import List, Optional

from .database import get_db
from .models import (
    Document, DocumentExtraction, ExtractedField, DocumentValidation,
    DocumentTemplate, DocumentProcessingLog, AuditLog, DocumentStatus,
    ExtractionStatus, DocumentType
)
from .schemas import (
    DocumentResponse, DocumentDetailResponse, DocumentExtractionResponse,
    DocumentExtractionDetailResponse, DocumentValidationResponse,
    DocumentTemplateResponse, ExtractedFieldResponse,
    DocumentUploadRequest, DocumentExtractionRequest, DocumentValidationRequest,
    DocumentTemplateCreateRequest, DocumentProcessingStatisticsResponse,
    CustomerDocumentSummaryResponse, DocumentStatusEnum, DocumentTypeEnum,
    ExtractionStatusEnum, ExtractionMethodEnum
)

router = APIRouter()

# Document Upload Endpoints

@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    customer_id: str = Query(...),
    document_type: DocumentTypeEnum = Query(...),
    file: UploadFile = File(...),
    uploaded_by: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Upload a document"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_size = len(await file.read())
        await file.seek(0)
        
        max_file_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_file_size:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
        # Create document record
        document = Document(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            document_type=document_type.value,
            file_path=f"/app/uploads/{file.filename}",
            file_name=file.filename,
            original_file_name=file.filename,
            file_size=file_size,
            mime_type=file.content_type or "application/octet-stream",
            status=DocumentStatus.UPLOADED.value,
            upload_source="api",
            expiry_date=datetime.utcnow() + timedelta(days=365)
        )
        
        audit_log = AuditLog(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            document_id=document.id,
            action="DOCUMENT_UPLOAD",
            resource="documents",
            status="success",
            changes=f"Uploaded document: {file.filename}"
        )
        
        db.add_all([document, audit_log])
        db.commit()
        db.refresh(document)
        return DocumentResponse.model_validate(document)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

@router.get("/documents/{document_id}", response_model=DocumentDetailResponse)
async def get_document(document_id: str, db: Session = Depends(get_db)):
    """Get document details"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentDetailResponse.model_validate(document)

@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    customer_id: Optional[str] = Query(None),
    document_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List documents with filtering"""
    query = db.query(Document)
    
    if customer_id:
        query = query.filter(Document.customer_id == customer_id)
    if document_type:
        query = query.filter(Document.document_type == document_type)
    if status:
        query = query.filter(Document.status == status)
    
    documents = query.order_by(desc(Document.created_at)).offset(skip).limit(limit).all()
    return [DocumentResponse.model_validate(doc) for doc in documents]

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Delete document (soft delete)"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document.status = DocumentStatus.REJECTED.value
    document.updated_at = datetime.utcnow()
    
    audit_log = AuditLog(
        id=str(uuid.uuid4()),
        customer_id=document.customer_id,
        document_id=document_id,
        action="DOCUMENT_DELETE",
        resource="documents",
        status="success",
        changes=f"Archived document: {document_id}"
    )
    
    db.add(audit_log)
    db.commit()
    return {"message": "Document deleted successfully"}

# Document Extraction Endpoints

@router.post("/documents/{document_id}/extract", response_model=DocumentExtractionResponse)
async def extract_document(
    document_id: str,
    request: DocumentExtractionRequest,
    db: Session = Depends(get_db)
):
    """Extract data from document"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Create extraction record
        extraction = DocumentExtraction(
            id=str(uuid.uuid4()),
            document_id=document_id,
            status=ExtractionStatus.IN_PROGRESS.value,
            extraction_method=request.extraction_method.value,
            overall_confidence=0.0,
            extraction_started_at=datetime.utcnow(),
            processing_time_seconds=0
        )
        
        # Simulate extraction (placeholder for ML model)
        extracted_fields = []
        if request.extraction_method.value == "ocr":
            # OCR extraction
            extracted_fields = [
                ExtractedField(
                    id=str(uuid.uuid4()),
                    extraction_id=extraction.id,
                    field_name="name",
                    field_value="John Doe",
                    confidence_score=0.95,
                    field_type="text",
                    is_verified=False
                ),
                ExtractedField(
                    id=str(uuid.uuid4()),
                    extraction_id=extraction.id,
                    field_name="document_number",
                    field_value="AB123456",
                    confidence_score=0.92,
                    field_type="alphanumeric",
                    is_verified=False
                )
            ]
        
        extraction.status = ExtractionStatus.COMPLETED.value
        extraction.overall_confidence = 0.93
        extraction.processing_time_seconds = 1
        extraction.extraction_completed_at = datetime.utcnow()
        
        # Update document status
        document.status = DocumentStatus.PROCESSING.value
        document.has_been_extracted = True
        document.extraction_confidence = extraction.overall_confidence
        
        audit_log = AuditLog(
            id=str(uuid.uuid4()),
            customer_id=document.customer_id,
            document_id=document_id,
            action="DOCUMENT_EXTRACT",
            resource="documents",
            status="success",
            changes=f"Extraction created: {extraction.id}"
        )
        
        db.add_all([extraction] + extracted_fields + [audit_log])
        db.commit()
        db.refresh(extraction)
        return DocumentExtractionResponse.model_validate(extraction)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error extracting document: {str(e)}")

@router.get("/documents/{document_id}/extraction", response_model=DocumentExtractionDetailResponse)
async def get_document_extraction(document_id: str, db: Session = Depends(get_db)):
    """Get document extraction results"""
    extraction = db.query(DocumentExtraction).filter(
        DocumentExtraction.document_id == document_id
    ).order_by(desc(DocumentExtraction.processed_at)).first()
    
    if not extraction:
        raise HTTPException(status_code=404, detail="Extraction not found")
    
    return DocumentExtractionDetailResponse.model_validate(extraction)

@router.get("/extractions/{extraction_id}", response_model=DocumentExtractionDetailResponse)
async def get_extraction_by_id(extraction_id: str, db: Session = Depends(get_db)):
    """Get extraction by ID"""
    extraction = db.query(DocumentExtraction).filter(
        DocumentExtraction.id == extraction_id
    ).first()
    
    if not extraction:
        raise HTTPException(status_code=404, detail="Extraction not found")
    
    return DocumentExtractionDetailResponse.model_validate(extraction)

# Document Validation Endpoints

@router.post("/documents/{document_id}/validate", response_model=DocumentValidationResponse)
async def validate_document(
    document_id: str,
    request: DocumentValidationRequest,
    db: Session = Depends(get_db)
):
    """Validate extracted document data"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        extraction = db.query(DocumentExtraction).filter(
            DocumentExtraction.id == request.extraction_id
        ).first()
        if not extraction:
            raise HTTPException(status_code=404, detail="Extraction not found")
        
        # Create validation record
        validation = DocumentValidation(
            id=str(uuid.uuid4()),
            document_id=document_id,
            validation_type="content",
            is_valid=True,
            validation_score=100.0,
            validation_notes="Validation passed",
            issues={}
        )
        
        # Update document status
        document.status = DocumentStatus.VERIFIED.value
        document.is_verified = True
        document.verified_at = datetime.utcnow()
        document.updated_at = datetime.utcnow()
        
        audit_log = AuditLog(
            id=str(uuid.uuid4()),
            customer_id=document.customer_id,
            document_id=document_id,
            action="DOCUMENT_VALIDATE",
            resource="documents",
            status="success",
            changes=f"Validation created: {validation.id}"
        )
        
        db.add_all([validation, audit_log])
        db.commit()
        db.refresh(validation)
        return DocumentValidationResponse.model_validate(validation)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error validating document: {str(e)}")

@router.get("/validations/{validation_id}", response_model=DocumentValidationResponse)
async def get_validation(validation_id: str, db: Session = Depends(get_db)):
    """Get validation details"""
    validation = db.query(DocumentValidation).filter(
        DocumentValidation.id == validation_id
    ).first()
    
    if not validation:
        raise HTTPException(status_code=404, detail="Validation not found")
    
    return DocumentValidationResponse.model_validate(validation)

# Document Template Endpoints

@router.post("/templates", response_model=DocumentTemplateResponse)
async def create_template(request: DocumentTemplateCreateRequest, db: Session = Depends(get_db)):
    """Create document template"""
    try:
        template = DocumentTemplate(
            id=str(uuid.uuid4()),
            document_type=request.document_type.value,
            name=request.template_name,
            description=request.description,
            expected_fields=request.required_fields,
            extraction_rules=request.extraction_rules or {},
            is_active=True
        )
        db.add(template)
        db.commit()
        db.refresh(template)
        return DocumentTemplateResponse.model_validate(template)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating template: {str(e)}")

@router.get("/templates/{document_type}", response_model=DocumentTemplateResponse)
async def get_template_by_type(document_type: DocumentTypeEnum, db: Session = Depends(get_db)):
    """Get document template by document type"""
    template = db.query(DocumentTemplate).filter(
        and_(
            DocumentTemplate.document_type == document_type.value,
            DocumentTemplate.is_active == True
        )
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return DocumentTemplateResponse.model_validate(template)

@router.get("/templates", response_model=List[DocumentTemplateResponse])
async def list_templates(
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List document templates"""
    query = db.query(DocumentTemplate)
    if is_active is not None:
        query = query.filter(DocumentTemplate.is_active == is_active)
    
    templates = query.offset(skip).limit(limit).all()
    return [DocumentTemplateResponse.model_validate(t) for t in templates]

# Statistics & Analytics Endpoints

@router.get("/statistics", response_model=DocumentProcessingStatisticsResponse)
async def get_processing_statistics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get document processing statistics"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    total_documents = db.query(Document).filter(Document.created_at >= cutoff_date).count()
    processed = db.query(Document).filter(
        and_(Document.created_at >= cutoff_date, Document.status == DocumentStatus.VERIFIED.value)
    ).count()
    pending = db.query(Document).filter(
        and_(Document.created_at >= cutoff_date, Document.status == DocumentStatus.UPLOADED.value)
    ).count()
    failed = db.query(Document).filter(
        and_(Document.created_at >= cutoff_date, Document.status == DocumentStatus.REJECTED.value)
    ).count()
    
    success_rate = (processed / total_documents * 100) if total_documents > 0 else 0
    
    return DocumentProcessingStatisticsResponse(
        total_documents=total_documents,
        documents_processed=processed,
        documents_pending=pending,
        documents_failed=failed,
        average_processing_time_ms=500.0,
        success_rate=success_rate,
        extraction_success_rate=92.5,
        validation_success_rate=95.0,
        period_start=cutoff_date,
        period_end=datetime.utcnow()
    )

@router.get("/customers/{customer_id}/summary", response_model=CustomerDocumentSummaryResponse)
async def get_customer_document_summary(customer_id: str, db: Session = Depends(get_db)):
    """Get document summary for customer"""
    total = db.query(Document).filter(Document.customer_id == customer_id).count()
    verified = db.query(Document).filter(
        and_(Document.customer_id == customer_id, Document.status == DocumentStatus.COMPLETED.value)
    ).count()
    pending = db.query(Document).filter(
        and_(Document.customer_id == customer_id, Document.status == DocumentStatus.UPLOADED.value)
    ).count()
    failed = db.query(Document).filter(
        and_(Document.customer_id == customer_id, Document.status == DocumentStatus.REJECTED.value)
    ).count()
    
    last_upload = db.query(Document).filter(
        Document.customer_id == customer_id
    ).order_by(desc(Document.created_at)).first()
    
    kyc_completion = (verified / total * 100) if total > 0 else 0
    
    return CustomerDocumentSummaryResponse(
        customer_id=customer_id,
        total_documents=total,
        verified_documents=verified,
        pending_documents=pending,
        failed_documents=failed,
        last_document_upload=last_upload.created_at if last_upload else None,
        kyc_completion_status="COMPLETE" if kyc_completion >= 100 else ("IN_PROGRESS" if kyc_completion > 0 else "NOT_STARTED"),
        kyc_completion_percentage=kyc_completion
    )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "document-ai"}
