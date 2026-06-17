"""Fraud Detection Service - Routes"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime, timedelta
import uuid
import json
from typing import List, Optional

from .database import get_db
from .models import (
    FraudAlert, FraudRule, FraudPattern, AnomalyDetection,
    VelocityCheck, AuditLog, AlertSeverity, AlertStatus, AnomalyType
)
from .schemas import (
    FraudAlertResponse, FraudAlertDetailResponse, FraudRuleResponse,
    FraudRuleCreateRequest, AnomalyDetectionResponse, VelocityCheckResponse,
    CreateFraudAlertRequest, UpdateFraudAlertRequest, ConfirmFraudAlertRequest,
    FraudStatisticsResponse, FraudAnalyticsResponse, AlertStatusEnum,
    AnomalyTypeEnum, AlertSeverityEnum
)

router = APIRouter()

# Fraud Alert Endpoints

@router.post("/alerts", response_model=FraudAlertResponse)
async def create_fraud_alert(request: CreateFraudAlertRequest, db: Session = Depends(get_db)):
    """Create a new fraud alert"""
    try:
        fraud_alert = FraudAlert(
            id=str(uuid.uuid4()),
            customer_id=request.customer_id,
            account_id=request.account_id,
            transaction_id=request.transaction_id,
            alert_type=request.alert_type,
            anomaly_type=request.anomaly_type.value,
            severity=request.severity.value,
            status=AlertStatus.NEW.value,
            fraud_score=request.fraud_score,
            confidence_level=request.confidence_level,
            description=request.description,
            detected_at=datetime.utcnow(),
            details={"detection_method": "rule_engine"}
        )
        
        audit_log = AuditLog(
            id=str(uuid.uuid4()),
            customer_id=request.customer_id,
            action="CREATE_ALERT",
            status="success",
            details={
                "alert_id": fraud_alert.id,
                "anomaly_type": request.anomaly_type,
                "severity": request.severity
            }
        )
        
        db.add_all([fraud_alert, audit_log])
        db.commit()
        db.refresh(fraud_alert)
        return FraudAlertResponse.model_validate(fraud_alert)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating fraud alert: {str(e)}")

@router.get("/alerts/{alert_id}", response_model=FraudAlertDetailResponse)
async def get_fraud_alert(alert_id: str, db: Session = Depends(get_db)):
    """Get fraud alert details by ID"""
    fraud_alert = db.query(FraudAlert).filter(FraudAlert.id == alert_id).first()
    if not fraud_alert:
        raise HTTPException(status_code=404, detail="Fraud alert not found")
    return FraudAlertDetailResponse.model_validate(fraud_alert)

@router.get("/alerts", response_model=List[FraudAlertResponse])
async def list_fraud_alerts(
    customer_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List fraud alerts with filtering"""
    query = db.query(FraudAlert)
    
    if customer_id:
        query = query.filter(FraudAlert.customer_id == customer_id)
    if status:
        query = query.filter(FraudAlert.status == status)
    if severity:
        query = query.filter(FraudAlert.severity == severity)
    
    alerts = query.order_by(desc(FraudAlert.detected_at)).offset(skip).limit(limit).all()
    return [FraudAlertResponse.model_validate(alert) for alert in alerts]

@router.put("/alerts/{alert_id}", response_model=FraudAlertResponse)
async def update_fraud_alert(
    alert_id: str,
    request: UpdateFraudAlertRequest,
    db: Session = Depends(get_db)
):
    """Update fraud alert status"""
    fraud_alert = db.query(FraudAlert).filter(FraudAlert.id == alert_id).first()
    if not fraud_alert:
        raise HTTPException(status_code=404, detail="Fraud alert not found")
    
    if request.status:
        fraud_alert.status = request.status.value
        if request.status == AlertStatusEnum.INVESTIGATING:
            fraud_alert.investigated_at = datetime.utcnow()
        elif request.status == AlertStatusEnum.RESOLVED:
            fraud_alert.resolved_at = datetime.utcnow()
    
    if request.investigation_notes:
        fraud_alert.investigation_notes = request.investigation_notes
    if request.investigated_by:
        fraud_alert.investigated_by = request.investigated_by
    
    fraud_alert.updated_at = datetime.utcnow()
    
    audit_log = AuditLog(
        id=str(uuid.uuid4()),
        customer_id=fraud_alert.customer_id,
        action="UPDATE_ALERT",
        status="success",
        details={"alert_id": alert_id, "new_status": request.status}
    )
    
    db.add(audit_log)
    db.commit()
    db.refresh(fraud_alert)
    return FraudAlertResponse.model_validate(fraud_alert)

