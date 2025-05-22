from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import bindparam, text
from sqlalchemy.dialects.postgresql import UUID as pUUID
from src.dependencies.core import DBSessionDep
from src.dependencies.user import get_current_user
from src.models.user import User
from src.models.enum import Status
from src.models.submission import Submission
from src.models.user_solution import UserSolution
from src.schemas.submission import SubmissionBody

submission_router = APIRouter(prefix="/submission", tags=["Submission"])


@submission_router.get("/{problem_id}")
async def get_user_submissions(
    problem_id: str,
    session: DBSessionDep,
    user: User | None = Depends(get_current_user),
):

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    sql = text(
        """
    SELECT *
    FROM submission s
    LEFT JOIN user_solution us ON us.user_id = :user_id
    WHERE s.user_id = :user_id AND s.problem_id = :problem_id
    ORDER BY s.created_at DESC
"""
    ).bindparams(
        bindparam("user_id", type_=pUUID),
        bindparam("problem_id", type_=pUUID),
    )

    result = await session.execute(
        sql,
        {
            "user_id": str(user.id),
            "problem_id": problem_id,
        },
    )
    submissions = result.mappings().all()
    return submissions


@submission_router.post("/")
async def post_user_submission(
    body: SubmissionBody,
    session: DBSessionDep,
    user: User = Depends(get_current_user),
):

    user_solution = UserSolution(
        code=body.code,
        has_solved=True if body.total_testcases == body.passed_testcases else False,
        user_id=user.id,
        problem_id=body.problem_id,
    )

    session.add(user_solution)
    await session.flush()

    submission = Submission(
        status=body.status if body.status is not None else Status.Accepted,
        user_id=user.id,
        problem_id=body.problem_id,
        user_solution_id=user_solution.id,
        passed_testcases=body.passed_testcases,
        total_testcases=body.total_testcases,
    )

    session.add(submission)
    await session.commit()
    await session.refresh(submission)

    return {
        "message": "Submission created",
        "solution_id": str(user_solution.id),
        "submission_id": str(submission.id),
    }
