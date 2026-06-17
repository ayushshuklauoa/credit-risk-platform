"""Account Service Database Models - Accounts and Transactions"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

Base = declarative_base()


class AccountType(str, enum.Enum):
    """Account Type"""
    CHECKING = "checking"
    SAVINGS = "savings"
    MONEY_MARKET = "money_market"
    LINE_OF_CREDIT = "line_of_credit"


class AccountStatus(str, enum.Enum):
    """Account Status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FROZEN = "frozen"
    CLOSED = "closed"
    SUSPENDED = "suspended"


class TransactionType(str, enum.Enum):
    """Transaction Type"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    FEE = "fee"
    INTEREST = "interest"


class TransactionStatus(str, enum.Enum):
    """Transaction Status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"


class Account(Base):
    """Account model"""
    __tablename__ = "accounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), nullable=False, index=True)  # Reference to customer service
    account_number = Column(String(50), unique=True, nullable=False, index=True)
    account_type = Column(Enum(AccountType), nullable=False)
    status = Column(Enum(AccountStatus), default=AccountStatus.ACTIVE)
    
    # Balance & Limits
    balance = Column(Float, default=0.0)
    credit_limit = Column(Float, nullable=True)
    available_balance = Column(Float, default=0.0)
    
    # Interest & Fees
    interest_rate = Column(Float, default=0.0)
    annual_percentage_rate = Column(Float, nullable=True)
    minimum_balance = Column(Float, default=0.0)
    monthly_fee = Column(Float, default=0.0)
    
    # Dates
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Account(id={self.id}, account_number={self.account_number})>"


class Transaction(Base):
    """Transaction model"""
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(36), ForeignKey('accounts.id'), nullable=False, index=True)
    
    # Transaction Details
    transaction_type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    amount = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    
    # Counterparty
    counterparty_account = Column(String(50), nullable=True)
    counterparty_name = Column(String(255), nullable=True)
    
    # Description & Reference
    description = Column(String(255), nullable=True)
    reference_number = Column(String(100), nullable=True, index=True)
    merchant_category = Column(String(100), nullable=True)
    
    # Fees
    transaction_fee = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    account = relationship("Account", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(id={self.id}, type={self.transaction_type}, amount={self.amount})>"


class Transfer(Base):
    """Transfer model for inter-account transfers"""
    __tablename__ = "transfers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Source & Destination
    from_account_id = Column(String(36), nullable=False, index=True)
    to_account_id = Column(String(36), nullable=False, index=True)
    
    # Transfer Details
    amount = Column(Float, nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    description = Column(String(255), nullable=True)
    
    # Related Transactions
    from_transaction_id = Column(String(36), nullable=True)
    to_transaction_id = Column(String(36), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Transfer(id={self.id}, amount={self.amount})>"


class Statement(Base):
    """Account statement model"""
    __tablename__ = "statements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(36), ForeignKey('accounts.id'), nullable=False, index=True)
    
    # Statement Period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Balances
    opening_balance = Column(Float, nullable=False)
    closing_balance = Column(Float, nullable=False)
    total_deposits = Column(Float, default=0.0)
    total_withdrawals = Column(Float, default=0.0)
    total_fees = Column(Float, default=0.0)
    total_interest = Column(Float, default=0.0)
    
    # Statement Info
    file_path = Column(String(500), nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Statement(account_id={self.account_id}, period={self.period_start} - {self.period_end})>"


class AuditLog(Base):
    """Audit log for account service actions"""
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(36), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=False)
    changes = Column(String(1000), nullable=True)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog(account_id={self.account_id}, action={self.action})>"
