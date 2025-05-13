from typing import Optional

from sqlalchemy import Column, Integer, ForeignKey, Double, Boolean, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from database.db import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement = True, index = True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable = False)
    total_rate: Mapped[float] = mapped_column(default=0.0, nullable=False)
    rate_count: Mapped[int] = mapped_column(default=0, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'), nullable=False)
    approved: Mapped[bool] = mapped_column(default=False, nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    user: Mapped["User"] = relationship(back_populates="quizzes")
    questions: Mapped[Optional[list["Question"]]] = relationship(back_populates="quiz", cascade="all, delete")
    category: Mapped["Category"] = relationship(back_populates="quizzes")
    taken_quizzes: Mapped[Optional[list["TakenQuiz"]]] = relationship(back_populates="quiz", cascade="all, delete")