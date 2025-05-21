from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship, WriteOnlyMapped
from sqlalchemy import String, Integer, Enum, func, TIMESTAMP
from datetime import datetime
from .enum import Difficulty
from src.core.db import Base
from .association import TopicProblem, ListProblem
from uuid import uuid4, UUID

if TYPE_CHECKING:
    from .testcase import TestCase
    from .topic import Topic
    from .list import List
    from .bookmark import Bookmark
    from .solution import Solution
    from .user_solution import UserSolution
    from .submission import Submission
    from .vote_problem import VoteProblem
    from .vote_solution import VoteSolution


class Problem(Base):

    __tablename__ = "problem"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(
        String(128), index=True, unique=True, nullable=False
    )
    description: Mapped[str] = mapped_column(String)
    difficulty: Mapped[Difficulty] = mapped_column(
        Enum(Difficulty), default=Difficulty.NA
    )
    starter_code: Mapped[str] = mapped_column(String)
    link: Mapped[str | None] = mapped_column(String, nullable=True)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)
    time_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    memory_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
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

    test_cases: Mapped[list["TestCase"]] = relationship(
        lazy="selectin", back_populates="problem"
    )
    topics: Mapped[list["Topic"]] = relationship(
        lazy="selectin", secondary=TopicProblem, back_populates="problems"
    )
    lists: Mapped[list["List"]] = relationship(
        lazy="selectin", secondary=ListProblem, back_populates="problems"
    )
    bookmarks: Mapped["Bookmark"] = relationship(
        lazy="selectin", back_populates="problem"
    )
    solutions: Mapped[list["Solution"]] = relationship(
        lazy="selectin", back_populates="problem"
    )
    user_solutions: WriteOnlyMapped["UserSolution"] = relationship(
        back_populates="problem"
    )
    solution_votes: Mapped["VoteSolution"] = relationship(
        lazy="selectin", back_populates="problem"
    )
    votes: Mapped["VoteProblem"] = relationship(
        lazy="selectin", back_populates="problem"
    )
    submissions: Mapped[list["Submission"]] = relationship(
        lazy="selectin", back_populates="problem"
    )

    def __repr__(self):
        return f"<Problem(id={self.id}, name={self.name})>"
