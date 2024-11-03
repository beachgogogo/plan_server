from fastapi import APIRouter, Depends
from typing import Annotated
from src.user_authentication import get_current_user_token, GetToken
from src.model import TokenData, UserInfo, UserProfileInfo, UserAddressInfo
# from src.database.mongo_method import find_user_by_id, update_user_profile, update_user_contact, del_user
from src.database.pg_method import find_user_by_email, SessionDep, update_user_profile, update_user_addr, \
    delete_user_addr
from src.tool.packaging_tool import response_data

user_router = APIRouter()


@user_router.get("/base")
async def api_get_user_info(session: SessionDep, token: GetToken):
    """
    :param session:
    :param token:
    :return:
    """
    user = await find_user_by_email(session, email=token.user_email)
    profile = user.profile
    contact = user.contact
    ret_user = UserInfo.model_validate_json(user.model_dump_json())
    ret_user = ret_user.model_validate_json(profile.model_dump_json())
    ret_user = ret_user.model_validate_json(contact.model_dump_json())
    return response_data(data=ret_user)


@user_router.patch("/profile")
async def api_update_user_profile(
        session: SessionDep,
        token: GetToken,
        data: UserProfileInfo):
    """
    更新用户名称
    :param session:
    :param data:
    :param token:
    :return:
    """
    await update_user_profile(session, token.user_id, data.model_dump())
    return response_data(data=data)


@user_router.patch("/contact")
async def api_update_user_contact(
        token: Annotated[TokenData, Depends(get_current_user_token)],
        data: UserAddressInfo):
    addr = await update_user_addr(token.user_id, user_email=token.user_email,
                                  addr_ptr=data.addr_ptr, addr_data=data.addr_data)
    return response_data(data=addr)


@user_router.patch("/contact")
async def api_delete_user_contact(
        token: Annotated[TokenData, Depends(get_current_user_token)],
        data: UserAddressInfo):
    addr = await delete_user_addr(token.user_id, user_email=token.user_email,
                                  addr_ptr=data.addr_ptr)

    return response_data(data=addr)


# @user_router.delete("/")
# async def api_delete_user(
#         token: Annotated[TokenData, Depends(get_current_user_token)]):
#     await del_user(token.user_id)
#     return response_data(data="done")
