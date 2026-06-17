"""Account Service - Routes and Endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy.exc import IntegrityError, DataError
from typing import Optional
import json
import redis
import logging
import uuid

from app.database import get_db
from app.models import (
    Account, Transaction, Transfer, Statement, AuditLog,
    AccountType, AccountStatus, TransactionType, TransactionStatus
)
from app.schemas import (
    AccountCreateRequest, AccountResponse, AccountDetailResponse, AccountUpdateRequest,
    DepositRequest, WithdrawalRequest, TransferRequest,
    TransactionResponse, TransactionHistoryResponse,
    TransferResponse, StatementResponse, BalanceResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

redis_client = redis.from_url("redis://redis:6379", decode_responses=True)


def generate_account_number() -> str:
    """Generate a unique, time-ordered account number using UUIDv7 format."""
    # Standard Python's uuid module doesn't natively support uuid7() yet.
    # We construct a valid UUIDv7 using the current timestamp and uuid4 randomness.
    timestamp_ms = int(datetime.utcnow().timestamp() * 1000)
    timestamp_hex = f"{timestamp_ms:012x}"
    
    random_hex = uuid.uuid4().hex
    version = '7'
    rand_a = random_hex[:3]
    variant = hex(8 | (int(random_hex[3], 16) & 3))[2:]
    rand_b = random_hex[4:19]
    
    uuid7_str = f"{timestamp_hex[:8]}-{timestamp_hex[8:12]}-{version}{rand_a}-{variant}{rand_b[:3]}-{rand_b[3:]}"
    return f"ACC-{uuid7_str}"


# ============ Account CRUD ============

@router.post("", response_model=AccountResponse, tags=["Accounts"])
async def create_account(request: AccountCreateRequest, db: Session = Depends(get_db)):
    """Create a new account"""
    try:
        account = Account(
            customer_id=request.customer_id,
            account_number=generate_account_number(),
            account_type=AccountType(request.account_type.value),
            status=AccountStatus.ACTIVE,
            balance=request.initial_balance,
            available_balance=request.initial_balance,
            credit_limit=request.credit_limit,
            interest_rate=request.interest_rate,
            minimum_balance=request.minimum_balance
        )
        db.add(account)
        db.flush()
        
        # Create initial deposit transaction if there's an initial balance
        if request.initial_balance > 0:
            transaction = Transaction(
                account_id=account.id,
                transaction_type=TransactionType.DEPOSIT,
                status=TransactionStatus.COMPLETED,
                amount=request.initial_balance,
                balance_after=request.initial_balance,
                description="Initial deposit",
                completed_at=datetime.utcnow()
            )
            db.add(transaction)
        
        # Audit log
        audit_log = AuditLog(
            account_id=account.id,
            action="ACCOUNT_CREATED",
            resource="accounts",
            changes=f"Account Type: {request.account_type.value}, Initial Balance: {request.initial_balance}",
            status="success"
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(account)
        
        logger.info(f"✅ Account created: {account.account_number}")
        return AccountResponse.model_validate(account)
    
    except (IntegrityError, DataError) as e:
        db.rollback()
        logger.error(f"Database error during account creation: {e}")
        # The e.orig attribute often contains the specific DB-API error message
        detail_msg = f"A database error occurred. Please check the data. Details: {e.orig}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail_msg
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during account creation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected internal error occurred. Please check service logs."
        )


@router.get("/{account_id}", response_model=AccountDetailResponse, tags=["Accounts"])
async def get_account(account_id: str, db: Session = Depends(get_db)):
    """Get account details"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    return AccountDetailResponse.model_validate(account)


@router.get("/by-number/{account_number}", response_model=AccountDetailResponse, tags=["Accounts"])
async def get_account_by_number(account_number: str, db: Session = Depends(get_db)):
    """Get account by account number"""
    account = db.query(Account).filter(Account.account_number == account_number).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    return AccountDetailResponse.model_validate(account)


@router.get("/customer/{customer_id}", response_model=list[AccountResponse], tags=["Accounts"])
async def get_customer_accounts(customer_id: str, db: Session = Depends(get_db)):
    """Get all accounts for a customer"""
    accounts = db.query(Account).filter(Account.customer_id == customer_id).all()
    return [AccountResponse.model_validate(acc) for acc in accounts]


@router.put("/{account_id}", response_model=AccountResponse, tags=["Accounts"])
async def update_account(
    account_id: str,
    request: AccountUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update account details"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    try:
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(account, field, value)
        
        account.updated_at = datetime.utcnow()
        
        # Audit log
        audit_log = AuditLog(
            account_id=account.id,
            action="ACCOUNT_UPDATED",
            resource="accounts",
            changes=str(update_data),
            status="success"
        )
        
        db.add(account)
        db.add(audit_log)
        db.commit()
        db.refresh(account)
        
        logger.info(f"✅ Account updated: {account_id}")
        return AccountResponse.model_validate(account)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Account update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update account"
        )


