from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, UniqueConstraint, func, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from src.core.db import Base
from uuid import uuid4, UUID

if TYPE_CHECKING:
    from .user import User
    from .problem import Problem


class Bookmark(Base):
    __tablename__ = "bookmark"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
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
        lazy="joined", innerjoin=True, back_populates="bookmarks"
    )
    problem: Mapped["Problem"] = relationship(
        lazy="joined", innerjoin=True, back_populates="bookmarks"
    )

    __table_args__ = (UniqueConstraint("user_id", "problem_id"),)

    def __repr__(self):
        return f"<Bookmark(id={self.id}, user_id={self.user_id}, problem_id={self.problem_id})>"
