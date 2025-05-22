from fastapi import APIRouter
from .signin import sign_in_router
from .submission import submission_router
from .dashboard import dashboard_router
from .problems import problems_router
from .sidebar import sidebar_router

user_router = APIRouter(prefix="/user", tags=["User"])
user_router.include_router(sign_in_router)
user_router.include_router(submission_router)
user_router.include_router(dashboard_router)
user_router.include_router(problems_router)
user_router.include_router(sidebar_router)
