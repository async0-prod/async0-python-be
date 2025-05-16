from uuid import UUID
from pydantic import BaseModel
from src.models.enum import Status


class SubmissionBody(BaseModel):
    status: Status | None = Status.Accepted
    problem_id: UUID
    passed_testcases: int
    total_testcases: int
    code: str
