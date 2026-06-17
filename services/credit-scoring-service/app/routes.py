"""Credit Scoring Service - Routes and Endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import logging
import uuid
import os

from app.database import get_db
from app.models import (
    CreditScore, CreditReport, RiskProfile, RiskFactor, CreditHistory, AuditLog, RiskLevel
)
from app.schemas import (
    CreditScoreResponse, CreditReportResponse, RiskProfileResponse, RiskProfileDetailResponse,
    CreditHistoryResponse, CreditSummaryResponse, CreditScoreCalculationRequest,
    RiskProfileAssessmentRequest, CreditReportGenerationRequest, CreditReportApprovalRequest,
    CreditAssessmentResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

# ==========================================
# Initialize Machine Learning Predictor
# ==========================================
import sys
# Safely add shared-lib to Python's path so it can be imported
if os.path.exists('/app/shared-lib'):
    sys.path.insert(0, '/app/shared-lib')
    MODEL_PATH = '/app/shared-lib/credit_risk_model.joblib'
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../shared-lib')))
    MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../shared-lib/credit_risk_model.joblib'))

import prediction
predictor = prediction.DefaultPredictor(MODEL_PATH)
# ==========================================


def calculate_credit_score(customer_id: str) -> int:
    """Calculate internal credit score based on factors (0-100)"""
    # Placeholder algorithm - in production, would query multiple data sources
    base_score = 50
    # This would be replaced with actual scoring logic
    return base_score


def assess_risk_profile(customer_id: str) -> dict:
    """Assess overall risk profile"""
    # Placeholder - would aggregate multiple risk factors
    return {
        "overall_risk_level": RiskLevel.MEDIUM,
        "risk_score": 50.0,
        "credit_risk": 40.0,
        "fraud_risk": 30.0,
        "behavioral_risk": 45.0,
        "income_stability_risk": 55.0
    }


# ============ Credit Score Operations ============

@router.post("/calculate-score", response_model=CreditScoreResponse, tags=["Credit Scoring"])
async def calculate_credit_score_endpoint(
    request: CreditScoreCalculationRequest,
    db: Session = Depends(get_db)
):
    """Calculate or update credit score for a customer"""
    try:
        # Check if score already exists
        existing_score = db.query(CreditScore).filter(
            CreditScore.customer_id == request.customer_id
        ).first()
        
        # Calculate score
        internal_score = calculate_credit_score(request.customer_id)
        
        if existing_score:
            # Update existing score
            existing_score.internal_score = internal_score
            existing_score.calculated_at = datetime.utcnow()
            existing_score.last_updated = datetime.utcnow()
            db.add(existing_score)
            db.commit()
            db.refresh(existing_score)
            score_record = existing_score
            logger.info(f"✅ Credit score updated for customer: {request.customer_id}")
        else:
            # Create new score
            credit_score = CreditScore(
                customer_id=request.customer_id,
                internal_score=internal_score,
                payment_history=0.0,
                credit_utilization=0.0,
                credit_age=0.0,
                credit_mix=0.0,
                new_inquiries=0.0
            )
            
            # Audit log
            audit_log = AuditLog(
                customer_id=request.customer_id,
                action="CREDIT_SCORE_CALCULATED",
                resource="credit_scores",
                changes=f"Score: {internal_score}",
                status="success"
            )
            
            db.add(credit_score)
            db.add(audit_log)
            db.commit()
            db.refresh(credit_score)
            score_record = credit_score
            logger.info(f"✅ Credit score calculated for customer: {request.customer_id}")
        
        return CreditScoreResponse.model_validate(score_record)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Credit score calculation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate credit score"
        )


@router.get("/score/{customer_id}", response_model=CreditScoreResponse, tags=["Credit Scoring"])
async def get_credit_score(customer_id: str, db: Session = Depends(get_db)):
    """Get credit score for a customer"""
    credit_score = db.query(CreditScore).filter(
        CreditScore.customer_id == customer_id
    ).first()
    
    if not credit_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credit score not found"
        )
    
    return CreditScoreResponse.model_validate(credit_score)


# ============ Risk Profile Operations ============

@router.post("/assess-risk", response_model=RiskProfileDetailResponse, tags=["Risk Assessment"])
async def assess_risk(
    request: RiskProfileAssessmentRequest,
    db: Session = Depends(get_db)
):
    """Assess risk profile for a customer"""
    try:
        # Check if profile exists
        existing_profile = db.query(RiskProfile).filter(
            RiskProfile.customer_id == request.customer_id
        ).first()
        
        # Calculate Debt Ratio
        debt_ratio = request.debt / request.income if request.income > 0 else 0.0
        
        # Run the actual Machine Learning Prediction!
        prediction_result = await predictor.predict_default(
            customer_id=request.customer_id,
            credit_score=request.credit_score,
            income=request.income,
            debt_ratio=debt_ratio,
            age=30  # Defaulting age for now
        )
        
        risk_assessment = {
            "overall_risk_level": RiskLevel(prediction_result["risk_level"].lower()),
            "risk_score": float(prediction_result["default_probability"] * 100),
            "credit_risk": float((1 - prediction_result["default_probability"]) * 100),
            "fraud_risk": 30.0,
            "behavioral_risk": 45.0,
            "income_stability_risk": 55.0,
            "recommended_actions": prediction_result.get("recommended_action", "")
        }
        
        if existing_profile:
            # Update existing profile
            existing_profile.overall_risk_level = risk_assessment["overall_risk_level"]
            existing_profile.risk_score = risk_assessment["risk_score"]
            existing_profile.credit_risk = risk_assessment["credit_risk"]
            existing_profile.fraud_risk = risk_assessment["fraud_risk"]
            existing_profile.behavioral_risk = risk_assessment["behavioral_risk"]
            existing_profile.income_stability_risk = risk_assessment["income_stability_risk"]
            existing_profile.assessment_method = request.assessment_method
            existing_profile.recommended_actions = risk_assessment["recommended_actions"]
            existing_profile.last_assessed = datetime.utcnow()
            existing_profile.next_assessment = datetime.utcnow() + timedelta(days=30)
            db.add(existing_profile)
            db.commit()
            db.refresh(existing_profile)
            profile = existing_profile
            logger.info(f"✅ Risk profile updated for customer: {request.customer_id}")
        else:
            # Create new profile
            profile = RiskProfile(
                customer_id=request.customer_id,
                overall_risk_level=risk_assessment["overall_risk_level"],
                risk_score=risk_assessment["risk_score"],
                credit_risk=risk_assessment["credit_risk"],
                fraud_risk=risk_assessment["fraud_risk"],
                behavioral_risk=risk_assessment["behavioral_risk"],
                income_stability_risk=risk_assessment["income_stability_risk"],
                assessment_method=request.assessment_method,
                recommended_actions=risk_assessment["recommended_actions"],
                next_assessment=datetime.utcnow() + timedelta(days=30)
            )
            db.add(profile)
            db.flush()
            
            # Create risk factors
            factors = [
                RiskFactor(
                    risk_profile_id=profile.id,
                    factor_name="Credit Risk",
                    factor_type="neutral",
                    impact_score=risk_assessment["credit_risk"] - 50
                ),
                RiskFactor(
                    risk_profile_id=profile.id,
                    factor_name="Fraud Risk",
                    factor_type="negative",
                    impact_score=risk_assessment["fraud_risk"] - 50
                ),
                RiskFactor(
                    risk_profile_id=profile.id,
                    factor_name="Behavioral Risk",
                    factor_type="neutral",
                    impact_score=risk_assessment["behavioral_risk"] - 50
                ),
                RiskFactor(
                    risk_profile_id=profile.id,
                    factor_name="Income Stability",
                    factor_type="neutral",
                    impact_score=50 - risk_assessment["income_stability_risk"]
                )
            ]
            
            # Audit log
            audit_log = AuditLog(
                customer_id=request.customer_id,
                action="RISK_PROFILE_ASSESSED",
                resource="risk_profiles",
                changes=f"Risk Level: {risk_assessment['overall_risk_level'].value}",
                status="success"
            )
            
            db.add_all(factors)
            db.add(audit_log)
            db.commit()
            db.refresh(profile)
            logger.info(f"✅ Risk profile created for customer: {request.customer_id}")
        
        # Load factors
        profile.factors = db.query(RiskFactor).filter(
            RiskFactor.risk_profile_id == profile.id
        ).all()
        
        return RiskProfileDetailResponse.model_validate(profile)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Risk assessment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assess risk profile: {str(e)}"
        )


@router.get("/risk/{customer_id}", response_model=RiskProfileDetailResponse, tags=["Risk Assessment"])
async def get_risk_profile(customer_id: str, db: Session = Depends(get_db)):
    """Get risk profile for a customer"""
    risk_profile = db.query(RiskProfile).filter(
        RiskProfile.customer_id == customer_id
    ).first()
    
    if not risk_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk profile not found"
        )
    
    # Load factors
    factors = db.query(RiskFactor).filter(
        RiskFactor.risk_profile_id == risk_profile.id
    ).all()
    
    return RiskProfileDetailResponse.model_validate(risk_profile)


# ============ Credit Report Operations ============

@router.post("/generate-report", response_model=CreditReportResponse, tags=["Reports"])
async def generate_credit_report(
    request: CreditReportGenerationRequest,
    db: Session = Depends(get_db)
):
    """Generate credit report for a customer"""
    try:
        # Get credit score
        credit_score = db.query(CreditScore).filter(
            CreditScore.id == request.credit_score_id
        ).first()
        
        if not credit_score:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credit score not found"
            )
        
        # Generate report
        report = CreditReport(
            credit_score_id=request.credit_score_id,
            customer_id=request.customer_id,
            summary=f"Credit report for customer {request.customer_id}",
            recommendations="Review credit profile for opportunities",
            is_approved=False
        )
        
        # Audit log
        audit_log = AuditLog(
            customer_id=request.customer_id,
            action="CREDIT_REPORT_GENERATED",
            resource="credit_reports",
            status="success"
        )
        
        db.add(report)
        db.add(audit_log)
        db.commit()
        db.refresh(report)
        
        logger.info(f"✅ Credit report generated for customer: {request.customer_id}")
        return CreditReportResponse.model_validate(report)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Report generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate credit report"
        )


@router.get("/report/{customer_id}", response_model=CreditReportResponse, tags=["Reports"])
async def get_latest_credit_report(customer_id: str, db: Session = Depends(get_db)):
    """Get latest credit report for a customer"""
    report = db.query(CreditReport).filter(
        CreditReport.customer_id == customer_id
    ).order_by(CreditReport.created_at.desc()).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No credit report found"
        )
    
    return CreditReportResponse.model_validate(report)


@router.post("/report/{report_id}/approve", response_model=CreditReportResponse, tags=["Reports"])
async def approve_credit_report(
    report_id: str,
    request: CreditReportApprovalRequest,
    db: Session = Depends(get_db)
):
    """Approve a credit report"""
    report = db.query(CreditReport).filter(CreditReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    try:
        report.is_approved = True
        report.approved_by = request.approved_by
        report.approved_at = datetime.utcnow()
        
        db.add(report)
        db.commit()
        db.refresh(report)
        
        logger.info(f"✅ Credit report approved: {report_id}")
        return CreditReportResponse.model_validate(report)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Report approval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve report"
        )


# ============ Summary & Assessment ============

@router.get("/summary/{customer_id}", response_model=CreditSummaryResponse, tags=["Summary"])
async def get_credit_summary(customer_id: str, db: Session = Depends(get_db)):
    """Get complete credit summary for a customer"""
    # Get credit score
    credit_score = db.query(CreditScore).filter(
        CreditScore.customer_id == customer_id
    ).first()
    
    # Get risk profile
    risk_profile = db.query(RiskProfile).filter(
        RiskProfile.customer_id == customer_id
    ).first()
    
    # Get latest report
    latest_report = db.query(CreditReport).filter(
        CreditReport.customer_id == customer_id
    ).order_by(CreditReport.created_at.desc()).first()
    
    # Get credit histories
    histories = db.query(CreditHistory).filter(
        CreditHistory.customer_id == customer_id
    ).all()
    
    return CreditSummaryResponse(
        customer_id=customer_id,
        credit_score=credit_score.internal_score if credit_score else 0,
        risk_level=risk_profile.overall_risk_level if risk_profile else RiskLevel.MEDIUM,
        risk_score=risk_profile.risk_score if risk_profile else 50.0,
        credit_report=CreditReportResponse.model_validate(latest_report) if latest_report else None,
        risk_profile=RiskProfileResponse.model_validate(risk_profile) if risk_profile else None,
        credit_histories=[CreditHistoryResponse.model_validate(h) for h in histories]
    )


# ============ Health Check ============

@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "credit-scoring-service",
        "timestamp": datetime.utcnow().isoformat()
    }
