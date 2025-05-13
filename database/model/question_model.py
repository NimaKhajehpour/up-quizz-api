from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True, autoincrement=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"), nullable = False)
    quiz: Mapped["Quiz"] = relationship(back_populates="questions")
    answers: Mapped[Optional[list["Answer"]]] = relationship(back_populates="question", cascade="all, delete")
    text: Mapped[str] = mapped_column(nullable = False)