from sqlalchemy import select, Sequence, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.model.question_model import Question
from database.model.quiz_model import Quiz
from models.requests.quiz_request import QuizRequest


async def get_quiz_by_id(id: int, db: AsyncSession) -> Quiz | None:
    query = (select(Quiz).options(joinedload(Quiz.questions).joinedload(Question.answers), joinedload(Quiz.category), joinedload(Quiz.user))
             .where(Quiz.id == id))
    async with db as session:
        quiz = await session.execute(query)
        return quiz.scalars().unique().one_or_none()

async def get_all_quizzes(page: int, size: int, db: AsyncSession):
    skip = (page-1)*size
    total_query = select(func.count()).select_from(Quiz)
    query = select(Quiz).offset(skip).limit(size).options(joinedload(Quiz.questions).joinedload(Question.answers), joinedload(Quiz.category), joinedload(Quiz.user))
    async with db as session:
        quizzes = await session.execute(query)
        total_queries = await session.execute(total_query)
        total = total_queries.scalars().one()
        quiz = quizzes.scalars().all()
        return {
            "total": total,
            "page": page,
            "size": size,
            "items": quiz,
            "pages": (total+size-1)//size
        }

async def get_all_approved_quizzes(page: int, size: int, db: AsyncSession):
    skip = (page-1)*size
    total_query = select(func.count()).select_from(Quiz)
    query = (select(Quiz).offset(skip).limit(size)
             .options(joinedload(Quiz.questions).joinedload(Question.answers), joinedload(Quiz.category), joinedload(Quiz.user))
             .where(Quiz.approved == True))
    async with db as session:
        quizzes = await session.execute(query)
        total_queries = await session.execute(total_query)
        total = total_queries.scalars().one()
        quiz = quizzes.scalars().all()
        return {
            "total": total,
            "page": page,
            "size": size,
            "items": quiz,
            "pages": (total+size-1)//size
        }

async def get_unapproved_quizzes(page: int, size: int, db: AsyncSession):
    skip = (page-1)*size
    total_query = select(func.count()).select_from(Quiz)
    query = (select(Quiz).offset(skip).limit(size)
             .options(joinedload(Quiz.questions).joinedload(Question.answers), joinedload(Quiz.category), joinedload(Quiz.user))
             .where(Quiz.approved == False))
    async with db as session:
        quizzes = await session.execute(query)
        total_queries = await session.execute(total_query)
        total = total_queries.scalars().one()
        quiz = quizzes.scalars().all()
        return {
            "total": total,
            "page": page,
            "size": size,
            "items": quiz,
            "pages": (total+size-1)//size
        }

async def get_all_user_quizzes(id: int, db: AsyncSession) -> Sequence[Quiz]:
    query = (select(Quiz).
             options(joinedload(Quiz.questions).joinedload(Question.answers), joinedload(Quiz.user), joinedload(Quiz.category))
             .where(Quiz.user_id == id))
    async with db as session:
        quizzes = await session.execute(query)
        return quizzes.scalars().unique().all()

async def search_quizzes(query: str, page: int, size: int, db: AsyncSession):
    skip = (page-1)*size
    total_query = select(func.count()).select_from(Quiz)
    query = (select(Quiz).offset(skip).limit(size).options(joinedload(Quiz.questions).joinedload(Question.answers), joinedload(Quiz.category), joinedload(Quiz.user))
             .where(Quiz.title.like(f'%{query}%')))
    async with db as session:
        quizzes = await session.execute(query)
        total_queries = await session.execute(total_query)
        total = total_queries.scalars().one()
        quiz = quizzes.scalars().all()
        return {
            "total": total,
            "page": page,
            "size": size,
            "items": quiz,
            "pages": (total+size-1)//size
        }

async def search_approved_quizzes(query: str, page: int, size: int, db: AsyncSession):
    skip = (page-1)*size
    total_query = select(func.count()).select_from(Quiz)
    query = (select(Quiz).offset(skip).limit(size).options(joinedload(Quiz.questions).joinedload(Question.answers), joinedload(Quiz.category), joinedload(Quiz.user))
             .where((Quiz.approved == True) & Quiz.title.like(f'%{query}%')))
    async with db as session:
        quizzes = await session.execute(query)
        total_queries = await session.execute(total_query)
        total = total_queries.scalars().one()
        quiz = quizzes.scalars().all()
        return {
            "total": total,
            "page": page,
            "size": size,
            "items": quiz,
            "pages": (total+size-1)//size
        }

async def get_quizzes_by_category(id: int, page: int, size: int, db: AsyncSession):
    skip = (page-1)*size
    total_query = select(func.count()).select_from(Quiz)
    query = (select(Quiz).offset(skip).limit(size).options(joinedload(Quiz.questions).joinedload(Question.answers), joinedload(Quiz.category), joinedload(Quiz.user))
             .where(Quiz.category_id == id))
    async with db as session:
        quizzes = await session.execute(query)
        total_queries = await session.execute(total_query)
        total = total_queries.scalars().one()
        quiz = quizzes.scalars().all()
        return {
            "total": total,
            "page": page,
            "size": size,
            "items": quiz,
            "pages": (total+size-1)//size
        }

async def get_approved_quizzes_by_category(id: int, page: int, size: int, db: AsyncSession):
    skip = (page-1)*size
    total_query = select(func.count()).select_from(Quiz)
    query = (select(Quiz).offset(skip).limit(size).options(joinedload(Quiz.questions).joinedload(Question.answers), joinedload(Quiz.category), joinedload(Quiz.user))
             .where((Quiz.category_id == id) & (Quiz.approved == True)))
    async with db as session:
        quizzes = await session.execute(query)
        total_queries = await session.execute(total_query)
        total = total_queries.scalars().one()
        quiz = quizzes.scalars().all()
        return {
            "total": total,
            "page": page,
            "size": size,
            "items": quiz,
            "pages": (total+size-1)//size
        }

async def get_all_user_approved_quizzes(id: int, db: AsyncSession) -> Sequence[Quiz]:
    query = (select(Quiz).options(joinedload(Quiz.questions).joinedload(Question.answers), joinedload(Quiz.category), joinedload(Quiz.user))
             .where((Quiz.user_id == id) & (Quiz.approved == True)))
    async with db as session:
        quizzes = await session.execute(query)
        return quizzes.scalars().unique().all()

async def create_quiz(quiz: Quiz, db: AsyncSession):
    async with db as session:
        session.add(quiz)
        await session.flush()
        await session.commit()

async def rate_quiz(id: int, rate: int, rate_count: int, db: AsyncSession):
    query = update(Quiz).where(Quiz.id == id).values(total_rate=Quiz.total_rate+rate, rate_count=rate_count)
    async with db as session:
        await session.execute(query)
        await session.commit()

async def approve_quiz(id: int, approved: bool, db: AsyncSession):
    query = update(Quiz).where(Quiz.id == id).values(approved=approved)
    async with db as session:
        await session.execute(query)
        await session.commit()

async def update_quiz(id: int, quiz: QuizRequest, db: AsyncSession):
    query = update(Quiz).where(Quiz.id == id).values(title=quiz.title, description=quiz.description, approved=False, category_id=quiz.category_id)
    async with db as session:
        await session.execute(query)
        await session.commit()

async def remove_quiz(id: int, db: AsyncSession):
    async with db as session:
        await session.execute(delete(Quiz).where(Quiz.id == id))
        await session.commit()