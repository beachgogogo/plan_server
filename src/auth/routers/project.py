from fastapi import APIRouter, Depends
from typing import Annotated
from src.model import TokenData, Folder, PlanInfo, TaskUnit, UserFolderList, \
    FolderCreateRecv, FolderDeleteRecv, FolderUpdateRecv, PlanCreateRecv, PlanDeleteRecv, PlanUpdateProfileRecv
from src.user_authentication import get_current_user_token
from src.database.mongo_method import (create_folder, get_all_folder,
                                       find_folder_by_name, get_plan_info_by_name, get_task_by_id, get_plan_info_by_id,
                                       del_folder, folder_update_info, create_plan, folder_remove_plan, plan_update_profile)
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
    model_json = await get_all_folder(token.user_id)
    folder_list = UserFolderList.model_validate_json(model_json)
    return response_data(data=folder_list)


@task_router.get("/{folder_name}")
async def api_get_folder_info(
        token: Annotated[TokenData, Depends(get_current_user_token)],
        folder_name: str
):
    """
    获取folder内plan信息
    :param folder_name:
    :param token:
    :return:
    """
    fd_data_json = await find_folder_by_name(token.user_id, folder_name)
    folder = Folder.model_validate_json(fd_data_json)
    return response_data(data=folder)


@task_router.get("/plan")
async def api_get_plan(
        token: Annotated[TokenData, Depends(get_current_user_token)],
        fd_name: str,
        plan_name: str
):
    plan_json = await get_plan_info_by_name(user_id=token.user_id, folder_name=fd_name, plan_name=plan_name)
    plan = PlanInfo.model_validate_json(plan_json)
    task_list = []
    for task_id in plan.task_list:
        task_json = await get_task_by_id(task_id)
        task_list.append(TaskUnit.model_validate_json(task_json))
    plan.task_list = task_list
    return response_data(data=plan)


@task_router.get("/plan")
async def api_get_folder_all_plan(
        token: Annotated[TokenData, Depends(get_current_user_token)],
        fd_name: str
):
    folder_json = await find_folder_by_name(token.user_id, fd_name)
    folder = Folder.model_validate_json(folder_json)
    plan_list = []
    for plan_id in folder.plans:
        plan_json = await get_plan_info_by_id(plan_id)
        plan_info = PlanInfo.model_validate_json(plan_json)
        plan_info.plan_id = plan_id
        plan_list.append(plan_info)
    folder.plans = plan_list
    return response_data(data=folder)


@task_router.post("/")
async def api_create_folder(
        token: Annotated[TokenData, Depends(get_current_user_token)],
        folder: FolderCreateRecv
):
    folder_json = await create_folder(token.email, folder.folder_name, folder.status)
    folder_ret = Folder.model_validate_json(folder_json)
    return response_data(data=folder_ret)


@task_router.delete("/")
async def api_delete_folder(
        token: Annotated[TokenData, Depends(get_current_user_token)],
        folder: FolderDeleteRecv
):
    await del_folder(token.user_id, folder.folder_name)
    return response_data(data={"folder_info": folder})


@task_router.patch("/")
async def api_update_folder_info(
        token: Annotated[TokenData, Depends(get_current_user_token)],
        folder_info: FolderUpdateRecv
):
    """
    修改当前folder信息
    :param token:
    :param folder_info:
    :return:
    """
    await folder_update_info(token.user_id, old_name=folder_info.old_name,
                             new_name=folder_info.new_name, status=folder_info.status)
    return response_data(data=folder_info)


@task_router.post("/plan")
async def api_create_plan(
        token: Annotated[TokenData, Depends(get_current_user_token)],
        plan_info: PlanCreateRecv
):
    plan_json = await create_plan(token.user_id, folder_name=plan_info.folder_name,
                                  plan_name=plan_info.plan_name,
                                  award_detail=plan_info.award.detail,
                                  status=plan_info.status)
    plan = PlanInfo.model_validate_json(plan_json)
    return response_data(data=plan.model_dump_json())


@task_router.delete("/plan")
async def api_delete_plan(
        token: Annotated[TokenData, Depends(get_current_user_token)],
        plan_info: PlanDeleteRecv
):
    await folder_remove_plan(token.user_id, folder_name=plan_info.folder_name,
                             plan_name=plan_info.plan_name)
    return response_data(data=plan_info.model_dump_json())


@task_router.patch("/plan")
async def api_plan_update_profile(
        token: Annotated[TokenData, Depends(get_current_user_token)],
        plan_profile: PlanUpdateProfileRecv):
    await plan_update_profile(token.user_id, plan_id=plan_profile.plan_id,
                              plan_name=plan_profile.plan_name, status=plan_profile.status,
                              award_detail=plan_profile.award.detail,
                              fulfill=plan_profile.award.is_fulfill,
                              start_time=plan_profile.start_time,
                              end_time=plan_profile.end_time)
    return response_data(data=plan_profile.model_dump_json())


