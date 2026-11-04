from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    hash_password,
    verify_password,
    verify_token_payload,
)
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    if db.scalar(select(User).where(User.email == data.email)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role or "analyst",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=str(user.id),
        email=user.email,
        role=user.role,
        created_at=user.created_at.isoformat(),
    )


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.scalar(select(User).where(User.email == data.email))

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(str(user.id), role=user.role)
    refresh_token = create_refresh_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        role=user.role,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token_route(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    payload = verify_token_payload(data.refresh_token, expected_type="refresh")
    try:
        user_id = UUID(payload["sub"])
    except (KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    new_access_token = create_access_token(str(user.id), role=user.role)
    new_refresh_token = create_refresh_token(str(user.id))

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        role=user.role,
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        role=current_user.role,
        created_at=current_user.created_at.isoformat(),
    )
