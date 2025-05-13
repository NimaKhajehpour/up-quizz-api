from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.openapi.utils import status_code_ranges
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette import status

from auth.auth import oauth2_scheme, decode_access_token
from database.dependencies import get_db
from database.model.category_model import Category
from database.operations import category_operations
from models.requests.category_request import CategoryRequest
from models.responses import category_response

router = APIRouter(
    prefix="/category",
    tags=["category"]
)

@router.get("", response_model=list[category_response.Category])
async def get_categories(db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    categories = None
    if user.role != "admin":
        categories = await category_operations.get_approved_categories(db)
    else:
        categories = await category_operations.get_all_categories(db)
    return categories

@router.get("/search", response_model=list[category_response.Category])
async def search_categories(query: str, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    categories = None
    if user.role != "admin":
        categories = await category_operations.search_approved_categories(query, db)
    else:
        categories = await category_operations.search_all_categories(query, db)
    return categories

@router.get("/{id}", response_model=category_response.Category)
async def get_category(id: int, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    category = await category_operations.get_category_by_id(id, db)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if not category.approved and user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to perform this action")
    return category

@router.post("", status_code=status.HTTP_204_NO_CONTENT)
async def create_category(category: CategoryRequest, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    category_exists = await category_operations.get_category_by_name(category.name, db)
    if category_exists:
        raise HTTPException(status_code=400, detail="Category already exists")
    db_category = Category(**category.model_dump())
    db_category.approved = False
    await category_operations.create_category(db_category, db)


@router.put("/approve/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def approve_category(id: int, approved: bool, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to perform this action")
    db_category = await category_operations.get_category_by_id(id, db)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category does not exist")
    await category_operations.approve_category(id, approved, db)

@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_category(id: int, category: CategoryRequest, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to perform this action")
    db_category = await category_operations.get_category_by_id(id, db)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category does not exist")
    category_name = await category_operations.get_category_by_name(category.name, db)
    if category_name:
        raise HTTPException(status_code=400, detail="Cant use this name. Name already exists")
    await category_operations.update_category(id, category, db)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_category(id: int, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to perform this action")
    category = category_operations.get_category_by_id(id, db)
    if not category:
        raise HTTPException(status_code=404, detail="Category does not exist")
    await category_operations.remove_category(id, db)