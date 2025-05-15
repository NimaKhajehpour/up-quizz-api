from typing import Any, Coroutine, Sequence

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from database.model.user_model import User
from models.requests.user_update_request import UserUpdateRequest
from models.responses import user_profile_response


async def get_user_by_username(username: str, session: AsyncSession) -> User | None:
    query = select(User).where(User.username == username)
    async with session as session:
        user = await session.execute(query)
        return user.scalars().one_or_none()

async def register_user(user: User, session: AsyncSession):
    async with session as session:
        session.add(user)
        await session.flush()
        await session.commit()
        await session.refresh(user)

async def get_all_users(page: int, size: int, session: AsyncSession):
    skip = (page-1)*size
    total_query = select(func.count()).select_from(User)
    query = select(User).offset(skip).limit(size).options(
        load_only(
            User.id, User.username, User.role, User.display_name, User.about
        )
    )
    async with session as session:
        users = await session.execute(query)
        total_queries = await session.execute(total_query)
        total = total_queries.scalars().one()
        user = users.scalars().all()
        return {
            "total": total,
            "page": page,
            "size": size,
            "items": user,
            "pages": (total+size-1)//size
        }

async def get_user_by_id(id: int, session: AsyncSession) -> User | None:
    query = select(User).where(User.id == id)
    async with session as session:
        user = await session.execute(query)
        return user.scalars().one_or_none()

async def update_user_profile(user_id: int, user: UserUpdateRequest, session: AsyncSession):
    query = update(User).where(User.id == user_id).values(display_name=user.display_name, about=user.about)
    async with session as session:
        await session.execute(query)
        await session.commit()

async def update_user_password(user_id: int, password: str, session: AsyncSession):
    query = update(User).where(User.id == user_id).values(password=password)
    async with session as session:
        await session.execute(query)
        await session.commit()

#use with caution
async def promote_user(user_id, session: AsyncSession):
    query = update(User).where(User.id == user_id).values(role="admin")
    async with session as session:
        await session.execute(query)
        await session.commit()

async def demote_user(user_id, session: AsyncSession):
    query = update(User).where(User.id == user_id).values(role="user")
    async with session as session:
        await session.execute(query)
        await session.commit()

async def delete_user(user_id: int, session: AsyncSession):
    async with session as session:
        await session.execute(delete(User).where(User.id == user_id))
        await session.commit()
