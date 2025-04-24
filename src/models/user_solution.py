from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Boolean, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, WriteOnlyMapped
from datetime import datetime
from src.core.db import Base
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from .user import User
    from .problem import Problem
    from .submission import Submission


class UserSolution(Base):
    __tablename__ = "user_solution"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String)
    has_solved: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    problem_id: Mapped[UUID] = mapped_column(
        ForeignKey("problem.id", ondelete="CASCADE")
    )
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

    user: Mapped["User"] = relationship(
        lazy="joined", innerjoin=True, back_populates="user_solutions"
    )
    problem: Mapped["Problem"] = relationship(
        lazy="joined", innerjoin=True, back_populates="user_solutions"
    )
    submissions: WriteOnlyMapped["Submission"] = relationship(
        back_populates="user_solution"
    )

    def __repr__(self):
        return f"<UserSolution(id={self.id}, code={self.code}, has_solved={self.has_solved})>"
