from fastapi import HTTPException, Request, status
from sqlalchemy import select
from src.models.user import User
from src.utils.token import decode_access_token
from src.dependencies.core import DBSessionDep


async def get_current_user(request: Request, db: DBSessionDep):
    token = ""

    auth_header = request.headers.get("Authorization")
    if auth_header is None or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token payload not available",
        )

    result = await db.execute(select(User).where(User.id == payload["user_id"]))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not authorized"
        )

    return user
