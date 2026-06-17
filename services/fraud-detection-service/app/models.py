"""Fraud Detection Service Database Models - Fraud Detection and Alerts"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, Enum, JSON, UniqueConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

Base = declarative_base()


class AlertSeverity(str, enum.Enum):
    """Alert Severity Level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, enum.Enum):
    """Alert Status"""
    NEW = "new"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    DISMISSED = "dismissed"
    RESOLVED = "resolved"


class AnomalyType(str, enum.Enum):
    """Anomaly Type"""
    TRANSACTION_VELOCITY = "transaction_velocity"
    UNUSUAL_AMOUNT = "unusual_amount"
    GEOGRAPHIC_ANOMALY = "geographic_anomaly"
    BEHAVIORAL_CHANGE = "behavioral_change"
    MERCHANT_MISMATCH = "merchant_mismatch"
    TIME_PATTERN = "time_pattern"
    ACCOUNT_TAKEOVER = "account_takeover"


class FraudAlert(Base):
    """Fraud alert model"""
    __tablename__ = "fraud_alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), nullable=False, index=True)
    account_id = Column(String(36), nullable=True, index=True)
    transaction_id = Column(String(36), nullable=True, index=True)
    
    # Alert Details
    alert_type = Column(String(100), nullable=False)
    anomaly_type = Column(Enum(AnomalyType), nullable=False)
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.MEDIUM)
    status = Column(Enum(AlertStatus), default=AlertStatus.NEW)
    
    # Risk Assessment
    fraud_score = Column(Float, default=0.0)  # 0-100
    confidence_level = Column(Float, default=0.0)  # 0-100
    
    # Description
    description = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    
    # Investigation
    investigated_by = Column(String(36), nullable=True)
    investigation_notes = Column(Text, nullable=True)
    
    # Dates
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    investigated_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rules = relationship("FraudRule", secondary="alert_rule_map", back_populates="alerts")

    def __repr__(self):
        return f"<FraudAlert(customer_id={self.customer_id}, severity={self.severity})>"


class FraudRule(Base):
    """Fraud detection rule model"""
    __tablename__ = "fraud_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    rule_type = Column(String(50), nullable=False)  # e.g., "velocity", "amount", "pattern"
    
    # Rule Conditions
    condition_json = Column(JSON, nullable=False)
    threshold = Column(Float, nullable=True)
    
    # Rule Status
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    alerts = relationship("FraudAlert", secondary="alert_rule_map", back_populates="rules")
    patterns = relationship("FraudPattern", back_populates="rule", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FraudRule(name={self.name}, type={self.rule_type})>"


class FraudPattern(Base):
    """Fraud pattern model for machine learning"""
    __tablename__ = "fraud_patterns"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_id = Column(String(36), ForeignKey('fraud_rules.id'), nullable=False, index=True)
    
    # Pattern Details
    pattern_name = Column(String(100), nullable=False)
    pattern_type = Column(String(50), nullable=False)
    pattern_data = Column(JSON, nullable=False)
    
    # Pattern Effectiveness
    hit_count = Column(Integer, default=0)
    false_positive_count = Column(Integer, default=0)
    effectiveness_score = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rule = relationship("FraudRule", back_populates="patterns")

    def __repr__(self):
        return f"<FraudPattern(name={self.pattern_name})>"


class AnomalyDetection(Base):
    """Anomaly detection result model"""
    __tablename__ = "anomaly_detections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), nullable=False, index=True)
    
    # Anomaly Details
    anomaly_type = Column(Enum(AnomalyType), nullable=False)
    anomaly_score = Column(Float, nullable=False)  # 0-100
    description = Column(String(255), nullable=False)
    
    # Detection Method
    detection_method = Column(String(50), nullable=False)  # e.g., "statistical", "ml", "rule_based"
    model_version = Column(String(50), nullable=True)
    
    # Related Data
    baseline_value = Column(Float, nullable=True)
    actual_value = Column(Float, nullable=True)
    deviation_percentage = Column(Float, nullable=True)
    
    # Status
    is_flagged = Column(Boolean, default=False)
    is_investigated = Column(Boolean, default=False)
    is_confirmed = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<AnomalyDetection(customer_id={self.customer_id}, type={self.anomaly_type})>"


class VelocityCheck(Base):
    """Velocity check model for transaction fraud detection"""
    __tablename__ = "velocity_checks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), nullable=False, index=True)
    account_id = Column(String(36), nullable=False, index=True)
    
    # Velocity Metrics
    transaction_count_1h = Column(Integer, default=0)
    transaction_count_24h = Column(Integer, default=0)
    amount_sum_1h = Column(Float, default=0.0)
    amount_sum_24h = Column(Float, default=0.0)
    
    # Geographic Velocity
    location_changes_24h = Column(Integer, default=0)
    
    # Status
    is_suspicious = Column(Boolean, default=False)
    risk_level = Column(String(50), nullable=True)
    
    last_checked = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<VelocityCheck(customer_id={self.customer_id}, risk={self.risk_level})>"


# Association table for FraudAlert and FraudRule
from sqlalchemy import Table, ForeignKey
alert_rule_map = Table(
    'alert_rule_map',
    Base.metadata,
    Column('alert_id', String(36), ForeignKey('fraud_alerts.id')),
    Column('rule_id', String(36), ForeignKey('fraud_rules.id'))
)


class AuditLog(Base):
    """Audit log for fraud detection service actions"""
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
