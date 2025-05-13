from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from database.db import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True, index = True, unique = True)
    display_name: Mapped[str] = mapped_column(nullable = False)
    username: Mapped[str] = mapped_column(unique=True, nullable = False)
    about: Mapped[Optional[str]] = mapped_column(nullable=True)
    role: Mapped[str] = mapped_column(nullable=False, default="user", server_default=text("'user'"))
    password: Mapped[str] = mapped_column(nullable=False)
    quizzes: Mapped[Optional[list["Quiz"]]] = relationship(back_populates="user", cascade="all, delete")
    taken_quizzes: Mapped[Optional[list["TakenQuiz"]]] = relationship(back_populates="user", cascade="all, delete")