@router.delete("/{account_id}", tags=["Accounts"])
async def close_account(account_id: str, db: Session = Depends(get_db)):
    """Close an account (soft delete)"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    try:
        account.status = AccountStatus.CLOSED
        account.closed_at = datetime.utcnow()
        account.updated_at = datetime.utcnow()
        
        # Audit log
        audit_log = AuditLog(
            account_id=account.id,
            action="ACCOUNT_CLOSED",
            resource="accounts",
            status="success"
        )
        
        db.add(account)
        db.add(audit_log)
        db.commit()
        
        logger.info(f"✅ Account closed: {account_id}")
        return {"message": "Account closed successfully"}
    
    except Exception as e:
        db.rollback()
        logger.error(f"Account closure error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to close account"
        )


# ============ Transaction Operations ============

@router.post("/{account_id}/deposit", response_model=TransactionResponse, tags=["Transactions"])
async def deposit(
    account_id: str,
    request: DepositRequest,
    db: Session = Depends(get_db)
):
    """Deposit money to account"""
    account = db.query(Account).filter(Account.id == account_id).with_for_update().first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    if account.status != AccountStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is not active"
        )
    
    try:
        new_balance = account.balance + request.amount
        
        transaction = Transaction(
            account_id=account_id,
            transaction_type=TransactionType.DEPOSIT,
            status=TransactionStatus.COMPLETED,
            amount=request.amount,
            balance_after=new_balance,
            description=request.description or "Deposit",
            reference_number=request.reference_number,
            completed_at=datetime.utcnow()
        )
        
        account.balance = new_balance
        account.available_balance = new_balance
        account.last_activity = datetime.utcnow()
        
        # Audit log
        audit_log = AuditLog(
            account_id=account_id,
            action="DEPOSIT",
            resource="transactions",
            changes=f"Deposited: {request.amount}",
            status="success"
        )
        
        db.add(transaction)
        db.add(account)
        db.add(audit_log)
        db.commit()
        db.refresh(transaction)
        
        # Invalidate cache
        redis_client.delete(f"balance:{account_id}")

        logger.info(f"✅ Deposit completed: {account_id} - ${request.amount}")
        return TransactionResponse.model_validate(transaction)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Deposit error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process deposit"
        )


@router.post("/{account_id}/withdraw", response_model=TransactionResponse, tags=["Transactions"])
async def withdraw(
    account_id: str,
    request: WithdrawalRequest,
    db: Session = Depends(get_db)
):
    """Withdraw money from account"""
    account = db.query(Account).filter(Account.id == account_id).with_for_update().first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    if account.status != AccountStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is not active"
        )
    
    if account.balance < request.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds"
        )
    
    try:
        new_balance = account.balance - request.amount
        
        transaction = Transaction(
            account_id=account_id,
            transaction_type=TransactionType.WITHDRAWAL,
            status=TransactionStatus.COMPLETED,
            amount=request.amount,
            balance_after=new_balance,
            description=request.description or "Withdrawal",
            reference_number=request.reference_number,
            completed_at=datetime.utcnow()
        )
        
        account.balance = new_balance
        account.available_balance = new_balance
        account.last_activity = datetime.utcnow()
        
        # Audit log
        audit_log = AuditLog(
            account_id=account_id,
            action="WITHDRAWAL",
            resource="transactions",
            changes=f"Withdrew: {request.amount}",
            status="success"
        )
        
        db.add(transaction)
        db.add(account)
        db.add(audit_log)
        db.commit()
        db.refresh(transaction)
        
        # Invalidate cache
        redis_client.delete(f"balance:{account_id}")

        logger.info(f"✅ Withdrawal completed: {account_id} - ${request.amount}")
        return TransactionResponse.model_validate(transaction)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Withdrawal error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process withdrawal"
        )


@router.post("/transfer", response_model=TransferResponse, tags=["Transactions"])
async def transfer_money(
    request: TransferRequest,
    db: Session = Depends(get_db)
):
    """Transfer money between accounts"""
    from_account = db.query(Account).filter(Account.id == request.from_account_id).with_for_update().first()
    if not from_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source account not found"
        )
    
    to_account = db.query(Account).filter(Account.id == request.to_account_id).with_for_update().first()
    if not to_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination account not found"
        )
    
    if from_account.status != AccountStatus.ACTIVE or to_account.status != AccountStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or both accounts are not active"
        )
    
    if from_account.balance < request.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds in source account"
        )
    
    try:
        # Debit from account
        from_balance = from_account.balance - request.amount
        from_txn = Transaction(
            account_id=request.from_account_id,
            transaction_type=TransactionType.TRANSFER,
            status=TransactionStatus.COMPLETED,
            amount=request.amount,
            balance_after=from_balance,
            counterparty_account=to_account.account_number,
            description=request.description or "Transfer out",
            completed_at=datetime.utcnow()
        )
        
        # Credit to account
        to_balance = to_account.balance + request.amount
        to_txn = Transaction(
            account_id=request.to_account_id,
            transaction_type=TransactionType.TRANSFER,
            status=TransactionStatus.COMPLETED,
            amount=request.amount,
            balance_after=to_balance,
            counterparty_account=from_account.account_number,
            description=request.description or "Transfer in",
            completed_at=datetime.utcnow()
        )
        
        # Update balances
        from_account.balance = from_balance
        from_account.available_balance = from_balance
        from_account.last_activity = datetime.utcnow()
        
        to_account.balance = to_balance
        to_account.available_balance = to_balance
        to_account.last_activity = datetime.utcnow()
        
        db.add_all([from_txn, to_txn, from_account, to_account])
        db.flush()
        
        # Audit logs
        audit_from = AuditLog(
            account_id=request.from_account_id,
            action="TRANSFER_OUT",
            resource="transfers",
            changes=f"Transferred: {request.amount} to {to_account.account_number}",
            status="success"
        )
        
        audit_to = AuditLog(
            account_id=request.to_account_id,
            action="TRANSFER_IN",
            resource="transfers",
            changes=f"Received: {request.amount} from {from_account.account_number}",
            status="success"
        )
        
        transfer = Transfer(
            from_account_id=request.from_account_id,
            to_account_id=request.to_account_id,
            amount=request.amount,
            status=TransactionStatus.COMPLETED,
            description=request.description,
            from_transaction_id=from_txn.id,
            to_transaction_id=to_txn.id,
            completed_at=datetime.utcnow()
        )

        db.add_all([transfer, audit_from, audit_to])
        db.commit()
        db.refresh(transfer)
        
        # Invalidate cache
        redis_client.delete(f"balance:{request.from_account_id}")
        redis_client.delete(f"balance:{request.to_account_id}")

        logger.info(f"✅ Transfer completed: {request.from_account_id} → {request.to_account_id} - ${request.amount}")
        return TransferResponse.model_validate(transfer)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Transfer error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process transfer"
        )


@router.get("/{account_id}/transactions", response_model=TransactionHistoryResponse, tags=["Transactions"])
async def get_transactions(
    account_id: str,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get transaction history for account"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    transactions = db.query(Transaction).filter(
        Transaction.account_id == account_id
    ).order_by(Transaction.created_at.desc()).offset(offset).limit(limit).all()
    
    total_count = db.query(Transaction).filter(
        Transaction.account_id == account_id
    ).count()
    
    return TransactionHistoryResponse(
        account_id=account_id,
        total_count=total_count,
        transactions=[TransactionResponse.model_validate(txn) for txn in transactions]
    )


@router.get("/{account_id}/balance", response_model=BalanceResponse, tags=["Accounts"])
async def get_balance(account_id: str, db: Session = Depends(get_db)):
    """Get current account balance"""
    cache_key = f"balance:{account_id}"
    cached_balance = redis_client.get(cache_key)
    if cached_balance:
        return json.loads(cached_balance)

    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    used_credit = None
    if account.credit_limit:
        used_credit = max(0, account.credit_limit - account.available_balance)
    
    response_data = {
        "account_id": account_id,
        "current_balance": account.balance,
        "available_balance": account.available_balance,
        "credit_limit": account.credit_limit,
        "used_credit": used_credit,
        "last_updated": (account.updated_at or account.created_at).isoformat()
    }

    # Cache for 60 seconds
    redis_client.setex(cache_key, 60, json.dumps(response_data))

    return response_data


# ============ Statements ============

@router.get("/{account_id}/statement", response_model=StatementResponse, tags=["Statements"])
async def get_latest_statement(account_id: str, db: Session = Depends(get_db)):
    """Get latest account statement"""
    statement = db.query(Statement).filter(
        Statement.account_id == account_id
    ).order_by(Statement.generated_at.desc()).first()
    
    if not statement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No statements found for this account"
        )
    
    return StatementResponse.model_validate(statement)


# ============ Health Check ============

@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "account-service",
        "timestamp": datetime.utcnow().isoformat()
    }
