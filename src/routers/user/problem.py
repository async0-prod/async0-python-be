import os
from fastapi import APIRouter, Depends
from sqlalchemy import func, select, literal
from sqlalchemy.orm import selectinload, contains_eager
from src.dependencies.user import get_current_user
from src.dependencies.core import DBSessionDep
from src.models.user_solution import UserSolution
from src.models.bookmark import Bookmark
from src.models.problem import Problem
from src.models.user import User
from src.models.submission import Submission
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

problem_router = APIRouter(prefix="/problem", tags=["Problem"])


@problem_router.get("/dashboard")
async def get_dashboard_problems(
    db: DBSessionDep, user: User = Depends(get_current_user)
):

    user_id = user.id if user else None
    print(user_id)
    solved_count_subq = (
        (
            select(
                UserSolution.problem_id,
                func.count(UserSolution.id.distinct()).label("solved_count"),
            )
        )
        .where(UserSolution.has_solved == True)
        .group_by(UserSolution.problem_id)
        .subquery("solved_count_subq")
    )

    bookmark_count_subq = (
        select(
            Bookmark.problem_id,
            func.count(Bookmark.id.distinct()).label("bookmark_count"),
        )
        .group_by(Bookmark.problem_id)
        .subquery("bookmark_count_subq")
    )

    if user_id:
        has_solved_subq = (
            select(
                UserSolution.problem_id,
                literal(True).label("has_solved"),
            )
            .where(
                UserSolution.user_id == user_id,
                UserSolution.has_solved == True,
            )
            .subquery()
        )

    query = (
        select(
            Problem,
            func.coalesce(solved_count_subq.c["solved_count"], 0).label(
                "totalUsersSolved"
            ),
            func.coalesce(bookmark_count_subq.c["bookmark_count"], 0).label(
                "totalBookmarks"
            ),
            (
                func.coalesce(has_solved_subq.c["has_solved"], False)
                if user_id
                else literal(False)
            ).label("hasSolved"),
        )
        .outerjoin(solved_count_subq, Problem.id == solved_count_subq.c.problem_id)
        .outerjoin(bookmark_count_subq, Problem.id == bookmark_count_subq.c.problem_id)
    )

    if user_id:
        query = query.outerjoin(
            has_solved_subq, Problem.id == has_solved_subq.c.problem_id
        )

    query = query.options(
        selectinload(Problem.topics),
        selectinload(Problem.lists),
    )

    result = await db.execute(query)
    rows = result.all()

    problems = []
    for problem, totalUsersSolved, totalBookmarks, hasSolved in rows:
        problems.append(
            {
                "id": str(problem.id),
                "name": problem.name,
                "difficulty": problem.difficulty.value,
                "topics": [t.name for t in problem.topics],
                "lists": [l.name for l in problem.lists],
                "totalUsersSolved": totalUsersSolved,
                "totalBookmarks": totalBookmarks,
                "hasSolved": hasSolved,
            }
        )

    return problems


class TestCaseResponse(BaseModel):
    id: UUID
    input: str
    output: str

    class Config:
        from_attributes = True


class SolutionResponse(BaseModel):
    id: UUID
    code: str
    rank: int

    class Config:
        from_attributes = True


class SubmissionResponse(BaseModel):
    id: UUID
    status: str
    passed_testcases: int
    total_testcases: int

    class Config:
        from_attributes = True


class ProblemResponse(BaseModel):
    id: UUID
    name: str
    # description: str
    difficulty: str
    starter_code: str
    link: str | None
    # time_limit: int | None
    # memory_limit: int | None
    # created_at: datetime
    # updated_at: datetime
    test_cases: list[TestCaseResponse] = []
    solutions: list[SolutionResponse] = []
    submissions: list[SubmissionResponse] = []

    class Config:
        from_attributes = True


@problem_router.get("/{problem_name}", response_model=ProblemResponse)
async def get_problem_details(
    problem_name: str, db: DBSessionDep, user: User = Depends(get_current_user)
):
    query = (
        select(Problem)
        .where(Problem.name == problem_name)
        .options(
            selectinload(Problem.bookmarks),
            selectinload(Problem.test_cases),
            selectinload(Problem.solutions),
        )
    )
    result = await db.execute(query)
    problem = result.scalar_one_or_none()

    submission_query = select(Submission).where(
        Submission.problem_id == problem.id, Submission.user_id == user.id
    )
    submissions_result = await db.execute(submission_query)

    problem.submissions = submissions_result.scalars().all()

    return problem
