"""Credit Scoring Service Database Models - Credit Scores and Risk Assessment"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, Enum, UniqueConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

Base = declarative_base()


class RiskLevel(str, enum.Enum):
    """Risk Level Classification"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class CreditScore(Base):
    """Credit Score model"""
    __tablename__ = "credit_scores"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), nullable=False, unique=True, index=True)  # Reference to customer service
    
    # Score Components
    fico_score = Column(Integer, nullable=True)  # 300-850
    vantage_score = Column(Integer, nullable=True)  # 300-850
    internal_score = Column(Integer, nullable=False)  # 0-100
    
    # Score Breakdown
    payment_history = Column(Float, default=0.0)  # Weight: 35%
    credit_utilization = Column(Float, default=0.0)  # Weight: 30%
    credit_age = Column(Float, default=0.0)  # Weight: 15%
    credit_mix = Column(Float, default=0.0)  # Weight: 10%
    new_inquiries = Column(Float, default=0.0)  # Weight: 10%
    
    # Dates
    calculated_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reports = relationship("CreditReport", back_populates="credit_score", cascade="all, delete-orphan")
    factors = relationship("RiskFactor", back_populates="credit_score", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CreditScore(customer_id={self.customer_id}, internal_score={self.internal_score})>"


class CreditReport(Base):
    """Credit report model"""
    __tablename__ = "credit_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    credit_score_id = Column(String(36), ForeignKey('credit_scores.id'), nullable=False, index=True)
    customer_id = Column(String(36), nullable=False, index=True)
    
    # Report Content
    summary = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)
    
    # Report Status
    is_approved = Column(Boolean, default=False)
    approved_by = Column(String(36), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    credit_score = relationship("CreditScore", back_populates="reports")

    def __repr__(self):
        return f"<CreditReport(customer_id={self.customer_id})>"


class RiskProfile(Base):
    """Risk profile model"""
    __tablename__ = "risk_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), nullable=False, unique=True, index=True)
    
    # Risk Assessment
    overall_risk_level = Column(Enum(RiskLevel), default=RiskLevel.MEDIUM)
    risk_score = Column(Float, default=50.0)  # 0-100
    
    # Risk Components
    credit_risk = Column(Float, default=0.0)
    fraud_risk = Column(Float, default=0.0)
    behavioral_risk = Column(Float, default=0.0)
    income_stability_risk = Column(Float, default=0.0)
    
    # Assessment Details
    assessment_method = Column(String(100), nullable=True)  # e.g., "automated", "manual"
    last_assessed = Column(DateTime, default=datetime.utcnow)
    next_assessment = Column(DateTime, nullable=True)
    
    # Recommendations
    recommended_credit_limit = Column(Float, nullable=True)
    recommended_actions = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    factors = relationship("RiskFactor", back_populates="risk_profile", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<RiskProfile(customer_id={self.customer_id}, level={self.overall_risk_level})>"


class RiskFactor(Base):
    """Individual risk factors model"""
    __tablename__ = "risk_factors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    credit_score_id = Column(String(36), ForeignKey('credit_scores.id'), nullable=True, index=True)
    risk_profile_id = Column(String(36), ForeignKey('risk_profiles.id'), nullable=True, index=True)
    
    # Factor Details
    factor_name = Column(String(100), nullable=False)
    factor_type = Column(String(50), nullable=False)  # e.g., "positive", "negative", "neutral"
    impact_score = Column(Float, nullable=False)  # -100 to +100
    description = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    credit_score = relationship("CreditScore", back_populates="factors")
    risk_profile = relationship("RiskProfile", back_populates="factors")

    def __repr__(self):
        return f"<RiskFactor(name={self.factor_name}, impact={self.impact_score})>"


class CreditHistory(Base):
    """Credit history tracking model"""
    __tablename__ = "credit_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), nullable=False, index=True)
    
    # Account Info
    account_type = Column(String(50), nullable=False)  # e.g., "credit_card", "auto_loan"
    account_status = Column(String(50), nullable=False)  # e.g., "open", "closed", "charged_off"
    original_amount = Column(Float, nullable=True)
    current_balance = Column(Float, nullable=True)
    payment_amount = Column(Float, nullable=True)
    
    # Dates
    account_opened = Column(DateTime, nullable=True)
    last_payment = Column(DateTime, nullable=True)
    account_closed = Column(DateTime, nullable=True)
    
    # Payment Performance
    on_time_payments = Column(Integer, default=0)
    late_payments = Column(Integer, default=0)
    missed_payments = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CreditHistory(customer_id={self.customer_id}, type={self.account_type})>"


class AuditLog(Base):
    """Audit log for credit scoring service actions"""
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=False)
    changes = Column(String(1000), nullable=True)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog(customer_id={self.customer_id}, action={self.action})>"
