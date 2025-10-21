"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta

from ..db.session import get_db
from ..db.models import User
from ..db.schemas import LoginRequest, LoginResponse, UserResponse
from ..utils.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from ..utils.logger import logger

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token
    """
    # Find user
    user = db.query(User).filter(User.username == request.username).first()
    
    if not user:
        logger.warning(f"Login attempt with non-existent username: {request.username}")
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Verify password
    if not verify_password(request.password, user.password_hash):
        logger.warning(f"Failed login attempt for user: {request.username}")
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"Login attempt for inactive user: {request.username}")
        raise HTTPException(status_code=401, detail="User account is inactive")
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    logger.info(f"User logged in: {user.username} (role: {user.role})")
    
    # Return token and user info
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            username=user.username,
            role=user.role,
            created_at=user.created_at,
            is_active=user.is_active
        )
    )
