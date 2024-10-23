from fastapi import APIRouter, Depends
from typing import Annotated
from src.user_authentication import get_current_user_token
from src.model import TokenData, UserInfo, UserProfileInfo, UserContactInfo
from src.database_method import phone_num_exist, find_user_by_id, update_user_profile, update_user_contact
from src.tool.packaging_tool import response_data
from src.config import engine

user_router = APIRouter()


@user_router.get("/info/base")
async def api_get_user_info(
        token: Annotated[TokenData, Depends(get_current_user_token)],
):
    """
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


@user_router.post("/info/profile")
async def api_update_user_profile(
        token: Annotated[TokenData, Depends(get_current_user_token)],
        data: UserProfileInfo):
    """
    更新用户名称
    :param data:
    :param token:
    :param name: username
    :return: username
    """
    await update_user_profile(token.user_id, data.model_dump())
    return response_data(data={data.model_dump_json()})


@user_router.patch("/info/contact")
async def api_update_user_contact(
        token: Annotated[TokenData, Depends(get_current_user_token)],
        data: UserContactInfo):
    """
    :param token:
    :param phone_num: phone number
    :return: phone number in database
    """
    await update_user_contact(token.user_id, act_type=data.action_type,
                              pf_data=data.model_dump())
    return response_data(data={data.model_dump_json()})
