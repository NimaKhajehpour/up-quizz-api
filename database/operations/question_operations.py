from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only

from database.model.question_model import Question
from models.requests.question_request import QuestionRequest


async def get_question_by_id(question_id: int, db: AsyncSession):
    query = (select(Question)
             .options(load_only(
        Question.id, Question.quiz_id
    )).where(Question.id == question_id))
    async with db as session:
        question = await session.execute(query)
        return question.scalars().unique().one_or_none()

async def create_question(question: Question, db: AsyncSession):
    async with db as session:
        session.add(question)
        await session.flush()
        await session.commit()

async def update_question(id: int, question: QuestionRequest, db: AsyncSession):
    query = update(Question).where(Question.id == id).values(text=question.text)
    async with db as session:
        await session.execute(query)
        await session.commit()

async def remove_question(id: int, db: AsyncSession):
    async with db as session:
        await session.execute(delete(Question).where(Question.id == id))
        await session.commit()