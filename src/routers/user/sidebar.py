from fastapi import APIRouter, Depends
from sqlalchemy import bindparam, text

from src.dependencies.core import DBSessionDep
from src.dependencies.user import get_current_user
from src.models.user import User

sidebar_router = APIRouter(prefix="/sidebar", tags=["Sidebar"])


@sidebar_router.get("/")
async def get_sidebar(
    db: DBSessionDep,
    # user: User | None = Depends(get_current_user),
):
    sql = text(
        """
    SELECT json_agg(
      json_build_object(
        'name', l.name,
        'topic', (
          SELECT json_agg(
            json_build_object(
              'name', t.name,
              'topic_problem', (
                SELECT json_agg(
                  json_build_object(
                    'problem', json_build_object(
                      'name', p.name,
                      'difficulty', p.difficulty,
                      'time_limit', p.time_limit,
                      'memory_limit', p.memory_limit
                    )
                  )
                )
                FROM topic_problem tp2
                JOIN problem p ON p.id = tp2.problem_id
                JOIN list_problem lp2 ON lp2.problem_id = p.id
                WHERE tp2.topic_id = t.id AND lp2.list_id = l.id
              )
            )
          )
          FROM topic t
          WHERE EXISTS (
            SELECT 1
            FROM topic_problem tp
            JOIN problem p2 ON tp.problem_id = p2.id
            JOIN list_problem lp ON p2.id = lp.problem_id
            WHERE tp.topic_id = t.id AND lp.list_id = l.id
          )
        )
      )
    ) AS sidebar_data
    FROM list l;
    """
    )

    result = await db.execute(sql)
    sidebar_data = result.scalar()
    return sidebar_data
