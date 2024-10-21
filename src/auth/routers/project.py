from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from src.model import TokenData, Folder, FolderUpdateInfo
from src.user_authentication import get_current_user_token
from src.database_method import (find_user_by_email, find_folder_info, plan_get_info, find_user_by_num, create_folder,
                                 find_folder_by_name, del_folder_by_user, str_to_objectid)
from src.tool.packaging_tool import response_data


task_router = APIRouter()


@task_router.get("/")
async def api_get_current_user_all_folder(
        token: Annotated[TokenData, Depends(get_current_user_token)],
):
    """
    得到当前登录用户下的所有的文件夹信息
    :param token:
    :return:
    """
    user = await find_user_by_email(email=token.email)
    folder_list = []
    for folder_id in user.file_set:
        fd = await find_folder_info(folder_id)
        plan_list = []
        sub_folder_list = []
        for task_id in fd.tasks:
            plan_list.append(await plan_get_info(task_id, "name"))
        for file_id in fd.folders:
            sub_folder_list.append(await plan_get_info(file_id, "name"))
        folder = Folder(name=fd.name,
                        tasks=plan_list,
                        folders=sub_folder_list,
                        create_time=fd.create_time)
        folder_list.append(folder)
    return response_data(data=({"folder_list": folder_list}))


@task_router.get("/{num}")
async def api_get_user_all_folder(num: int):
    """
    访问该用户的文件夹信息(包括内部信息)
    :param num: 用户的标识码
    :return:
    """
    user = await find_user_by_num(num)
    data = []

    for folder_info in user.file_set:
        if folder_info["status"]:
            data.append(folder_info["name"])
    return response_data(data={"folder_list": data})


@task_router.post("/")
async def api_create_folder(
        token: Annotated[TokenData, Depends(get_current_user_token)],
        folder_name: str
):
    await create_folder(token.email, folder_name)
    return response_data(data={"folder_name": folder_name})


@task_router.delete("/{folder_id}")
async def api_delete_folder(
        token: Annotated[TokenData, Depends(get_current_user_token)],
        folder_id: str
):
    ret_id = await del_folder_by_user(token.email, str_to_objectid(folder_id))
    return response_data(data={"folder_info": ret_id})


@task_router.put("/")
async def api_update_folder_info(
        token: Annotated[TokenData, Depends(get_current_user_token)],
        folder_info: FolderUpdateInfo
):
    """
    修改当前folder信息
    :param token:
    :param folder_info:
    :return:
    """
    user = await find_user_by_email(email=token.email)
    if folder_info.folder_name is not None:
        folder = await find_folder_by_name(folder_name=folder_info.folder_name)
        if folder.id not in user.file_set:
            raise HTTPException(404, "folder not belong with user")
    return response_data(data=folder_info.model_dump())


# @task_router.get("/plan")
# async def get_plan_info(
#         token: Annotated[TokenData, Depends(get_current_user_token)],
# ):
#     """
#     得到当前任务信息
#     :param token:
#     :return:
#     """

