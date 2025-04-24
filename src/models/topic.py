from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from src.core.db import Base
from .association import TopicProblem
from uuid import uuid4, UUID

if TYPE_CHECKING:
    from .problem import Problem
    from .list import List


class Topic(Base):
    __tablename__ = "topic"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String)
    list_id: Mapped[UUID] = mapped_column(ForeignKey("list.id", ondelete="CASCADE"))
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

    list_title: Mapped["List"] = relationship(
        lazy="joined", innerjoin=True, back_populates="topics"
    )
    problems: Mapped[list["Problem"]] = relationship(
        lazy="selectin", secondary=TopicProblem, back_populates="topics"
    )

    def __repr__(self):
        return f"<Topic(id={self.id}, name={self.name})>"
