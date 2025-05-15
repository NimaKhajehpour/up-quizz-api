from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from auth.auth import oauth2_scheme, decode_access_token, get_password_hash, verify_password
from database.dependencies import get_db
from database.model.user_model import User
from database.operations import user_operations
from models.requests.password_update_request import PasswordUpdateRequest
from models.requests.user_update_request import UserUpdateRequest
from models.responses.user_profile_response import UserProfile

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@router.get("", response_model=UserProfile)
async def get_user_profile(db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    return user

@router.get("/users")
async def get_all_users(db: Annotated[AsyncSession, Depends(get_db)], page: int = Query(1, ge=1),
                        size: int = Query(10, ge=1, le=100), token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    users = await user_operations.get_all_users(page, size, db)
    return users

@router.get("/users/{user_id}", response_model=UserProfile)
async def get_user_by_id(user_id: int, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    db_user = await user_operations.get_user_by_id(user_id, db)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("", status_code=204)
async def edit_user_profile(user_update: UserUpdateRequest, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    await user_operations.update_user_profile(user.id, user_update, db)

@router.put("/change_password", status_code=204)
async def change_password(password: PasswordUpdateRequest, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    if not verify_password(password.current_password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    if verify_password(password.new_password, user.password):
        raise HTTPException(status_code=400, detail="use a different password")
    await user_operations.update_user_password(user.id, get_password_hash(password.new_password), db)

@router.put("/promote/{id}", status_code=204)
async def promote_user(id: int, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not allowed to do that")
    db_user = await user_operations.get_user_by_id(id, db)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    await user_operations.promote_user(id, db)

@router.put("/demote/{id}", status_code=204)
async def demote_user(id: int, db: Annotated[AsyncSession, Depends(get_db)],  token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not allowed to do that")
    db_user = await user_operations.get_user_by_id(id, db)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    await user_operations.demote_user(id, db)

@router.delete("", status_code=204)
async def delete_account(db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    await user_operations.delete_user(user.id, db)