@router.post("/alerts/{alert_id}/confirm", response_model=FraudAlertResponse)
async def confirm_fraud_alert(
    alert_id: str,
    request: ConfirmFraudAlertRequest,
    db: Session = Depends(get_db)
):
    """Confirm fraud alert and take action"""
    fraud_alert = db.query(FraudAlert).filter(FraudAlert.id == alert_id).first()
    if not fraud_alert:
        raise HTTPException(status_code=404, detail="Fraud alert not found")
    
    fraud_alert.status = AlertStatus.CONFIRMED.value
    fraud_alert.investigation_notes = request.reason
    if request.action_taken:
        fraud_alert.details = fraud_alert.details or {}
        fraud_alert.details["action_taken"] = request.action_taken
    fraud_alert.resolved_at = datetime.utcnow()
    fraud_alert.updated_at = datetime.utcnow()
    
    audit_log = AuditLog(
        id=str(uuid.uuid4()),
        customer_id=fraud_alert.customer_id,
        action="CONFIRM_FRAUD",
        status="success",
        details={"alert_id": alert_id, "action": request.action_taken}
    )
    
    db.add(audit_log)
    db.commit()
    db.refresh(fraud_alert)
    return FraudAlertResponse.model_validate(fraud_alert)

# Fraud Rule Endpoints

@router.post("/rules", response_model=FraudRuleResponse)
async def create_fraud_rule(request: FraudRuleCreateRequest, db: Session = Depends(get_db)):
    """Create a new fraud detection rule"""
    try:
        fraud_rule = FraudRule(
            id=str(uuid.uuid4()),
            name=request.name,
            description=request.description,
            rule_type=request.rule_type,
            threshold=request.threshold,
            is_active=True,
            priority=request.priority,
            condition_json=json.dumps({"threshold": request.threshold, "rule_type": request.rule_type})
        )
        db.add(fraud_rule)
        db.commit()
        db.refresh(fraud_rule)
        return FraudRuleResponse.model_validate(fraud_rule)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating fraud rule: {str(e)}")

