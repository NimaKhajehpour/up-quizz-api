import os

from fastapi import FastAPI
from sqlalchemy import select

from auth.auth import get_password_hash
from database.db import Base, engine, sessionLocal
from contextlib import asynccontextmanager
from database.dependencies import get_db
from database.model.user_model import User
from database.model.answer_model import Answer
from database.model.category_model import Category
from database.model.quiz_model import Quiz
from database.model.question_model import Question
from database.model.taken_quiz_model import TakenQuiz
from models.requests.user_create import UserCreate
from routes import signup, token, user_routes, category_routes, quiz_routes, question_routes, answer_routes, \
    taken_quiz_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with sessionLocal() as session:
        result = await session.execute(select(User).where(User.username == "adminUser"))
        existing_user = result.scalar_one_or_none()
        if not existing_user:
            user = UserCreate(
                display_name="Nima Kh",
                username=os.getenv("USERNAME"),
                about=None,
                password=get_password_hash(os.getenv("PASSWORD"))
            )
            db_user = User(**user.model_dump())
            db_user.role = "admin"
            session.add(db_user)
            await session.flush()
            await session.commit()
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(signup.router)
app.include_router(token.router)
app.include_router(user_routes.router)
app.include_router(category_routes.router)
app.include_router(quiz_routes.router)
app.include_router(question_routes.router)
app.include_router(answer_routes.router)
app.include_router(taken_quiz_routes.router)