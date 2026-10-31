from typing import Annotated
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import app.models
from app.database import get_db
from app.auth.schemas import UserRead, UserCreate, Token
from app.auth.dependencies import CurrentUser

from app.auth.auth import (
    create_access_token,
    verify_access_token,
    hash_password,
    verify_password,
    oauth2_scheme,
)

from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201, response_model=UserRead)
async def register(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(app.models.User).where(
            func.lower(app.models.User.username) == user.username.lower()
        )
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="User name already exists",
        )

    result = await db.execute(
        select(app.models.User).where(
            func.lower(app.models.User.email) == user.email.lower()
        ),
    )
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="Email already exists",
        )

    new_user = app.models.User(
        username=user.username,
        email=user.email.lower(),
        hashed_password=hash_password(user.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Look up user by email (case-insensitive)
    # Note: OAuth2PasswordRequestForm uses "username" field, but we treat it as email
    result = await db.execute(
        select(app.models.User).where(
            func.lower(app.models.User.email) == form_data.username.lower(),
        )
    )
    user = result.scalars().first()

    # Verify user exists and password is correct
    # Don't reveal which one failed (security best practice)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with user id as subject
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: CurrentUser):
    return current_user


"""@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(app.models.User).where(
            app.models.User.id == user_id,
        )
    )
    user = result.scalars().first()
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not found")"""
