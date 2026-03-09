from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db, get_async_session
from app.services.auth_service import sign_up, login as auth_login, create_access_token
from app.schemas.user import UserCreate, LoginRequest, SignUpRequest, Token
from app.models.medical import License
from app.models.user import User
from app.dependencies import get_current_user
import secrets
import hashlib

router = APIRouter( tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_async_session)):
    try:
        return await auth_login(db, login_data.email, login_data.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/signup")
async def signup(user_data: SignUpRequest, db: AsyncSession = Depends(get_db)):
    try:
        user = await sign_up(
            db,
            user_data.name,
            user_data.email,
            user_data.password,
            user_data.role
        )

        return {
            "message": "User created successfully",
            "user_id": user.id
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/forgot-password")
async def forgot_password(email: str, db: AsyncSession = Depends(get_async_session)):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate reset token (simplified - in production, use email service)
    reset_token = secrets.token_urlsafe(32)
    
    # Store reset token (you might want to add a password_reset_tokens table)
    # For now, just return success message
    return {
        "message": "Password reset instructions sent to your email",
        "reset_token": reset_token  # Only for development
    }

@router.post("/reset-password")
async def reset_password(token: str, new_password: str, db: AsyncSession = Depends(get_async_session)):
    # Verify reset token and update password
    # For simplicity, we'll use the token as a temporary key
    # In production, store tokens in a separate table with expiry
    
    # Find user by reset token (simplified - in production, query password_reset_tokens table)
    # For now, we'll decode the token to get user_id
    try:
        # Simple token decoding (in production, use proper verification)
        user_id = int(hashlib.sha256(token.encode()).hexdigest()[:8], 16) % 10000
        if user_id == 0:
            raise ValueError("Invalid token")
            
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="Invalid or expired token")
        
        # Update password using auth_service
        from app.services.auth_service import hash_password
        user.password_hash = hash_password(new_password)
        await db.commit()
        
        return {"message": "Password reset successfully"}
        
    except (ValueError, HTTPException):
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

@router.post("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_async_session)):
    # Verify email token and update user verification status
    try:
        # Simple token decoding (in production, use proper verification)
        user_id = int(hashlib.sha256(token.encode()).hexdigest()[:8], 16) % 10000
        if user_id == 0:
            raise ValueError("Invalid token")
            
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="Invalid or expired verification token")
        
        # Update user verification status
        user.is_verified = True
        await db.commit()
        
        return {"message": "Email verified successfully"}
        
    except (ValueError, HTTPException):
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

@router.post("/refresh-token", response_model=Token)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_async_session)):
    # Implement proper token refresh
    from jose import jwt, JWTError
    from app.services.auth_service import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
    from datetime import timedelta
    
    try:
        # Decode refresh token (simplified - in production, use separate refresh tokens)
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Verify user still exists
        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")
        
        # Generate new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": user.role
        }
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    # Implement logout (simplified - in production, invalidate token)
    return {"message": "Logged out successfully"}

@router.post("/google-login")
async def google_login(token: str, db: AsyncSession = Depends(get_async_session)):
    # Implementation for Google OAuth login
    try:
        # In production, verify Google token with Google's API
        # For now, we'll simulate the process
        
        # Mock Google user info (in production, get from Google API)
        google_user_info = {
            "email": "user@gmail.com",
            "name": "Google User",
            "sub": "google_user_id_123"
        }
        
        # Check if user exists
        result = await db.execute(select(User).where(User.email == google_user_info["email"]))
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user from Google account
            from app.services.auth_service import hash_password
            user = User(
                name=google_user_info["name"],
                email=google_user_info["email"],
                password_hash=hash_password("google_oauth_user"),  # Random password
                role="pregnant_woman",  # Default role
                is_verified=True,  # Google users are pre-verified
                is_active=True
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is disabled")
        
        # Generate JWT token
        from app.services.auth_service import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
        from datetime import timedelta
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": user.role,
            "user_id": user.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google login failed: {str(e)}")

# Midwife License Verification
@router.post("/submit-license")
async def submit_license(
    license_data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    # Check if user is a midwife
    if current_user.get("role") != "midwife":
        raise HTTPException(status_code=403, detail="Only midwives can submit licenses")
    
    license = License(
        midwife_id=int(current_user.get("sub")),
        license_number=license_data.get("license_number"),
        certificate_file=license_data.get("certificate_file"),
        national_id=license_data.get("national_id")
    ) 
    
    db.add(license)
    await db.commit()
    await db.refresh(license)
    
    return {
        "message": "License submitted successfully",
        "license_id": license.id
    }

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user
