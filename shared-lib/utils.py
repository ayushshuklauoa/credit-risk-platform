"""
Shared utility functions
"""
import re
import hashlib
import uuid
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def sanitize_string(value: str, max_length: int = 1000) -> str:
    """Sanitize string to prevent XSS"""
    if not isinstance(value, str):
        return value
    
    value = value[:max_length]
    value = re.sub(r'[<>\"\'&]', '', value)
    return value.strip()

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    pattern = r'^[\d\-\+\(\)\s]{10,}$'
    return re.match(pattern, phone) is not None

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed

def generate_uuid7_str() -> str:
    """
    Generate a unique, time-ordered UUID version 7 string.
    This is a backport since uuid.uuid7() is not available in all Python versions.
    """
    timestamp_ms = int(datetime.utcnow().timestamp() * 1000)
    timestamp_hex = f"{timestamp_ms:012x}"
    
    random_hex = uuid.uuid4().hex
    # Construct a UUIDv7-like string. It's time-sortable and highly unique.
    version = '7'
    rand_a = random_hex[:3]
    variant = hex(8 | (int(random_hex[3], 16) & 3))[2:] # Set variant to RFC 4122
    rand_b = random_hex[4:19]
    
    return f"{timestamp_hex[:8]}-{timestamp_hex[8:12]}-{version}{rand_a}-{variant}{rand_b[:3]}-{rand_b[3:]}"

def generate_customer_id() -> str:
    """Generate unique customer ID"""
    import uuid
    return f"CUST_{uuid.uuid4().hex[:12].upper()}"
    return f"CUST-{generate_uuid7_str()}"

def generate_account_id() -> str:
    """Generate unique account ID"""
    import uuid
    return f"ACC_{uuid.uuid4().hex[:12].upper()}"

def generate_transaction_id() -> str:
    """Generate unique transaction ID"""
    import uuid
    return f"TXN_{uuid.uuid4().hex[:12].upper()}"
    return f"TXN-{generate_uuid7_str()}"
