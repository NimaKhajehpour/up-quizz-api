from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from auth.auth import oauth2_scheme, decode_access_token
from database.dependencies import get_db
from database.model.answer_model import Answer
from database.model.question_model import Question
from database.operations import question_operations, answer_operations, quiz_operations
from models.requests.answer_request import AnswerRequest

router = APIRouter(
    prefix="/answer",
    tags=["answer"]
)

@router.post("", status_code=204)
async def create_answer(answer: AnswerRequest, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    question = await question_operations.get_question_by_id(answer.question_id, db)
    if not question:
        raise HTTPException(status_code=404, detail="question not found")
    quiz = await quiz_operations.get_quiz_by_id(question.quiz_id, db)
    if not quiz:
        raise HTTPException(status_code=404, detail="quiz not found")
    if quiz.user_id != user.id:
        raise HTTPException(status_code=403, detail="You are not authorized")
    db_answer = Answer(**answer.model_dump())
    await answer_operations.create_answer(db_answer, db)

@router.put("/{id}", status_code=204)
async def update_answer(id: int, answer: AnswerRequest, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    db_answer = await answer_operations.get_answer_by_id(id, db)
    if not db_answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    question = await question_operations.get_question_by_id(answer.question_id, db)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    quiz = await quiz_operations.get_quiz_by_id(question.quiz_id, db)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz.user_id != user.id:
        raise HTTPException(status_code=403, detail="You are not authorized")
    await answer_operations.update_answer(id, answer, db)

@router.delete("/{id}", status_code=204)
async def remove_question(id: int, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    answer = await answer_operations.get_answer_by_id(id, db)
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    question = await question_operations.get_question_by_id(answer.question_id, db)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    quiz = await quiz_operations.get_quiz_by_id(question.quiz_id, db)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz.user_id != user.id:
        raise HTTPException(status_code=403, detail="You are not authorized")
    await answer_operations.delete_answer(id, db)