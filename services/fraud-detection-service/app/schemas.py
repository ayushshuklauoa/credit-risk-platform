"""Fraud Detection Service - Pydantic Schemas"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum

# Enums
class AlertSeverityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatusEnum(str, Enum):
    NEW = "new"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    DISMISSED = "dismissed"
    RESOLVED = "resolved"

class AnomalyTypeEnum(str, Enum):
    TRANSACTION_VELOCITY = "transaction_velocity"
    UNUSUAL_AMOUNT = "unusual_amount"
    GEOGRAPHIC_ANOMALY = "geographic_anomaly"
    BEHAVIORAL_CHANGE = "behavioral_change"
    MERCHANT_MISMATCH = "merchant_mismatch"
    TIME_PATTERN = "time_pattern"
    ACCOUNT_TAKEOVER = "account_takeover"

# Fraud Alert Schemas
class FraudAlertResponse(BaseModel):
    id: str
    customer_id: str
    account_id: Optional[str]
    transaction_id: Optional[str]
    alert_type: str
    anomaly_type: AnomalyTypeEnum
    severity: AlertSeverityEnum
    status: AlertStatusEnum
    fraud_score: float
    confidence_level: float
    description: str
    detected_at: datetime
    investigated_at: Optional[datetime]
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class FraudAlertDetailResponse(FraudAlertResponse):
    details: Optional[Dict]
    investigation_notes: Optional[str]
    investigated_by: Optional[str]
    created_at: datetime
    updated_at: datetime

# Fraud Rule Schemas
class FraudRuleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    rule_type: str
    threshold: Optional[float]
    is_active: bool
    priority: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class FraudRuleCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    rule_type: str
    threshold: Optional[float] = None
    priority: int = 0

# Anomaly Detection Schemas
class AnomalyDetectionResponse(BaseModel):
    id: str
    customer_id: str
    anomaly_type: AnomalyTypeEnum
    anomaly_score: float
    description: str
    detection_method: str
    baseline_value: Optional[float]
    actual_value: Optional[float]
    deviation_percentage: Optional[float]
    is_flagged: bool
    is_investigated: bool
    is_confirmed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Velocity Check Schemas
class VelocityCheckResponse(BaseModel):
    id: str
    customer_id: str
    account_id: str
    transaction_count_1h: int
    transaction_count_24h: int
    amount_sum_1h: float
    amount_sum_24h: float
    location_changes_24h: int
    is_suspicious: bool
    risk_level: Optional[str]
    last_checked: datetime
    
    class Config:
        from_attributes = True

# Request Schemas
class CreateFraudAlertRequest(BaseModel):
    customer_id: str
    account_id: Optional[str] = None
    transaction_id: Optional[str] = None
    alert_type: str
    anomaly_type: AnomalyTypeEnum
    severity: AlertSeverityEnum
    fraud_score: float = Field(..., ge=0, le=100)
    confidence_level: float = Field(..., ge=0, le=100)
    description: str

class UpdateFraudAlertRequest(BaseModel):
    status: Optional[AlertStatusEnum] = None
    investigation_notes: Optional[str] = None
    investigated_by: Optional[str] = None

class ConfirmFraudAlertRequest(BaseModel):
    reason: str
    action_taken: Optional[str] = None

# Summary & Analytics
class FraudStatisticsResponse(BaseModel):
    total_alerts: int
    new_alerts: int
    confirmed_frauds: int
    dismissed_alerts: int
    high_severity_count: int
    average_fraud_score: float
    investigation_rate: float
    confirmation_rate: float
    period_start: datetime
    period_end: datetime

class FraudAnalyticsResponse(BaseModel):
    customer_id: str
    alert_count: int
    confirmed_fraud_count: int
    suspicious_transactions: int
    risk_level: str
    last_alert: Optional[datetime]
    fraud_probability: float
