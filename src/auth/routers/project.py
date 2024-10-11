from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Annotated
from src.model import TokenData, Folder
from src.user_authentication import get_current_user_token
from src.database_method import find_user_by_email, get_folder_info, plan_get_info
from src.tool.packaging_tool import response_data


task_router = APIRouter()


class UpdateData(BaseModel):
    timestamp: str


@task_router.get("/")
async def get_all_file(
        token: Annotated[TokenData, Depends(get_current_user_token)],
):
    """
    得到当前用户下的所有的文件夹信息
    :param token:
    :return:
    """
    user = await find_user_by_email(email=token.email)
    folder_list = []
    for folder_id in user.file_set:
        fd = await get_folder_info(folder_id)
        plan_list = []
        sub_folder_list = []
        for task_id in fd.tasks:
            plan_list.append(await plan_get_info(task_id, "name"))
        for doc_id in fd.docs:
            sub_folder_list.append(await plan_get_info(doc_id, "name"))
        folder = Folder(name=fd.name,
                        tasks=plan_list,
                        docs=sub_folder_list,
                        create_time=fd.create_time)
        folder_list.append(folder)
    return response_data(data=({"folder_list": folder_list}))


@task_router.get("/plan")
async def get_plan_info(
        token: Annotated[TokenData, Depends(get_current_user_token)],
):
    """
    得到当前任务信息
    :param token:
    :return:
    """
