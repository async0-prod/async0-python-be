from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer, func, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship, WriteOnlyMapped
from datetime import datetime
from src.core.db import Base
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from .problem import Problem
    from .vote_solution import VoteSolution


class Solution(Base):
    __tablename__ = "solution"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String)
    rank: Mapped[int] = mapped_column(Integer, default=1)
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

    problem: Mapped["Problem"] = relationship(
        lazy="joined", innerjoin=True, back_populates="solutions"
    )
    votes: WriteOnlyMapped["VoteSolution"] = relationship(back_populates="solution")

    def __repr__(self):
        return f"<Solution(id={self.id}, code={self.code}, rank={self.rank})>"
