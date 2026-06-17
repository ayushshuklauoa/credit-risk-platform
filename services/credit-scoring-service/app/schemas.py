"""Credit Scoring Service - Pydantic Schemas"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

# Enums
class RiskLevelEnum(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

# Credit Score Schemas
class CreditScoreResponse(BaseModel):
    id: str
    customer_id: str
    fico_score: Optional[int]
    vantage_score: Optional[int]
    internal_score: int
    payment_history: float
    credit_utilization: float
    credit_age: float
    credit_mix: float
    new_inquiries: float
    calculated_at: datetime
    last_updated: datetime
    
    class Config:
        from_attributes = True

class RiskFactorResponse(BaseModel):
    id: str
    factor_name: str
    factor_type: str  # positive, negative, neutral
    impact_score: float
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class RiskProfileResponse(BaseModel):
    id: str
    customer_id: str
    overall_risk_level: RiskLevelEnum
    risk_score: float
    credit_risk: float
    fraud_risk: float
    behavioral_risk: float
    income_stability_risk: float
    assessment_method: Optional[str]
    recommended_credit_limit: Optional[float]
    last_assessed: datetime
    next_assessment: Optional[datetime]
    
    class Config:
        from_attributes = True

class RiskProfileDetailResponse(RiskProfileResponse):
    factors: List[RiskFactorResponse] = []
    recommended_actions: Optional[str]
    created_at: datetime
    updated_at: datetime

class CreditReportResponse(BaseModel):
    id: str
    customer_id: str
    credit_score_id: str
    summary: Optional[str]
    recommendations: Optional[str]
    file_path: Optional[str]
    is_approved: bool
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CreditHistoryResponse(BaseModel):
    id: str
    customer_id: str
    account_type: str
    account_status: str
    original_amount: Optional[float]
    current_balance: Optional[float]
    payment_amount: Optional[float]
    on_time_payments: int
    late_payments: int
    missed_payments: int
    account_opened: Optional[datetime]
    last_payment: Optional[datetime]
    account_closed: Optional[datetime]
    
    class Config:
        from_attributes = True

class CreditSummaryResponse(BaseModel):
    customer_id: str
    credit_score: int
    risk_level: RiskLevelEnum
    risk_score: float
    credit_report: Optional[CreditReportResponse]
    risk_profile: Optional[RiskProfileResponse]
    credit_histories: List[CreditHistoryResponse] = []

# Request Schemas
class CreditScoreCalculationRequest(BaseModel):
    customer_id: str
    include_historical: bool = True

class RiskProfileAssessmentRequest(BaseModel):
    customer_id: str
    assessment_method: str = "automated"  # automated, manual
    credit_score: float = 0.0
    income: float = 0.0
    debt: float = 0.0

class CreditReportGenerationRequest(BaseModel):
    customer_id: str
    credit_score_id: str

class CreditReportApprovalRequest(BaseModel):
    approved_by: str
    notes: Optional[str] = None

# Aggregated Response
class CreditAssessmentResponse(BaseModel):
    customer_id: str
    timestamp: datetime
    credit_score: Optional[CreditScoreResponse]
    risk_profile: Optional[RiskProfileDetailResponse]
    latest_report: Optional[CreditReportResponse]
    recommendation: str
