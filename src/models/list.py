from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship, WriteOnlyMapped
from src.core.db import Base
from uuid import uuid4, UUID

if TYPE_CHECKING:
    from .problem import Problem
    from .topic import Topic


class List(Base):
    __tablename__ = "list"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(16))

    topics: WriteOnlyMapped["Topic"] = relationship(back_populates="list_title")
    problems: Mapped[list["Problem"]] = relationship(
        lazy="selectin", secondary="list_problem", back_populates="lists"
    )

    def __repr__(self):
        return f"<List(id={self.id}, name={self.name})>"
