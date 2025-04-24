from fastapi import APIRouter
from .problem import problem_router
from .signin import sign_in_router

user_router = APIRouter(prefix="/user", tags=["User"])
user_router.include_router(problem_router)
user_router.include_router(sign_in_router)
