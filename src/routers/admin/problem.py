from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import Integer, String, bindparam, text
from sqlalchemy.dialects.postgresql import UUID as pUUID
from src.models.user import User
from src.dependencies.admin import get_current_admin_user
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
    rank: int | None = None
    time_limit: int | None = None
    memory_limit: int | None = None
    topicId: str
    listId: str
    testcases: list[TestCaseModel] = Field(default_factory=list)


class ProblemUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128)
    description: str | None = None
    difficulty: str
    starterCode: str | None = None
    link: str | None = None
    time_limit: int | None = None
    memory_limit: int | None = None
    topicId: str
    listId: str
    testcases: list[TestCaseModel] = Field(default_factory=list)


@problem_router.get("/")
async def get_problems(
    session: DBSessionDep, admin: User | None = Depends(get_current_admin_user)
):

    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized role"
        )

    sql = text(
        """
        SELECT json_agg(
            json_build_object(
                'id', p.id,
                'name', p.name,
                'description', p.description,
                'difficulty', p.difficulty,
                'starter_code', p.starter_code,
                'link', p.link,
                'time_limit', p.time_limit,
                'memory_limit', p.memory_limit,
                'created_at', p.created_at,
                'updated_at', p.updated_at,
                'rank', p.rank,
                'testcase', COALESCE(tc.testcases, '[]'::json),
                'topic_problem', COALESCE(tp.topics, '[]'::json),
                'list_problem', COALESCE(lp.lists, '[]'::json)
            )
        ) AS problems
        FROM problem p
        LEFT JOIN (
            SELECT problem_id, json_agg(
                json_build_object(
                    'input', input,
                    'output', output
                )
            ) AS testcases
            FROM testcase
            GROUP BY problem_id
        ) tc ON tc.problem_id = p.id
        LEFT JOIN (
            SELECT tp.problem_id, json_agg(
                json_build_object(
                    'topic', json_build_object('name', t.name)
                )
            ) AS topics
            FROM topic_problem tp
            JOIN topic t ON tp.topic_id = t.id
            GROUP BY tp.problem_id
        ) tp ON tp.problem_id = p.id
        LEFT JOIN (
            SELECT lp.problem_id, json_agg(
                json_build_object(
                    'list', json_build_object('name', l.name)
                )
            ) AS lists
            FROM list_problem lp
            JOIN list l ON lp.list_id = l.id
            GROUP BY lp.problem_id
        ) lp ON lp.problem_id = p.id
    """
    )

    result = await session.execute(sql)
    problems = result.scalar_one_or_none() or []
    return problems


@problem_router.get("/{problem_id}", status_code=status.HTTP_200_OK)
async def get_problem(
    problem_id: str,
    session: DBSessionDep,
    admin: User | None = Depends(get_current_admin_user),
):
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized role"
        )

    sql = text(
        """
        SELECT json_build_object(
            'id', p.id,
            'name', p.name,
            'description', p.description,
            'difficulty', p.difficulty,
            'starter_code', p.starter_code,
            'link', p.link,
            'time_limit', p.time_limit,
            'memory_limit', p.memory_limit,
            'created_at', p.created_at,
            'updated_at', p.updated_at,
            'rank', p.rank,
            'testcase', COALESCE(tc.testcases, '[]'::json),
            'topic_problem', COALESCE(tp.topics, '[]'::json),
            'list_problem', COALESCE(lp.lists, '[]'::json),
            'solution', COALESCE(sol.solutions, '[]'::json)
        ) AS problem
        FROM problem p
        LEFT JOIN (
            SELECT problem_id, json_agg(
                json_build_object(
                    'input', input,
                    'output', output
                )
            ) AS testcases
            FROM testcase
            GROUP BY problem_id
        ) tc ON tc.problem_id = p.id
        LEFT JOIN (
            SELECT tp.problem_id, json_agg(
                json_build_object(
                    'topic', json_build_object(
                        'id', t.id,
                        'name', t.name
                    )
                )
            ) AS topics
            FROM topic_problem tp
            JOIN topic t ON tp.topic_id = t.id
            GROUP BY tp.problem_id
        ) tp ON tp.problem_id = p.id
        LEFT JOIN (
            SELECT lp.problem_id, json_agg(
                json_build_object(
                    'list', json_build_object(
                        'id', l.id,
                        'name', l.name
                    )
                )
            ) AS lists
            FROM list_problem lp
            JOIN list l ON lp.list_id = l.id
            GROUP BY lp.problem_id
        ) lp ON lp.problem_id = p.id
        LEFT JOIN (
            SELECT problem_id, json_agg(
                json_build_object(
                    'code', code,
                    'rank', rank
                )
            ) AS solutions
            FROM solution
            GROUP BY problem_id
        ) sol ON sol.problem_id = p.id
        WHERE p.id = :pid
        """
    ).bindparams(bindparam("pid", type_=pUUID))

    result = await session.execute(sql, {"pid": problem_id})
    problem = result.scalar_one_or_none()

    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found"
        )

    return problem


@problem_router.delete("/{problem_id}", status_code=status.HTTP_200_OK)
async def delete_problem(
    problem_id: str,
    session: DBSessionDep,
    admin: User | None = Depends(get_current_admin_user),
):
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized role"
        )

    sql = text(
        """
        DELETE FROM problem
        WHERE id = :problem_id
        """
    ).bindparams(bindparam("problem_id", type_=pUUID))

    await session.execute(sql, {"problem_id": problem_id})


