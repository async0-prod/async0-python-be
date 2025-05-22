from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, Enum, func, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .enum import Status
from src.core.db import Base
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from .user import User
    from .problem import Problem
    from .user_solution import UserSolution


class Submission(Base):
    __tablename__ = "submission"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.Pending)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    problem_id: Mapped[UUID] = mapped_column(ForeignKey("problem.id"))
    user_solution_id: Mapped[UUID] = mapped_column(ForeignKey("user_solution.id"))
    passed_testcases: Mapped[int] = mapped_column(Integer)
    total_testcases: Mapped[int] = mapped_column(Integer)
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
        lazy="joined", innerjoin=True, back_populates="submissions"
    )
    problem: Mapped["Problem"] = relationship(
        lazy="joined", innerjoin=True, back_populates="submissions"
    )
    user_solution: Mapped["UserSolution"] = relationship(
        lazy="joined", innerjoin=True, back_populates="submissions"
    )

    def __repr__(self):
        return f"<Submission(id={self.id}, status={self.status}, user_id={self.user_id}, problem_id={self.problem_id}, user_solution_id={self.user_solution_id}, passed_testcases={self.passed_testcases}, total_testcases={self.total_testcases})>"
