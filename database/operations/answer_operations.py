from fastapi import HTTPException
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from database.model.answer_model import Answer
from database.model.question_model import Question
from database.model.quiz_model import Quiz
from models.requests.answer_request import AnswerRequest


async def create_answer(answer: Answer, db: AsyncSession):
    async with db as session:
        session.add(answer)
        await session.flush()
        await session.commit()

async def bulk_add_answers(user_id: int, answers: list[AnswerRequest], db: AsyncSession):
    question_ids = {a.question_id for a in answers}

    # Step 1: Fetch allowed question_ids
    stmt = (
        select(Question.id)
        .join(Quiz)
        .where(
            Question.id.in_(question_ids),
            Quiz.user_id == user_id
        )
    )
    result = await db.execute(stmt)
    allowed_question_ids = {row[0] for row in result.all()}

    # Step 2: Filter answers
    valid_answers = [
        Answer(**a.model_dump()) for a in answers if a.question_id in allowed_question_ids
    ]

    # Optional: Raise error if invalid
    invalid_ids = question_ids - allowed_question_ids
    if invalid_ids:
        raise HTTPException(
            status_code=403,
            detail=f"You don't have access to question IDs: {invalid_ids}"
        )

    # Step 3: Bulk add
    db.add_all(valid_answers)
    await db.commit()

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

async def bulk_delete_answers(user_id: int, id: list[int], db: AsyncSession):
    async with db as session:
        subquery = (
            select(Answer.id)
            .join(Question, Answer.question_id == Question.id)
            .join(Quiz, Question.quiz_id == Quiz.id)
            .where(
                Answer.id.in_(id),
                Quiz.user_id == user_id
            )
        )

        # Delete only answers in that subquery
        stmt = delete(Answer).where(Answer.id.in_(subquery))
        await session.execute(stmt)
        await session.commit()