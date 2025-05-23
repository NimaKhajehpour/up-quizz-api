from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from auth.auth import oauth2_scheme, decode_access_token
from database.dependencies import get_db
from database.model.question_model import Question
from database.model.quiz_model import Quiz
from database.operations import quiz_operations, question_operations
from models.requests.question_request import QuestionRequest

router = APIRouter(
    prefix = "/question",
    tags = ["question"],
)

@router.post("", status_code=204)
async def create_question(question: QuestionRequest, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    quiz = await quiz_operations.get_quiz_by_id(question.quiz_id, db)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz.user_id != user.id:
        raise HTTPException(status_code=403, detail="You are not authorized")
    db_question = Question(**question.model_dump())
    await question_operations.create_question(db_question, db)

@router.put("/{id}", status_code=204)
async def update_question(id: int, question: QuestionRequest, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    db_question = await question_operations.get_question_by_id(id, db)
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")
    db_quiz = await quiz_operations.get_quiz_by_id(question.quiz_id, db)
    if not db_quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if db_quiz.user_id != user.id:
        raise HTTPException(status_code=403, detail="You are not authorized")
    await question_operations.update_question(id, question, db)

@router.delete("/bulk", status_code=204)
async def bulk_delete_questions(ids: list[int], db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    await question_operations.bulk_delete_question(user.id, ids, db)

@router.delete("/{id}", status_code=204)
async def remove_question(id: int, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    question = await question_operations.get_question_by_id(id, db)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    quiz = await quiz_operations.get_quiz_by_id(question.quiz_id, db)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz.user_id != user.id:
        raise HTTPException(status_code=403, detail="You are not authorized")
    await question_operations.remove_question(id, db)