@problem_router.post("/", status_code=status.HTTP_201_CREATED)
async def add_problem(
    data: ProblemCreateRequest,
    session: DBSessionDep,
    admin: User | None = Depends(get_current_admin_user),
):
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized role"
        )

    check_sql = text("SELECT id FROM problem WHERE name = :name").bindparams(
        bindparam("name", type_=String)
    )
    result = await session.execute(check_sql, {"name": data.name})
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Problem with name '{data.name}' already exists",
        )

    try:

        insert_problem_sql = text(
            """
                INSERT INTO problem (
                    name, description, difficulty, starter_code, link,
                    rank, time_limit, memory_limit
                ) VALUES (
                    :name, :description, :difficulty, :starter_code, :link,
                    :rank, :time_limit, :memory_limit
                )
                RETURNING id
            """
        ).bindparams(
            bindparam("name", type_=String),
            bindparam("description", type_=String),
            bindparam("difficulty", type_=String),
            bindparam("starter_code", type_=String),
            bindparam("link", type_=String),
            bindparam("rank", type_=Integer),
            bindparam("time_limit", type_=Integer),
            bindparam("memory_limit", type_=Integer),
        )

        result = await session.execute(
            insert_problem_sql,
            {
                "name": data.name,
                "description": data.description,
                "difficulty": data.difficulty,
                "starter_code": data.starterCode,
                "link": data.link,
                "time_limit": data.time_limit,
                "memory_limit": data.memory_limit,
            },
        )

        problem_id = result.scalar_one()

        await session.execute(
            text(
                "INSERT INTO topic_problem (topic_id, problem_id) VALUES (:topic_id, :problem_id)"
            ).bindparams(
                bindparam("topic_id", type_=String),
                bindparam("problem_id", type_=String),
            ),
            {"topic_id": str(data.topicId), "problem_id": problem_id},
        )

        await session.execute(
            text(
                "INSERT INTO list_problem (list_id, problem_id) VALUES (:list_id, :problem_id)"
            ).bindparams(
                bindparam("list_id", type_=String),
                bindparam("problem_id", type_=String),
            ),
            {"list_id": str(data.listId), "problem_id": problem_id},
        )

        for tc in data.testcases:
            await session.execute(
                text(
                    """
                    INSERT INTO testcase (problem_id, input, output)
                    VALUES (:problem_id, :input, :output)
                """
                ).bindparams(
                    bindparam("problem_id", type_=String),
                    bindparam("input", type_=String),
                    bindparam("output", type_=String),
                ),
                {
                    "problem_id": problem_id,
                    "input": tc.input,
                    "output": tc.output,
                },
            )

        await session.commit()

        return {
            "status": "success",
            "message": f"Problem '{data.name}' created successfully",
            "problem_id": problem_id,
        }

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create problem: {str(e)}",
        )


@problem_router.put("/{problem_id}", status_code=status.HTTP_200_OK)
async def update_problem(
    problem_id: str,
    data: ProblemUpdateRequest,
    session: DBSessionDep,
    admin: User | None = Depends(get_current_admin_user),
):
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized role"
        )

    check_sql = text("SELECT id FROM problem WHERE id = :problem_id").bindparams(
        bindparam("problem_id", type_=String)
    )

    result = await session.execute(check_sql, {"problem_id": problem_id})
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Problem with name '{data.name}' already exists",
        )

    try:

        update_sql = text(
            """
            UPDATE problem SET
                name = :name,
                description = :description,
                difficulty = :difficulty,
                starter_code = :starter_code,
                link = :link,
                time_limit = :time_limit,
                memory_limit = :memory_limit,
                updated_at = NOW()
            WHERE id = :problem_id
        """
        ).bindparams(
            bindparam("name", type_=String),
            bindparam("description", type_=String),
            bindparam("difficulty", type_=String),
            bindparam("starter_code", type_=String),
            bindparam("link", type_=Integer),
            bindparam("time_limit", type_=Integer),
            bindparam("memory_limit", type_=Integer),
        )

        await session.execute(
            update_sql,
            {
                "name": data.name,
                "description": data.description or "",
                "difficulty": data.difficulty,
                "starter_code": data.starterCode,
                "link": data.link,
                "time_limit": data.time_limit,
                "memory_limit": data.memory_limit,
                "problem_id": problem_id,
            },
        )

        await session.execute(
            text("DELETE FROM topic_problem WHERE problem_id = :pid").bindparams(
                bindparam("pid", type_=String)
            ),
            {"pid": problem_id},
        )
        await session.execute(
            text("DELETE FROM list_problem WHERE problem_id = :pid").bindparams(
                bindparam("pid", type_=String)
            ),
            {"pid": problem_id},
        )

        for tc in data.testcases:
            await session.execute(
                text(
                    """
                    INSERT INTO testcase (problem_id, input, output)
                    VALUES (:problem_id, :input, :output)
                """
                ).bindparams(
                    bindparam("problem_id", type_=String),
                    bindparam("input", type_=String),
                    bindparam("output", type_=String),
                ),
                {
                    "problem_id": problem_id,
                    "input": tc.input,
                    "output": tc.output,
                },
            )

        await session.commit()

        return {
            "status": "success",
            "message": f"Problem '{data.name}' updated successfully",
            "problem_id": problem_id,
        }
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update problem: {str(e)}",
        )
