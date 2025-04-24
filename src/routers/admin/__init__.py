from fastapi import APIRouter
from .problem import problem_router
from .signin import sign_in_router

admin_router = APIRouter(prefix="/admin", tags=["Admin"])
admin_router.include_router(problem_router)
admin_router.include_router(sign_in_router)
