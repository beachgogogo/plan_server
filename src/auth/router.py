from fastapi import APIRouter
from .routers.login import login_router
from .routers.register import register_router
from .routers.project import task_router
from .routers.user import user_router


auth_router = APIRouter()

auth_router.include_router(user_router, prefix="/info", tags=["info"])
auth_router.include_router(login_router, prefix="/token", tags=["token"])
auth_router.include_router(register_router, prefix="/register", tags=["register"])
auth_router.include_router(task_router, prefix="/project", tags=["project"])


