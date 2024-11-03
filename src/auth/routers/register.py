from fastapi import APIRouter
from fastapi.exceptions import HTTPException
# from src.database.mongo_method import create_user_info
from src.database.pg_method import create_user_info, SessionDep
from src.model import UserRegister, UserShortInfo
from src.tool.packaging_tool import response_data
from src.log_manager import LogLevel, logging_by_thread
from src.tool.hash_context import get_info_hash


register_router = APIRouter()


@register_router.post("/")
async def user_register(session: SessionDep, user: UserRegister):
    """
    :param session:
    :param user:
    :return: User info
             result
    """
    try:
        user.password = get_info_hash(user.password)
        await create_user_info(session, user.model_dump())
    except HTTPException as err:
        await logging_by_thread(LogLevel.WARNING, err.detail, user_register.__qualname__)
        raise err
    else:
        await logging_by_thread(LogLevel.INFO,
                                f"add user succeed. {user.email}", user_register.__qualname__)
        return response_data(data=UserShortInfo.model_validate_json(user.model_dump_json()),
                             message="register succeed")
