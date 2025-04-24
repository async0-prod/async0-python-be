from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field, UUID4
from sqlalchemy import select, delete
from src.models.solution import Solution
from src.models.association import TopicProblem, ListProblem
from src.models.user import User
from src.dependencies.admin import get_current_admin_user
from src.models.testcase import TestCase
from src.models.problem import Problem
from src.dependencies.core import DBSessionDep


problem_router = APIRouter(prefix="/problem", tags=["Problem"])


class SolutionModel(BaseModel):
    code: str
    rank: int


class TestCaseModel(BaseModel):
    input: str
    output: str


class ProblemCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: str | None = ""
    difficulty: str
    starterCode: str
    link: str | None = None
    time_limit: int | None = None
    memory_limit: int | None = None
    topicId: UUID4
    listId: UUID4
    solutions: list[SolutionModel] = Field(default_factory=list)
    testcases: list[TestCaseModel] = Field(default_factory=list)


class ProblemUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128)
    description: str | None = None
    difficulty: str
    starterCode: str | None = None
    link: str | None = None
    time_limit: int | None = None
    memory_limit: int | None = None
    topicId: UUID4
    listId: UUID4
    solutions: list[SolutionModel] = Field(default_factory=list)
    testcases: list[TestCaseModel] = Field(default_factory=list)


@problem_router.post("/", status_code=status.HTTP_201_CREATED)
async def add_problem(
    data: ProblemCreateRequest,
    db: DBSessionDep,
    admin: User = Depends(get_current_admin_user),
):

    result = await db.execute(select(Problem).where(Problem.name == data.name))
    existing_problem = result.scalar_one_or_none()
    print(existing_problem)
    if existing_problem:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Problem with name '{data.name}' already exists",
        )

    try:
        new_problem = Problem(
            name=data.name,
            description=data.description,
            difficulty=data.difficulty,
            starter_code=data.starterCode,
            link=data.link,
            time_limit=data.time_limit,
            memory_limit=data.memory_limit,
        )

        db.add(new_problem)
        await db.flush()

        topic_association = TopicProblem.insert().values(
            topic_id=data.topicId, problem_id=new_problem.id
        )
        await db.execute(topic_association)

        list_association = ListProblem.insert().values(
            list_id=data.listId, problem_id=new_problem.id
        )
        await db.execute(list_association)

        for tc_data in data.testcases:
            tc = TestCase(
                problem_id=new_problem.id,
                input=tc_data.input,
                output=tc_data.output,
            )
            db.add(tc)

        for i, sol_data in enumerate(data.solutions):
            sol = Solution(
                problem_id=new_problem.id,
                code=sol_data.code,
                rank=sol_data.rank,
            )
            db.add(sol)

        await db.commit()
        await db.refresh(new_problem)

        return {
            "status": "success",
            "message": f"Problem '{new_problem.name}' created successfully",
            "problem_id": str(new_problem.id),
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create problem: {str(e)}",
        )


@problem_router.put("/{problem_id}", status_code=status.HTTP_200_OK)
async def update_problem(
    problem_id: UUID4,
    data: ProblemUpdateRequest,
    db: DBSessionDep,
    admin: User = Depends(get_current_admin_user),
):
    result = await db.execute(select(Problem).where(Problem.id == problem_id))
    problem = result.scalar_one_or_none()

    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Problem with id '{problem_id}' not found",
        )

    try:
        problem.name = data.name
        problem.description = data.description if data.description else ""
        problem.difficulty = data.difficulty
        problem.starter_code = data.starterCode
        problem.link = data.link
        problem.time_limit = data.time_limit
        problem.memory_limit = data.memory_limit

        await db.execute(
            delete(TopicProblem).where(TopicProblem.c["problem_id"] == problem_id)
        )
        topic_association = TopicProblem.insert().values(
            topic_id=data.topicId, problem_id=problem_id
        )
        await db.execute(topic_association)

        await db.execute(
            delete(ListProblem).where(ListProblem.c["problem_id"] == problem_id)
        )
        list_association = ListProblem.insert().values(
            list_id=data.listId, problem_id=problem_id
        )
        await db.execute(list_association)

        await db.execute(delete(TestCase).where(TestCase.problem_id == problem_id))

        for tc_data in data.testcases:
            tc = TestCase(
                problem_id=problem_id,
                input=tc_data.input,
                output=tc_data.output,
            )
            db.add(tc)

        await db.execute(delete(Solution).where(Solution.problem_id == problem_id))

        for i, sol_data in enumerate(data.solutions):
            sol = Solution(
                problem_id=problem_id,
                code=sol_data.code,
                rank=sol_data.rank,
            )
            db.add(sol)

        await db.commit()
        await db.refresh(problem)

        return {
            "status": "success",
            "message": f"Problem '{problem.name}' updated successfully",
            "problem_id": str(problem.id),
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update problem: {str(e)}",
        )