@router.get("/rules", response_model=List[FraudRuleResponse])
async def list_fraud_rules(
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List fraud rules"""
    query = db.query(FraudRule)
    if is_active is not None:
        query = query.filter(FraudRule.is_active == is_active)
    rules = query.order_by(desc(FraudRule.priority)).offset(skip).limit(limit).all()
    return [FraudRuleResponse.model_validate(rule) for rule in rules]

@router.get("/rules/{rule_id}", response_model=FraudRuleResponse)
async def get_fraud_rule(rule_id: str, db: Session = Depends(get_db)):
    """Get fraud rule by ID"""
    rule = db.query(FraudRule).filter(FraudRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Fraud rule not found")
    return FraudRuleResponse.model_validate(rule)

@router.put("/rules/{rule_id}", response_model=FraudRuleResponse)
async def update_fraud_rule(
    rule_id: str,
    request: FraudRuleCreateRequest,
    db: Session = Depends(get_db)
):
    """Update fraud rule"""
    rule = db.query(FraudRule).filter(FraudRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Fraud rule not found")
    
    rule.name = request.name
    rule.description = request.description
    rule.rule_type = request.rule_type
    rule.threshold = request.threshold
    rule.priority = request.priority
    rule.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(rule)
    return FraudRuleResponse.model_validate(rule)

# Anomaly Detection Endpoints

@router.post("/anomalies", response_model=AnomalyDetectionResponse)
async def create_anomaly_detection(
    customer_id: str = Query(...),
    anomaly_type: str = Query(...),
    anomaly_score: float = Query(..., ge=0, le=100),
    description: str = Query(...),
    baseline_value: Optional[float] = Query(None),
    actual_value: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    """Log anomaly detection"""
    try:
        deviation_percentage = None
        if baseline_value and actual_value:
            deviation_percentage = ((actual_value - baseline_value) / baseline_value * 100) if baseline_value != 0 else 0
        
        anomaly = AnomalyDetection(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            anomaly_type=anomaly_type,
            anomaly_score=anomaly_score,
            description=description,
            detection_method="statistical_analysis",
            baseline_value=baseline_value,
            actual_value=actual_value,
            deviation_percentage=deviation_percentage,
            is_flagged=anomaly_score > 70,
            is_investigated=False,
            is_confirmed=False
        )
        
        db.add(anomaly)
        db.commit()
        db.refresh(anomaly)
        return AnomalyDetectionResponse.model_validate(anomaly)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating anomaly detection: {str(e)}")

@router.get("/anomalies/{customer_id}", response_model=List[AnomalyDetectionResponse])
async def get_anomalies_by_customer(
    customer_id: str,
    is_flagged: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get anomalies for a customer"""
    query = db.query(AnomalyDetection).filter(AnomalyDetection.customer_id == customer_id)
    if is_flagged is not None:
        query = query.filter(AnomalyDetection.is_flagged == is_flagged)
    anomalies = query.order_by(desc(AnomalyDetection.created_at)).offset(skip).limit(limit).all()
    return [AnomalyDetectionResponse.model_validate(a) for a in anomalies]

# Velocity Check Endpoints

@router.get("/velocity/{customer_id}", response_model=VelocityCheckResponse)
async def check_transaction_velocity(customer_id: str, db: Session = Depends(get_db)):
    """Check transaction velocity for customer"""
    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)
    twenty_four_hours_ago = now - timedelta(days=1)
    
    velocity = db.query(VelocityCheck).filter(
        and_(
            VelocityCheck.customer_id == customer_id,
            VelocityCheck.last_checked >= twenty_four_hours_ago
        )
    ).order_by(desc(VelocityCheck.last_checked)).first()
    
    if not velocity:
        # Create new velocity check
        velocity = VelocityCheck(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            account_id="",
            transaction_count_1h=0,
            transaction_count_24h=0,
            amount_sum_1h=0.0,
            amount_sum_24h=0.0,
            location_changes_24h=0,
            is_suspicious=False,
            risk_level="LOW",
            last_checked=now
        )
        db.add(velocity)
        db.commit()
        db.refresh(velocity)
    
    return VelocityCheckResponse.model_validate(velocity)

@router.post("/velocity/{customer_id}/update")
async def update_velocity_check(
    customer_id: str,
    account_id: str = Query(...),
    transaction_count_1h: int = Query(..., ge=0),
    transaction_count_24h: int = Query(..., ge=0),
    amount_sum_1h: float = Query(..., ge=0),
    amount_sum_24h: float = Query(..., ge=0),
    db: Session = Depends(get_db)
):
    """Update transaction velocity metrics"""
    velocity = db.query(VelocityCheck).filter(
        VelocityCheck.customer_id == customer_id
    ).order_by(desc(VelocityCheck.last_checked)).first()
    
    if not velocity:
        velocity = VelocityCheck(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            account_id=account_id,
            transaction_count_1h=transaction_count_1h,
            transaction_count_24h=transaction_count_24h,
            amount_sum_1h=amount_sum_1h,
            amount_sum_24h=amount_sum_24h,
            location_changes_24h=0,
            is_suspicious=transaction_count_1h > 10 or amount_sum_1h > 10000,
            risk_level="MEDIUM" if transaction_count_1h > 10 else "LOW",
            last_checked=datetime.utcnow()
        )
    else:
        velocity.account_id = account_id
        velocity.transaction_count_1h = transaction_count_1h
        velocity.transaction_count_24h = transaction_count_24h
        velocity.amount_sum_1h = amount_sum_1h
        velocity.amount_sum_24h = amount_sum_24h
        velocity.is_suspicious = transaction_count_1h > 10 or amount_sum_1h > 10000
        velocity.risk_level = "HIGH" if transaction_count_1h > 15 else ("MEDIUM" if transaction_count_1h > 10 else "LOW")
        velocity.last_checked = datetime.utcnow()
    
    db.add(velocity)
    db.commit()
    db.refresh(velocity)
    return VelocityCheckResponse.model_validate(velocity)

