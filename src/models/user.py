from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship, WriteOnlyMapped
from sqlalchemy import String, Enum, func, TIMESTAMP
from datetime import datetime
from src.core.db import Base
from .enum import UserRoles

from uuid import uuid4, UUID

if TYPE_CHECKING:
    from .bookmark import Bookmark
    from .user_solution import UserSolution
    from .vote_problem import VoteProblem
    from .vote_solution import VoteSolution
    from .submission import Submission


class User(Base):
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    role: Mapped[UserRoles] = mapped_column(Enum(UserRoles), default=UserRoles.USER)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        index=True,
        nullable=False,
        default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        index=True,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )

    bookmarks: WriteOnlyMapped["Bookmark"] = relationship(back_populates="user")
    user_solutions: WriteOnlyMapped["UserSolution"] = relationship(
        back_populates="user"
    )
    solution_votes: WriteOnlyMapped["VoteSolution"] = relationship(
        back_populates="user"
    )
    problem_votes: WriteOnlyMapped["VoteProblem"] = relationship(back_populates="user")
    submissions: WriteOnlyMapped["Submission"] = relationship(back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
