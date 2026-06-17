"""Auth Service - Routes and Endpoints"""
import inspect
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.database import get_db
from app.models import User, Role, Permission, Session as DBSession, AuditLog
from app.schemas import (
    LoginRequest, LoginResponse, RefreshTokenRequest, RefreshTokenResponse,
    UserRegisterRequest, UserResponse, UserDetailResponse, RoleResponse,
    AssignRoleRequest, PasswordChangeRequest, UserUpdateRequest
)
from app.auth_utils import (
    hash_password, verify_password, create_access_token, 
    create_refresh_token, decode_refresh_token
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ============ User Registration & Login ============

@router.post("/register", response_model=UserResponse, tags=["Auth"])
async def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        logger.warning(f"Registration attempt with existing email: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    hashed_pw = hash_password(request.password)
    if inspect.iscoroutine(hashed_pw):
        hashed_pw = await hashed_pw

    # Create new user
    new_user = User(
        email=request.email,
        password_hash=hashed_pw,
        first_name=request.first_name,
        last_name=request.last_name
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Log audit
        audit_log = AuditLog(
            user_id=new_user.id,
            action="USER_REGISTERED",
            resource="users",
            resource_id=new_user.id,
            status="success"
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"✅ User registered: {request.email}")
        return UserResponse.model_validate(new_user)
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post("/login", response_model=LoginResponse, tags=["Auth"])
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """User login - issue JWT tokens"""
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    
    is_valid = False
    if user:
        is_valid = verify_password(request.password, user.password_hash)
        if inspect.iscoroutine(is_valid):
            is_valid = await is_valid
            
    if not user or not is_valid:
        logger.warning(f"Failed login attempt: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        logger.warning(f"Login attempt for inactive user: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create tokens
    access_token, access_expires_in = create_access_token(
        user.id, user.email, user.roles
    )
    refresh_token, _ = create_refresh_token(user.id, user.email)
    
    # Create session in database
    db_session = DBSession(
        user_id=user.id,
        token=access_token,
        refresh_token=refresh_token,
        is_active=True,
        expires_at=datetime.utcnow().replace(microsecond=0)
    )
    
    try:
        # Update last login
        user.last_login = datetime.utcnow()
        db.add(user)
        db.add(db_session)
        
        # Audit log
        audit_log = AuditLog(
            user_id=user.id,
            action="USER_LOGIN",
            resource="auth",
            status="success"
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"✅ User logged in: {request.email}")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=access_expires_in,
            user_id=user.id,
            email=user.email
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=RefreshTokenResponse, tags=["Auth"])
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    try:
        # Validate refresh token
        payload = decode_refresh_token(request.refresh_token)
        user_id = payload.get("user_id")
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            logger.warning(f"Token refresh attempt for invalid/inactive user: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user"
            )
        
        # Create new access token
        new_access_token, access_expires_in = create_access_token(
            user.id, user.email, user.roles
        )
        
        # Update session
        session = db.query(DBSession).filter(
            DBSession.refresh_token == request.refresh_token
        ).first()
        
        if session:
            session.token = new_access_token
            session.updated_at = datetime.utcnow()
            db.add(session)
            db.commit()
        
        logger.info(f"✅ Token refreshed for user: {user_id}")
        
        return RefreshTokenResponse(
            access_token=new_access_token,
            expires_in=access_expires_in
        )
    
    except ValueError as e:
        logger.warning(f"Invalid refresh token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )


# ============ User Management ============

@router.get("/users", response_model=list[UserResponse], tags=["Users"])
async def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all registered users"""
    users = db.query(User).offset(skip).limit(limit).all()
    return [UserResponse.model_validate(user) for user in users]


@router.get("/users/{user_id}", response_model=UserDetailResponse, tags=["Users"])
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user details"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserDetailResponse.model_validate(user)


@router.put("/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def update_user(user_id: str, request: UserUpdateRequest, db: Session = Depends(get_db)):
    """Update user details"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if request.first_name is not None:
        user.first_name = request.first_name
    if request.last_name is not None:
        user.last_name = request.last_name
    if request.is_active is not None:
        user.is_active = request.is_active
        
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}", tags=["Users"])
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    """Soft delete / deactivate a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    db.commit()
    return {"message": "User successfully deactivated"}

@router.post("/change-password", tags=["Users"])
async def change_password(
    request: PasswordChangeRequest,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Change user password"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    is_valid = verify_password(request.current_password, user.password_hash)
    if inspect.iscoroutine(is_valid):
        is_valid = await is_valid
    if not is_valid:
        logger.warning(f"Failed password change attempt: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    try:
        # Update password
        new_hashed_pw = hash_password(request.new_password)
        if inspect.iscoroutine(new_hashed_pw):
            new_hashed_pw = await new_hashed_pw
        user.password_hash = new_hashed_pw
        user.updated_at = datetime.utcnow()
        
        # Audit log
        audit_log = AuditLog(
            user_id=user.id,
            action="PASSWORD_CHANGED",
            resource="users",
            resource_id=user.id,
            status="success"
        )
        db.add(user)
        db.add(audit_log)
        db.commit()
        
        logger.info(f"✅ Password changed for user: {user.email}")
        return {"message": "Password changed successfully"}
    
    except Exception as e:
        db.rollback()
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


# ============ Role Management ============

@router.get("/roles", response_model=list[RoleResponse], tags=["Roles"])
async def list_roles(db: Session = Depends(get_db)):
    """List all roles"""
    roles = db.query(Role).filter(Role.is_active == True).all()
    return [RoleResponse.model_validate(role) for role in roles]


@router.post("/roles/{user_id}", tags=["Roles"])
async def assign_role(user_id: str, request: AssignRoleRequest, db: Session = Depends(get_db)):
    """Assign role to user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    role = db.query(Role).filter(Role.id == request.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    try:
        if role not in user.roles:
            user.roles.append(role)
            
            audit_log = AuditLog(
                user_id=user.id,
                action="ROLE_ASSIGNED",
                resource="roles",
                resource_id=role.id,
                changes=f"Assigned role: {role.name}"
            )
            db.add(user)
            db.add(audit_log)
            db.commit()
            
            logger.info(f"✅ Role assigned to user: {user.email} - {role.name}")
        
        return {"message": f"Role '{role.name}' assigned successfully"}
    
    except Exception as e:
        db.rollback()
        logger.error(f"Role assignment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign role"
        )


# ============ Health Check ============

@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "auth-service",
        "timestamp": datetime.utcnow().isoformat()
    }
