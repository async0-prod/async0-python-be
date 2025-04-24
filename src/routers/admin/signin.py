import os
from typing import Annotated
from fastapi.responses import JSONResponse
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from uuid import UUID
from google.oauth2 import id_token
from google.auth.transport import requests
from src.utils.token import create_admin_access_token
from src.dependencies.core import DBSessionDep
from src.models.user import User, UserRoles

sign_in_router = APIRouter(prefix="/signin", tags=["Sign In"])


class UserRequest(BaseModel):
    email: EmailStr


class UserResponse(BaseModel):
    id: UUID
    email: str
    role: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@sign_in_router.post("/", response_model=UserResponse)
async def signin_admin(db: DBSessionDep, token: Annotated[str, Depends(oauth2_scheme)]):
    if token == "undefined":
        raise HTTPException(status_code=401, detail="Access token missing or invalid")
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            os.environ["GOOGLE_CLIENT_ID_ADMIN"],
            clock_skew_in_seconds=10,
        )
        email = idinfo["email"]

        result = await db.execute(
            select(User).where(User.email == email and User.role == UserRoles.ADMIN)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=401, detail="Not authorized")

        jwt_token = create_admin_access_token(
            {
                "user_id": str(user.id),
                "email": user.email,
                "role": user.role.value,
            }
        )

        response_data = {
            "id": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "server_access_token": jwt_token,
        }

        response = JSONResponse(content=response_data)

        return response

    except Exception as e:
        print("Error", e)
        raise HTTPException(status_code=401, detail="Something went wrong")
