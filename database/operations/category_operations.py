from typing import Any, Coroutine, Sequence

from sqlalchemy import select, Row, RowMapping, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only

from database.model.category_model import Category
from models.requests.category_request import CategoryRequest


async def get_approved_categories(db: AsyncSession):
    query = select(Category).where(Category.approved == True).options(
        load_only(
            Category.id, Category.name, Category.description, Category.approved
        )
    )
    async with db as session:
        categories = await session.execute(query)
        return categories.scalars().all()

async def get_all_categories(db: AsyncSession):
    query = select(Category).options(
        load_only(Category.id, Category.name, Category.description, Category.approved))
    async with db as session:
        categories = await session.execute(query)
        return categories.scalars().all()

async def create_category(category: Category, db: AsyncSession):
    async with db as session:
        session.add(category)
        await session.flush()
        await session.commit()

async def get_category_by_name(name: str, db: AsyncSession):
    query = select(Category).where(Category.name == name).options(
        load_only(Category.id)
    )
    async with db as session:
        category = await session.execute(query)
        return category.scalars().one_or_none()

async def search_approved_categories(query: str, db: AsyncSession):
    query = (select(Category)
             .where((Category.approved == True) & (Category.name.like(f'%{query}%') | Category.description.like(f'%{query}%')))
            .options(
                load_only(
                    Category.id, Category.name, Category.description, Category.approved
                )))
    async with db as session:
        categories = await session.execute(query)
        return categories.scalars().all()

async def search_all_categories(query: str, db: AsyncSession):
    query = (select(Category)
             .where((Category.name.like(f'%{query}%') | Category.description.like(f'%{query}%')))
            .options(
                load_only(
                    Category.id, Category.name, Category.description, Category.approved
                )))
    async with db as session:
        categories = await session.execute(query)
        return categories.scalars().all()

async def get_category_by_id(id: int, db: AsyncSession):
    query = (select(Category).where(Category.id == id)
            .options(
                load_only(
                    Category.id, Category.name, Category.description, Category.approved
                )))
    async with db as session:
        category = await session.execute(query)
        return category.scalars().one_or_none()

async def approve_category(id: int, approved: bool, db: AsyncSession):
    query = update(Category).where(Category.id == id).values(approved=approved)
    async with db as session:
        await session.execute(query)
        await session.commit()

async def update_category(id: int, category: CategoryRequest, db: AsyncSession):
    query = update(Category).where(Category.id == id).values(name=category.name, description=category.description)
    async with db as session:
        await session.execute(query)
        await session.commit()

async def remove_category(id: int, db: AsyncSession):
    async with db as session:
        await session.execute(delete(Category).where(Category.id == id))
        await session.commit()
