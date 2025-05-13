from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from auth.auth import get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from database.dependencies import get_db
from database.model.user_model import User
from database.operations import user_operations
from database.operations.user_operations import get_user_by_username
from models.requests.user_create import UserCreate

router = APIRouter(
    tags=["signup"],
)

@router.post("/register")
async def register_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    existing_user = await user_operations.get_user_by_username(user.username, db)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = get_password_hash(user.password)
    new_user = User(
        **user.model_dump()
    )
    new_user.password = hashed_password
    await user_operations.register_user(new_user, db)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data = {"sub": new_user.username}, expires_delta = access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}