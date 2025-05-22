from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import text

from src.dependencies.admin import get_current_admin_user
from src.dependencies.core import DBSessionDep
from src.models.user import User

topic_router = APIRouter(prefix="/topic", tags=["Topic"])


@topic_router.get("/")
async def get_topics(
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
            'id', t.id,
            'name', t.name,
            'list_id', t.list_id
          )
        ) as topics
        FROM topic t
"""
    )
    result = await session.execute(sql)
    lists = result.scalar_one()
    return lists
