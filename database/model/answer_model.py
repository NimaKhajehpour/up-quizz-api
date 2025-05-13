from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db import Base


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True, unique = True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable = False)
    text: Mapped[str] = mapped_column(nullable = False)
    isCorrect: Mapped[bool] = mapped_column(nullable = False)

    question: Mapped["Question"] = relationship(back_populates="answers")