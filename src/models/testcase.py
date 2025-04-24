from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, func, TIMESTAMP
from datetime import datetime
from src.core.db import Base
from uuid import uuid4, UUID

if TYPE_CHECKING:
    from .problem import Problem


class TestCase(Base):
    __tablename__ = "testcase"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    problem_id: Mapped[UUID] = mapped_column(
        ForeignKey("problem.id", ondelete="CASCADE")
    )
    input: Mapped[str] = mapped_column(String)
    output: Mapped[str] = mapped_column(String)
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
        lazy="joined", innerjoin=True, back_populates="test_cases"
    )

    def __repr__(self):
        return f"<TestCase(id={self.id}, problem_id={self.problem_id})>"
