from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, UniqueConstraint, Enum, func, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import UUID, uuid4
from .enum import VoteType
from src.core.db import Base

if TYPE_CHECKING:
    from .user import User
    from .problem import Problem
    from .solution import Solution


class VoteSolution(Base):
    __tablename__ = "vote_solution"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    vote_type: Mapped[VoteType] = mapped_column(Enum(VoteType))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    problem_id: Mapped[UUID] = mapped_column(
        ForeignKey("problem.id", ondelete="CASCADE")
    )
    solution_id: Mapped[UUID] = mapped_column(
        ForeignKey("solution.id", ondelete="CASCADE")
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
        lazy="joined", innerjoin=True, back_populates="solution_votes"
    )
    problem: Mapped["Problem"] = relationship(
        lazy="joined", innerjoin=True, back_populates="solution_votes"
    )
    solution: Mapped["Solution"] = relationship(
        lazy="joined", innerjoin=True, back_populates="votes"
    )

    __table_args__ = (UniqueConstraint("user_id", "solution_id"),)

    def __repr__(self):
        return f"<VoteSolution(id={self.id}, vote_type={self.vote_type}, user_id={self.user_id}, problem_id={self.problem_id}, solution_id={self.solution_id})>"
