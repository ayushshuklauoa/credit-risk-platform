"""Account Service - Pydantic Schemas"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

# Enums
class AccountTypeEnum(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    MONEY_MARKET = "money_market"
    LINE_OF_CREDIT = "line_of_credit"

class AccountStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FROZEN = "frozen"
    CLOSED = "closed"
    SUSPENDED = "suspended"

class TransactionTypeEnum(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    FEE = "fee"
    INTEREST = "interest"

class TransactionStatusEnum(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"

# Account Schemas
class AccountCreateRequest(BaseModel):
    customer_id: str
    account_type: AccountTypeEnum
    initial_balance: float = Field(default=0.0, ge=0)
    credit_limit: Optional[float] = None
    interest_rate: float = Field(default=0.0, ge=0)
    minimum_balance: float = Field(default=0.0, ge=0)

class AccountResponse(BaseModel):
    id: str
    customer_id: str
    account_number: str
    account_type: AccountTypeEnum
    status: AccountStatusEnum
    balance: float
    available_balance: float
    credit_limit: Optional[float]
    interest_rate: float
    opened_at: datetime
    last_activity: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AccountDetailResponse(AccountResponse):
    annual_percentage_rate: Optional[float]
    minimum_balance: float
    monthly_fee: float
    closed_at: Optional[datetime]
    updated_at: datetime

class AccountUpdateRequest(BaseModel):
    status: Optional[AccountStatusEnum] = None
    credit_limit: Optional[float] = None
    interest_rate: Optional[float] = None
    minimum_balance: Optional[float] = None
    monthly_fee: Optional[float] = None

class DepositRequest(BaseModel):
    amount: float = Field(..., gt=0)
    description: Optional[str] = None
    reference_number: Optional[str] = None

class WithdrawalRequest(BaseModel):
    amount: float = Field(..., gt=0)
    description: Optional[str] = None
    reference_number: Optional[str] = None

class TransferRequest(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: float = Field(..., gt=0)
    description: Optional[str] = None

class TransactionResponse(BaseModel):
    id: str
    account_id: str
    transaction_type: TransactionTypeEnum
    status: TransactionStatusEnum
    amount: float
    balance_after: float
    transaction_fee: float
    description: Optional[str]
    reference_number: Optional[str]
    merchant_category: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class TransactionDetailResponse(TransactionResponse):
    counterparty_account: Optional[str]
    counterparty_name: Optional[str]
    updated_at: datetime

class TransactionHistoryResponse(BaseModel):
    account_id: str
    total_count: int
    transactions: List[TransactionResponse]

class TransferResponse(BaseModel):
    id: str
    from_account_id: str
    to_account_id: str
    amount: float
    status: TransactionStatusEnum
    description: Optional[str]
    from_transaction_id: Optional[str]
    to_transaction_id: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class StatementResponse(BaseModel):
    id: str
    account_id: str
    period_start: datetime
    period_end: datetime
    opening_balance: float
    closing_balance: float
    total_deposits: float
    total_withdrawals: float
    total_fees: float
    total_interest: float
    file_path: Optional[str]
    generated_at: datetime
    
    class Config:
        from_attributes = True

class BalanceResponse(BaseModel):
    account_id: str
    current_balance: float
    available_balance: float
    credit_limit: Optional[float]
    used_credit: Optional[float]
    last_updated: datetime
