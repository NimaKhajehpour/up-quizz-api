from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from database.model.answer_model import Answer
from models.requests.answer_request import AnswerRequest


async def create_answer(answer: Answer, db: AsyncSession):
    async with db as session:
        session.add(answer)
        await session.flush()
        await session.commit()

async def get_answer_by_id(id: int, db: AsyncSession):
    query = select(Answer).where(Answer.id == id).options(
        load_only(
            Answer.id,
            Answer.question_id
        )
    )
    async with db as session:
        answer = await session.execute(query)
        return answer.scalars().one_or_none()

async def update_answer(id: int, answer: AnswerRequest, db: AsyncSession):
    query = update(Answer).where(Answer.id == id).values(text=answer.text, isCorrect=answer.isCorrect)
    async with db as session:
        await session.execute(query)
        await session.commit()

async def delete_answer(id: int, db: AsyncSession):
    async with db as session:
        await session.execute(delete(Answer).where(Answer.id == id))
        await session.commit()