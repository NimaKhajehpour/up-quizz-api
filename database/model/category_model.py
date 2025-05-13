from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    approved: Mapped[bool] = mapped_column(default=False, nullable=False)

    quizzes: Mapped[Optional[list["Quiz"]]] = relationship(back_populates="category", cascade="all, delete")