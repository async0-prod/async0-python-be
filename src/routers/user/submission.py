from fastapi import APIRouter, Depends
from src.dependencies.core import DBSessionDep
from src.dependencies.user import get_current_user
from src.models.enum import Status
from src.models.submission import Submission
from src.models.user import User
from src.models.user_solution import UserSolution
from src.schemas.submission import SubmissionBody

submission_router = APIRouter(prefix="/submissions", tags=["Submission"])


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
