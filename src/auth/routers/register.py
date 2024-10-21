from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from src.database_method import create_user_info
from src.model import User
from src.tool.packaging_tool import response_data
from src.log_manager import LogLevel, logging_by_thread
from src.tool.hash_context import get_info_hash


register_router = APIRouter()


@register_router.post("/")
async def user_register(user: User):
    """
    :param user:
    :return: User info
             result
    """
    try:
        user.password = get_info_hash(user.password)
        await create_user_info(user)
    except HTTPException as err:
        await logging_by_thread(LogLevel.INFO, err.detail, user_register.__qualname__)
        raise err
    else:
        await logging_by_thread(LogLevel.INFO, f"add user succeed. {user.email}", user_register.__qualname__)
        return response_data(data=user.model_dump(),
                             message="register succeed")
