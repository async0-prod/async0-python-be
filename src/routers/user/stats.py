from fastapi import APIRouter, Depends
from sqlalchemy import bindparam, text
from sqlalchemy.dialects.postgresql import UUID
from src.dependencies.core import DBSessionDep
from src.dependencies.user import get_current_user
from src.models.user import User


stats_router = APIRouter(prefix="/problem/stat", tags=["User Problem Stats"])


@stats_router.get("/problem")
async def get_problem_stat(
    session: DBSessionDep,
    user: User | None = Depends(get_current_user),
):

    sql = text(
        """
        WITH current_month AS (
            SELECT COUNT(DISTINCT problem_id) AS count
            FROM submission
            WHERE status = 'Accepted'
              AND user_id = :user_id
              AND date_trunc('month', created_at) = date_trunc('month', CURRENT_DATE)
        ),
        last_month AS (
            SELECT COUNT(DISTINCT problem_id) AS count
            FROM submission
            WHERE status = 'Accepted'
              AND user_id = :user_id
              AND date_trunc('month', created_at) = date_trunc('month', CURRENT_DATE - INTERVAL '1 month')
        ),
        total_solved AS (
            SELECT COUNT(DISTINCT problem_id) AS count
            FROM submission
            WHERE status = 'Accepted'
              AND user_id = :user_id
        )
        SELECT
            total_solved.count AS total_problems_solved,
            ROUND(
                CASE
                    WHEN last_month.count = 0 THEN NULL
                    ELSE ((current_month.count - last_month.count) * 100.0 / last_month.count)
                END,
                2
            ) AS percentage_change
        FROM current_month, last_month, total_solved
        """
    ).bindparams(bindparam("user_id", type_=UUID))

    user_id = str(user.id) if user else None
    result = await session.execute(sql, {"user_id": user_id})
    row = result.mappings().first()
    return row


@stats_router.get("/streak")
async def get_problem_streak(
    session: DBSessionDep,
    user: User | None = Depends(get_current_user),
):
    sql = text(
        """
        WITH accepted_days AS (
            SELECT DISTINCT
                DATE(created_at) AS solved_date
            FROM submission
            WHERE status = 'Accepted'
              AND user_id = :user_id
        ),
        dated_rows AS (
            SELECT
                solved_date,
                ROW_NUMBER() OVER (ORDER BY solved_date) AS row_num
            FROM accepted_days
        ),
        streak_groups AS (
            SELECT
                solved_date,
                row_num,
                solved_date - (row_num || ' days')::INTERVAL AS streak_group
            FROM dated_rows
        ),
        streak_lengths AS (
            SELECT
                COUNT(*) AS streak_length
            FROM streak_groups
            GROUP BY streak_group
        )
        SELECT
            COALESCE(MAX(streak_length), 0)::int AS current_streak
        FROM streak_lengths
        """
    ).bindparams(bindparam("user_id", type_=UUID))

    user_id = str(user.id) if user else None
    result = await session.execute(sql, {"user_id": user_id})
    row = result.mappings().first()
    return row
