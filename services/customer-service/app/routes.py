"""Customer Service - Routes and Endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.database import get_db
from app.models import Customer, CustomerProfile, CustomerDocument, AuditLog, KYCStatus, CustomerStatus
from app.schemas import (
    CustomerCreateRequest, CustomerUpdateRequest, CustomerResponse, CustomerDetailResponse,
    CustomerProfileResponse, CustomerProfileUpdateRequest, KYCVerificationRequest,
    CustomerDocumentResponse, CustomerRiskResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

# ============ Customer CRUD ============

@router.post("", response_model=CustomerResponse, tags=["Customers"])
async def create_customer(request: CustomerCreateRequest, db: Session = Depends(get_db)):
    """Create a new customer"""
    # Check if customer already exists for this user
    existing = db.query(Customer).filter(Customer.user_id == request.user_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer already exists for this user"
        )
    
    try:
        # Create customer
        customer = Customer(
            user_id=request.user_id,
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            phone=request.phone,
            date_of_birth=request.date_of_birth,
            status=CustomerStatus.ACTIVE,
            kyc_status=KYCStatus.NOT_STARTED
        )
        
        db.add(customer)
        db.flush()  # Flush to generate customer.id
        
        # Create default profile
        profile = CustomerProfile(customer_id=customer.id)
        
        # Audit log
        audit_log = AuditLog(
            customer_id=customer.id,
            action="CUSTOMER_CREATED",
            resource="customers",
            status="success"
        )
        
        db.add(customer)
        db.add(profile)
        db.add(audit_log)
        db.commit()
        db.refresh(customer)
        
        logger.info(f"✅ Customer created: {customer.email}")
        return CustomerResponse.model_validate(customer)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Customer creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create customer"
        )


@router.get("/{customer_id}", response_model=CustomerDetailResponse, tags=["Customers"])
async def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """Get customer details"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return CustomerDetailResponse.model_validate(customer)


@router.put("/{customer_id}", response_model=CustomerResponse, tags=["Customers"])
async def update_customer(
    customer_id: str,
    request: CustomerUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update customer details"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    try:
        # Update fields
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(customer, field, value)
        
        customer.updated_at = datetime.utcnow()
        
        # Audit log
        audit_log = AuditLog(
            customer_id=customer.id,
            action="CUSTOMER_UPDATED",
            resource="customers",
            changes=str(update_data),
            status="success"
        )
        
        db.add(customer)
        db.add(audit_log)
        db.commit()
        db.refresh(customer)
        
        logger.info(f"✅ Customer updated: {customer_id}")
        return CustomerResponse.model_validate(customer)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Customer update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update customer"
        )


@router.delete("/{customer_id}", tags=["Customers"])
async def delete_customer(customer_id: str, db: Session = Depends(get_db)):
    """Delete customer (soft delete via status)"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    try:
        customer.status = CustomerStatus.CLOSED
        customer.updated_at = datetime.utcnow()
        
        # Audit log
        audit_log = AuditLog(
            customer_id=customer.id,
            action="CUSTOMER_DELETED",
            resource="customers",
            status="success"
        )
        
        db.add(customer)
        db.add(audit_log)
        db.commit()
        
        logger.info(f"✅ Customer deleted: {customer_id}")
        return {"message": "Customer deleted successfully"}
    
    except Exception as e:
        db.rollback()
        logger.error(f"Customer deletion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete customer"
        )


# ============ Customer Profile ============

@router.get("/{customer_id}/profile", response_model=CustomerProfileResponse, tags=["Profile"])
async def get_profile(customer_id: str, db: Session = Depends(get_db)):
    """Get customer profile"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    profile = db.query(CustomerProfile).filter(
        CustomerProfile.customer_id == customer_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return CustomerProfileResponse.model_validate(profile)


@router.put("/{customer_id}/profile", response_model=CustomerProfileResponse, tags=["Profile"])
async def update_profile(
    customer_id: str,
    request: CustomerProfileUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update customer profile"""
    profile = db.query(CustomerProfile).filter(
        CustomerProfile.customer_id == customer_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    try:
        # Update fields
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        
        profile.updated_at = datetime.utcnow()
        
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
        logger.info(f"✅ Profile updated: {customer_id}")
        return CustomerProfileResponse.model_validate(profile)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


# ============ KYC & Verification ============

@router.post("/{customer_id}/kyc-verify", tags=["KYC"])
async def verify_kyc(
    customer_id: str,
    request: KYCVerificationRequest,
    db: Session = Depends(get_db)
):
    """Update KYC verification status"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    try:
        customer.kyc_status = request.kyc_status
        
        if request.kyc_status == KYCStatus.VERIFIED:
            customer.kyc_verified_at = datetime.utcnow()
        elif request.kyc_status == KYCStatus.REJECTED:
            customer.kyc_rejection_reason = request.rejection_reason
        
        customer.updated_at = datetime.utcnow()
        
        # Audit log
        audit_log = AuditLog(
            customer_id=customer.id,
            action="KYC_UPDATED",
            resource="kyc",
            changes=f"Status: {request.kyc_status.value}",
            status="success"
        )
        
        db.add(customer)
        db.add(audit_log)
        db.commit()
        
        logger.info(f"✅ KYC updated for customer: {customer_id}")
        return {"message": "KYC status updated", "status": request.kyc_status.value}
    
    except Exception as e:
        db.rollback()
        logger.error(f"KYC update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update KYC"
        )


# ============ Risk & Scoring ============

@router.get("/{customer_id}/risk", response_model=CustomerRiskResponse, tags=["Risk"])
async def get_risk_profile(customer_id: str, db: Session = Depends(get_db)):
    """Get customer risk profile"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return CustomerRiskResponse(
        customer_id=customer.id,
        risk_score=customer.risk_score,
        credit_score=customer.credit_score,
        kyc_status=customer.kyc_status,
        status=customer.status
    )


# ============ Health Check ============

@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "customer-service",
        "timestamp": datetime.utcnow().isoformat()
    }
