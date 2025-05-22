from fastapi import APIRouter, Depends
from sqlalchemy import String, bindparam, text
from sqlalchemy.dialects.postgresql import UUID
from src.dependencies.core import DBSessionDep
from src.dependencies.user import get_current_user
from src.models.user import User

problems_router = APIRouter(prefix="/problems", tags=["Problems"])


@problems_router.get("/")
async def get_problems(
    session: DBSessionDep,
    user: User | None = Depends(get_current_user),
):

    sql = text(
        """
  SELECT
  p.id,
  p.name,
  p.difficulty,
  COALESCE(bm.bookmark_count, 0)::int AS totalBookmarks,
  COALESCE(s.solved_count, 0)::int AS totalUsersSolved,
  EXISTS (
    SELECT 1
    FROM submission s2
    WHERE s2.problem_id = p.id
        AND (:user_id IS NOT NULL AND s2.user_id = :user_id)
        AND s2.status = 'Accepted'
    ) AS hasSolved,
  ARRAY_AGG(DISTINCT t.name) FILTER (WHERE t.name IS NOT NULL) AS topics,
  ARRAY_AGG(DISTINCT l.name) FILTER (WHERE l.name IS NOT NULL) AS lists
FROM
  problem p
LEFT JOIN (
  SELECT
    problem_id,
    COUNT(*)::int AS bookmark_count
  FROM
    bookmark
  GROUP BY
    problem_id
) bm ON p.id = bm.problem_id
LEFT JOIN (
  SELECT
    problem_id,
    COUNT(DISTINCT user_id)::int AS solved_count
  FROM
    submission
  WHERE
    status = 'Accepted'
  GROUP BY
    problem_id
) s ON p.id = s.problem_id
LEFT JOIN topic_problem tp ON p.id = tp.problem_id
LEFT JOIN topic t ON tp.topic_id = t.id
LEFT JOIN list_problem lp ON p.id = lp.problem_id
LEFT JOIN list l ON lp.list_id = l.id
GROUP BY
  p.id, p.name, p.difficulty, bm.bookmark_count, s.solved_count
ORDER BY
  p.rank ASC

 """
    ).bindparams(bindparam("user_id", type_=UUID))

    user_id = str(user.id) if user else None
    result = await session.execute(sql, {"user_id": user_id})
    problems = result.mappings().all()
    return problems


@problems_router.get("/{problem_name}")
async def get_problem_by_name(
    problem_name: str,
    session: DBSessionDep,
):
    sql = text(
        """
    SELECT
      p.id,
      p.name,
      p.difficulty,
      p.link,
      p.starter_code,
      COALESCE(
        json_agg(
          json_build_object(
            'id', t.id,
            'input', t.input,
            'output', t.output
          )
        ) FILTER (WHERE t.id IS NOT NULL),
        '[]'
      ) AS testcases
    FROM problem p
    LEFT JOIN testcase t ON p.id = t.problem_id
    WHERE p.name = :problem_name
    GROUP BY p.id
    """
    ).bindparams(bindparam("problem_name", type_=String))

    result = await session.execute(sql, {"problem_name": problem_name})
    problem = result.mappings().all()
    return problem
