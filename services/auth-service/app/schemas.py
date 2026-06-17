"""Auth Service - Pydantic Schemas for Request/Response"""
from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List

# Roles & Permissions (define first for forward references)
class PermissionResponse(BaseModel):
    id: str
    resource: str
    action: str
    description: Optional[str]
    
    class Config:
        from_attributes = True

class RoleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    is_active: bool
    permissions: List[PermissionResponse] = []
    
    class Config:
        from_attributes = True

# Login & Authentication
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    email: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

# User Registration
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)

class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserDetailResponse(UserResponse):
    last_login: Optional[datetime]
    email_verified_at: Optional[datetime]
    updated_at: datetime
    roles: List[RoleResponse] = []

class RoleCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None

class RoleUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class AssignRoleRequest(BaseModel):
    user_id: str
    role_id: str

# Session
class SessionResponse(BaseModel):
    id: str
    user_id: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    is_active: bool
    expires_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

# Token Payload (for JWT)
class TokenData(BaseModel):
    user_id: str
    email: str
    roles: List[str]
    permissions: List[tuple]  # List of (resource, action) tuples
    exp: int  # Expiration time

# Password Reset
class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

# Error Response
class ErrorResponse(BaseModel):
    detail: str
    error_code: str
    timestamp: datetime
