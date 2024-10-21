from fastapi import APIRouter, Depends
from typing import Annotated
from src.user_authentication import get_current_user_token
from src.model import TokenData, UserInfo
from src.database_method import find_user_by_email, user_name_exist, phone_num_exist, find_user_by_id
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
    user = await find_user_by_id(user_id=token.user_id)
    profile = user.profile
    contact = user.contact
    ret_user = UserInfo(email=user.email,
                        username=user.username,
                        profile_photo=profile.profile_photo,
                        personalized_signature=profile.personalized_signature,
                        birthday=profile.birthday,
                        gender=profile.gender,
                        create_time=profile.create_time,
                        phone_number=contact.phone_number)
    return response_data(data=ret_user.model_dump_json())


@user_router.patch("/info/username")
async def reset_user_name(
        token: Annotated[TokenData, Depends(get_current_user_token)],
        name: str):
    """
    更新用户名称
    :param token:
    :param name: username
    :return: username
    """
    await user_name_exist(name)
    user = await find_user_by_id(user_id=token.user_id)
    user.username = name
    await engine.save(user)
    return response_data(data={"username": name})


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
    user_contact = (await find_user_by_id(user_id=token.user_id)).contact
    user_contact.phone_number = phone_num
    await engine.save(user_contact)
    return response_data(data={"phone number": user_contact.phone_number})