# Fraud Patterns Endpoints

@router.get("/patterns", response_model=List[dict])
async def get_fraud_patterns(
    days: int = Query(30, ge=1, le=365),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get identified fraud patterns"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    patterns = db.query(FraudPattern).filter(
        FraudPattern.created_at >= cutoff_date
    ).order_by(desc(FraudPattern.occurrence_count)).offset(skip).limit(limit).all()
    
    return [
        {
            "id": p.id,
            "pattern_name": p.pattern_name,
            "description": p.description,
            "occurrence_count": p.occurrence_count,
            "avg_fraud_score": p.avg_fraud_score,
            "is_active": p.is_active,
            "created_at": p.created_at
        }
        for p in patterns
    ]

# Statistics & Analytics Endpoints

@router.get("/statistics", response_model=FraudStatisticsResponse)
async def get_fraud_statistics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get fraud statistics for period"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    total_alerts = db.query(FraudAlert).filter(FraudAlert.created_at >= cutoff_date).count()
    new_alerts = db.query(FraudAlert).filter(
        and_(FraudAlert.created_at >= cutoff_date, FraudAlert.status == AlertStatus.NEW.value)
    ).count()
    confirmed_frauds = db.query(FraudAlert).filter(
        and_(FraudAlert.created_at >= cutoff_date, FraudAlert.status == AlertStatus.CONFIRMED.value)
    ).count()
    dismissed_alerts = db.query(FraudAlert).filter(
        and_(FraudAlert.created_at >= cutoff_date, FraudAlert.status == AlertStatus.DISMISSED.value)
    ).count()
    high_severity_count = db.query(FraudAlert).filter(
        and_(FraudAlert.created_at >= cutoff_date, FraudAlert.severity == AlertSeverity.HIGH.value)
    ).count()
    
    avg_fraud_score = db.query(FraudAlert).filter(FraudAlert.created_at >= cutoff_date).count()
    
    investigation_rate = (new_alerts / total_alerts * 100) if total_alerts > 0 else 0
    confirmation_rate = (confirmed_frauds / total_alerts * 100) if total_alerts > 0 else 0
    
    return FraudStatisticsResponse(
        total_alerts=total_alerts,
        new_alerts=new_alerts,
        confirmed_frauds=confirmed_frauds,
        dismissed_alerts=dismissed_alerts,
        high_severity_count=high_severity_count,
        average_fraud_score=65.0,
        investigation_rate=investigation_rate,
        confirmation_rate=confirmation_rate,
        period_start=cutoff_date,
        period_end=datetime.utcnow()
    )

@router.get("/analytics/{customer_id}", response_model=FraudAnalyticsResponse)
async def get_customer_fraud_analytics(customer_id: str, db: Session = Depends(get_db)):
    """Get fraud analytics for a specific customer"""
    alert_count = db.query(FraudAlert).filter(FraudAlert.customer_id == customer_id).count()
    confirmed_fraud_count = db.query(FraudAlert).filter(
        and_(FraudAlert.customer_id == customer_id, FraudAlert.status == AlertStatus.CONFIRMED.value)
    ).count()
    
    last_alert = db.query(FraudAlert).filter(
        FraudAlert.customer_id == customer_id
    ).order_by(desc(FraudAlert.detected_at)).first()
    
    fraud_probability = (confirmed_fraud_count / alert_count * 100) if alert_count > 0 else 0
    risk_level = "CRITICAL" if fraud_probability > 50 else ("HIGH" if fraud_probability > 25 else ("MEDIUM" if fraud_probability > 10 else "LOW"))
    
    return FraudAnalyticsResponse(
        customer_id=customer_id,
        alert_count=alert_count,
        confirmed_fraud_count=confirmed_fraud_count,
        suspicious_transactions=0,
        risk_level=risk_level,
        last_alert=last_alert.detected_at if last_alert else None,
        fraud_probability=fraud_probability
    )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "fraud-detection"}
