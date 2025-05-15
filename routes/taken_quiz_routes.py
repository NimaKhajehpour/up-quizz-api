from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from auth.auth import oauth2_scheme, decode_access_token
from database.dependencies import get_db
from database.model.quiz_model import Quiz
from database.model.taken_quiz_model import TakenQuiz
from database.model.user_model import User
from database.operations import taken_quiz_operations, user_operations, quiz_operations
from models.requests.taken_quiz_request import TakenQuizRequest
from models.responses import taken_quiz_response

router = APIRouter(
    prefix="/taken_quiz",
    tags=["taken_quiz"],
)

@router.get("")
async def get_taken_quizzes(db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    taken_quizzes = await taken_quiz_operations.get_taken_quizzes(user.id, db)
    return taken_quizzes

@router.get("/user/{id}")
async def get_user_taken_quiz(id: int, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    db_user = await user_operations.get_user_by_id(id, db)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    taken_quizzes = await taken_quiz_operations.get_taken_quizzes(id, db)
    return taken_quizzes

@router.post("", status_code=204)
async def add_taken_quiz(taken_quiz: TakenQuizRequest, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    quiz_exists = await quiz_operations.get_quiz_by_id(taken_quiz.quiz_id, db)
    if not quiz_exists:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if not quiz_exists.approved:
        raise HTTPException(status_code=403, detail="You are not authorized to take this quiz. Quiz not approved")
    taken_quiz_db = TakenQuiz(**taken_quiz.model_dump())
    taken_quiz_db.user_id = user.id
    await taken_quiz_operations.create_taken_quiz(taken_quiz_db, db)