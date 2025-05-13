from typing import Any, Coroutine, Sequence

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.model.user_model import User
from models.requests.user_update_request import UserUpdateRequest


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

async def get_all_users(session: AsyncSession) -> Sequence[User]:
    query = select(User)
    async with session as session:
        users = await session.execute(query)
        return users.scalars().all()

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
