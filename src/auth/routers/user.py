from fastapi import APIRouter, Depends
from typing import Annotated
from src.user_authentication import get_current_user_token
from src.model import TokenData
from src.database_method import find_user_by_email, user_name_exist, phone_num_exist
from src.tool.packaging_tool import response_data
from src.config import engine

user_router = APIRouter()


@user_router.get("/info")
async def get_user_info(
        token: Annotated[TokenData, Depends(get_current_user_token)],
):
    """
    得到用户除密码外所有信息\n
    user_num：用户码
    :param token:
    :return:
    """
    user = await find_user_by_email(email=token.email)
    return response_data(data={"num": user.num,
                               "email": user.email,
                               "username": user.username,
                               "create_time": user.create_time,
                               "phone_number": user.phone_number,
                               "profile_photo": user.profile_photo,
                               "personalized_signature": user.personalized_signature,
                               "file_set": user.file_set})


@user_router.patch("/info/username")
async def reset_user_name(
        token: Annotated[TokenData, Depends(get_current_user_token)],
        un: str):
    """
    更新用户名称
    :param token:
    :param un: username
    :return: username
    """
    await user_name_exist(un)
    user = await find_user_by_email(email=token.email)
    user.username = un
    await engine.save(user)
    return response_data(data={"username": un})


@user_router.patch("/info/phone")
async def reset_user_name(
        token: Annotated[TokenData, Depends(get_current_user_token)],
        phone_num: str):
    """
    更新用户手机号
    :param token:
    :param phone_num: phone number
    :return: phone number in database
    """
    await phone_num_exist(phone_num)
    user = await find_user_by_email(email=token.email)
    user.phone_number = phone_num
    await engine.save(user)
    return response_data(data={"phone number": user.phone_number})
