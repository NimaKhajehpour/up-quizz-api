from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from auth.auth import verify_password, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from database.dependencies import get_db
from database.model.user_model import User
from database.operations import user_operations
from models.requests.login_request import LoginRequest

router = APIRouter(
    tags=["token"],
)

@router.post("/token")
async def login_for_access_token(form_data: LoginRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await user_operations.get_user_by_username(form_data.username, db)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}