from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette import status

from auth.auth import oauth2_scheme, decode_access_token
from database.dependencies import get_db
from database.model.category_model import Category
from database.model.quiz_model import Quiz
from database.model.user_model import User
from database.operations import quiz_operations, user_operations, category_operations
from models.requests.quiz_request import QuizRequest
from models.responses import quiz_response, question_response

router = APIRouter(
    prefix="/quiz",
    tags=["quiz"],
)

@router.get("")
async def get_all_quizzes(db: Annotated[AsyncSession, Depends(get_db)], page: int = Query(1, ge=1),
                          size: int = Query(10, ge=1, le=100), token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    quizzes = None
    if user.role == "admin":
        quizzes = await quiz_operations.get_all_quizzes(page, size, db)
    else:
        quizzes = await quiz_operations.get_all_approved_quizzes(page, size, db)
    return quizzes

@router.get("/user", response_model=list[quiz_response.Quiz])
async def get_own_quizzes(db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    quizzes = await quiz_operations.get_all_user_quizzes(user.id, db)
    return quizzes

@router.get("/search")
async def search_quizzes(query: str, db: Annotated[AsyncSession, Depends(get_db)], page: int = Query(1, ge=1),
                         size: int = Query(10, ge=1, le=100), token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    quizzes = None
    if user.role == "admin":
        quizzes = await quiz_operations.search_quizzes(query, page, size, db)
    else:
        quizzes = await quiz_operations.search_approved_quizzes(query, page, size, db)
    return quizzes

@router.get("/unapproved")
async def get_unapproved_quizzes(db: Annotated[AsyncSession, Depends(get_db)], page: int = Query(1, ge=1),
                                 size: int = Query(10, ge=1, le=100), token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    if user.role != "admin":
        raise HTTPException(status_code = 403, detail="Not authorized")
    return await quiz_operations.get_unapproved_quizzes(page, size, db)

@router.get("/filter")
async def filter_quizzes(category_id: int, db: Annotated[AsyncSession, Depends(get_db)], page: int = Query(1, ge=1),
                         size: int = Query(10, ge=1, le=100), token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    category = await category_operations.get_category_by_id(category_id, db)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if user.role == "admin":
        return await quiz_operations.get_quizzes_by_category(category_id, page, size, db)
    else:
        return await quiz_operations.get_approved_quizzes_by_category(category_id, page, size, db)

@router.get("/user/{user_id}", response_model=list[quiz_response.Quiz])
async def get_user_quizzes(user_id: int, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    query_user = await user_operations.get_user_by_id(user_id, db)
    if not query_user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == "admin":
        return await quiz_operations.get_all_user_quizzes(user_id, db)
    else:
        return await quiz_operations.get_all_user_approved_quizzes(user_id, db)

@router.get("/{id}", response_model=quiz_response.Quiz)
async def get_quiz(id: int, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    quiz = await quiz_operations.get_quiz_by_id(id, db)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if (quiz.approved == False and user.role != "admin") or (quiz.user_id != user.id and quiz.approved == False):
        raise HTTPException(status_code=403, detail="You are not authorized to view this quiz.")
    return quiz

@router.post("", status_code=status.HTTP_204_NO_CONTENT)
async def create_quiz(quiz: QuizRequest, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    category_exists = await category_operations.get_category_by_id(quiz.category_id, db)
    if not category_exists:
        raise HTTPException(status_code=404, detail="Category does not exist.")
    db_quiz = Quiz(**quiz.model_dump())
    db_quiz.user_id = user.id
    await quiz_operations.create_quiz(db_quiz, db)

@router.put("/rate/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def rate_quiz(id: int, rate: int, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    quiz = await quiz_operations.get_quiz_by_id(id, db)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    if not quiz.approved:
        raise HTTPException(status_code=400, detail="Can't rate quiz that is not approved")
    await quiz_operations.rate_quiz(id, rate, quiz.rate_count+1, db)

@router.put("/approve/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def approve_quiz(id: int, approved: bool, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to view this quiz.")
    quiz = await quiz_operations.get_quiz_by_id(id, db)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    await quiz_operations.approve_quiz(id, approved, db)

@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_quiz(id: int, quiz: QuizRequest, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    category_exists = await category_operations.get_category_by_id(quiz.category_id, db)
    if not category_exists:
        raise HTTPException(status_code=404, detail="Category does not exist.")
    db_quiz = await quiz_operations.get_quiz_by_id(id, db)
    if not db_quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    if db_quiz.user_id != user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to view this quiz.")
    await quiz_operations.update_quiz(id, quiz, db)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_quiz(id: int, db: Annotated[AsyncSession, Depends(get_db)], token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token, db)
    quiz = await quiz_operations.get_quiz_by_id(id, db)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    if quiz.user_id != user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to view this quiz.")
    await quiz_operations.remove_quiz(id, db)