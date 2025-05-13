from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db import Base


class TakenQuiz(Base):
    __tablename__ = 'takenQuizzes'

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True, index=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    correct_answers: Mapped[int] = mapped_column(nullable=False)
    total_answers: Mapped[int] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship(back_populates="taken_quizzes")
    quiz: Mapped["Quiz"] = relationship(back_populates="taken_quizzes")