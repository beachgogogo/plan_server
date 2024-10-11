from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from src.database_method import create_user_info
from src.model import User
from src.tool.packaging_tool import response_data
from src.log_manager import LogLevel, logging_by_thread


register_router = APIRouter()


@register_router.post("/")
async def user_register(user: User):
    """
    :param user:
    :return: User info
             result
    """
    ret_message = None
    try:
        await create_user_info(user.email, user.username, user.password, user.phone_number)
    except HTTPException as err:
        ret_message = err.detail
        await logging_by_thread(LogLevel.INFO, err.detail, user_register.__qualname__)
        raise err
    else:
        await logging_by_thread(LogLevel.INFO, f"add user succeed. {user.email}", user_register.__qualname__)
        return response_data(data=user.model_dump(),
                             message=ret_message)
