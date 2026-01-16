from fastapi import APIRouter, HTTPException, status, Depends
from app.models import LoginRequest, SignupRequest, AuthResponse, User, ErrorResponse
from app.database import db
from app.auth import create_access_token, get_current_user_id
from datetime import timedelta

router = APIRouter()


@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def login(login_request: LoginRequest):
    """User login endpoint"""
    user = db.get_user_by_email(login_request.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not db.verify_password(login_request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user["id"])}, expires_delta=access_token_expires
    )
    
    return AuthResponse(
        success=True,
        user=User(
            id=user["id"],
            username=user["username"],
            email=user["email"]
        ),
        token=access_token
    )


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(signup_request: SignupRequest):
    """User registration endpoint"""
    # Check if email already exists
    if db.email_exists(signup_request.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )
    
    # Check if username already exists
    if db.username_exists(signup_request.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    
    # Create user
    user_id = db.create_user(
        username=signup_request.username,
        email=signup_request.email,
        password=signup_request.password
    )
    
    user = db.get_user_by_id(user_id)
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user_id)}, expires_delta=access_token_expires
    )
    
    return AuthResponse(
        success=True,
        user=User(
            id=user["id"],
            username=user["username"],
            email=user["email"]
        ),
        token=access_token
    )


@router.post("/logout", response_model=dict, status_code=status.HTTP_200_OK)
async def logout():
    """User logout endpoint"""
    # In a real implementation, you might want to blacklist the token
    # For now, we just return success
    return {"success": True}


@router.get("/me", response_model=User, status_code=status.HTTP_200_OK)
async def get_current_user(user_id: int = Depends(get_current_user_id)):
    """Get current authenticated user"""
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return User(
        id=user["id"],
        username=user["username"],
        email=user["email"]
    )

