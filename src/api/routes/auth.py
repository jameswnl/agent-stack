"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user
from src.api.models import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from src.auth.jwt import create_access_token
from src.auth.password import verify_password
from src.db.crud import create_user, get_user_by_email
from src.db.database import get_db
from src.db.models import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(request: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Register a user and return an access token."""
    if get_user_by_email(db, request.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    user = create_user(
        db=db,
        email=request.email,
        password=request.password,
        full_name=request.full_name,
    )
    token = create_access_token({"sub": user.email, "user_id": user.id})
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login_user(request: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Authenticate a user and return an access token."""
    user = get_user_by_email(db, request.email)
    if user is None or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token({"sub": user.email, "user_id": user.id})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return the authenticated user."""
    return _to_user_response(current_user)
