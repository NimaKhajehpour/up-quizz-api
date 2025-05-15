from sqlalchemy import Sequence, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only, joinedload

from database.model.quiz_model import Quiz
from database.model.taken_quiz_model import TakenQuiz


async def get_taken_quizzes(id: int, db: AsyncSession):
    query = select(TakenQuiz).where(TakenQuiz.user_id == id).options(load_only(
        TakenQuiz.quiz_id, TakenQuiz.correct_answers, TakenQuiz.total_answers,
    ), joinedload(
        TakenQuiz.quiz
    ).load_only(
        Quiz.title, Quiz.description,
    ))
    async with db as session:
        taken_quizzes = await session.execute(query)
        return taken_quizzes.scalars().all()

async def create_taken_quiz(taken_quiz: TakenQuiz, db: AsyncSession):
    async with db as session:
        session.add(taken_quiz)
        await session.flush()
        await session.commit()