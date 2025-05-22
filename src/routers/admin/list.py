from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import text
from src.dependencies.admin import get_current_admin_user
from src.dependencies.core import DBSessionDep
from src.models.user import User

list_router = APIRouter(prefix="/list", tags=["List"])


@list_router.get("/")
async def get_lists(
    session: DBSessionDep,
    admin: User | None = Depends(get_current_admin_user),
):

    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized role"
        )

    sql = text(
        """
        SELECT json_agg(
          json_build_object(
            'id', l.id,
            'name', l.name
          )
        ) as lists
        FROM list l
"""
    )
    result = await session.execute(sql)
    lists = result.scalar_one()
    return lists
