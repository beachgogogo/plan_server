from fastapi import APIRouter, Depends
from typing import Annotated
from src.model import TokenData, Folder, PlanInfo, TaskUnit, UserFolderList, \
    FolderCreateRecv, FolderDeleteRecv, FolderUpdateRecv, PlanCreateRecv, PlanDeleteRecv, PlanUpdateProfileRecv, \
    UserPlanList, UserTaskList, TaskUnitCreateRecv, UserTaskCreateList, TaskUnitUpdateRecv, TaskUnitDelRecv
from src.user_authentication import GetToken
# from src.database.mongo_method import (create_folder, get_all_folder,
#                                        find_folder_by_name, get_plan_info_by_name, get_task_by_id, get_plan_info_by_id,
#                                        del_folder, folder_update_info, create_plan, folder_remove_plan, plan_update_profile)
from src.database.pg_method import SessionDep, get_user_folder, get_folder_plans, inner_get_plan_by_id, create_folder, \
    delete_user_folder, update_folder_info, create_plan, delete_plan, update_plan_profile, add_task, add_multi_tasks, \
    update_task, delete_task
from src.tool.packaging_tool import response_data

task_router = APIRouter()


@task_router.get("/")
async def api_get_current_user_all_folder(
        session: SessionDep,
        token: GetToken,
):
    """
    得到当前登录用户下的所有的文件夹信息
    :param session:
    :param token:
    :return:
    """
    data = await get_user_folder(session, token.user_email)
    folder_list = []
    for folder in data:
        folder_list.append(Folder.model_validate(folder))
    ret_folder_list = UserFolderList(folder_list=folder_list)
    return response_data(data=ret_folder_list)


@task_router.get("/{folder_id}")
async def api_get_folder_plans_info(
        session: SessionDep,
        token: GetToken,
        folder_id: str
):
    """
    获取folder内plans信息
    :param session:
    :param folder_id:
    :param token:
    :return:
    """
    plans = await get_folder_plans(session, folder_id)
    plan_list = []
    for plan in plans:
        plan_list.append(PlanInfo.model_validate(plans))
    ret_plan_list = UserPlanList(plan_list=plan_list)
    return response_data(data=ret_plan_list)


@task_router.get("/plan/{plan_id}")
async def api_get_plan_detail(
        session: SessionDep,
        token: GetToken,
        plan_id: str
):
    """
    得到plan下tasks内容
    :param session:
    :param token:
    :param plan_id:
    :return:
    """
    plan = await inner_get_plan_by_id(session, plan_id)
    tasks = []
    for task in plan.tasks:
        tasks.append(TaskUnit.model_validate(task))
    ret_task_list = UserTaskList(task_list=tasks)
    return response_data(data=ret_task_list)


@task_router.post("/")
async def api_create_folder(
        session: SessionDep,
        token: GetToken,
        folder: FolderCreateRecv
):
    folder = await create_folder(token.email, folder.folder_name, folder.model_dump())
    folder_ret = Folder.model_validate(folder)
    return response_data(data=folder_ret)


@task_router.delete("/")
async def api_delete_folder(
        session: SessionDep,
        token: GetToken,
        folder: FolderDeleteRecv
):
    fd_id = await delete_user_folder(session, token.user_email, folder.folder_id)
    return response_data(data=fd_id)


@task_router.patch("/")
async def api_update_folder_info(
        session: SessionDep,
        token: GetToken,
        folder_info: FolderUpdateRecv
):
    """
    修改当前folder信息
    :param session:
    :param token:
    :param folder_info:
    :return:
    """
    folder = await update_folder_info(session, token.user_email, folder_info.folder_id, folder_info.model_dump())
    return response_data(data=Folder.model_validate(folder))


@task_router.post("/plan")
async def api_create_plan(
        session: SessionDep,
        token: GetToken,
        plan_info: PlanCreateRecv
):
    plan = create_plan(session, token.user_email, folder_id=plan_info.folder_id, plan_data=plan_info.model_dump())
    ret_plan = PlanInfo.model_validate(plan)
    return response_data(data=ret_plan)


@task_router.delete("/plan")
async def api_delete_plan(
        session: SessionDep,
        token: GetToken,
        plan_info: PlanDeleteRecv
):
    plan_id = await delete_plan(session, user_email=token.user_email,
                                plan_id=plan_info.plan_id,
                                plan_name=plan_info.plan_name)
    return response_data(data={"plan_id": plan_id})


@task_router.patch("/plan/profile")
async def api_plan_update_profile(
        session: SessionDep,
        token: GetToken,
        plan_profile: PlanUpdateProfileRecv):
    plan = await update_plan_profile(session, token.user_email, plan_profile.plan_id, plan_profile.model_dump())
    ret_plan = PlanInfo.model_validate(plan)
    return response_data(data=ret_plan)


@task_router.post("/plan/single_task")
async def api_create_task(
        session: SessionDep,
        token: GetToken,
        plan_profile: TaskUnitCreateRecv):
    task = await add_task(session, token.user_email, plan_profile.plan_id, plan_profile.model_dump())
    ret_task = TaskUnit.model_validate(task)
    return response_data(data=ret_task)


@task_router.post("/plan/multi_task")
async def api_create_multi_task(
        session: SessionDep,
        token: GetToken,
        task_list: UserTaskCreateList):
    await add_multi_tasks(session, token.user_email, plan_id=task_list.plan_id,
                          task_list=task_list.model_dump()["task_list"])
    return response_data(data=task_list)


@task_router.patch("/plan/task")
async def api_update_task_info(
        session: SessionDep,
        token: GetToken,
        task_info: TaskUnitUpdateRecv):
    task = await update_task(session, token.user_email, plan_id=task_info.plan_id,
                             task_id=task_info.task_id,
                             task_info=task_info.data.model_dump())
    ret_task = TaskUnit.model_validate(task)
    return response_data(data=ret_task)


@task_router.delete("/plan/task")
async def api_delete_task_info(
        session: SessionDep,
        token: GetToken,
        info: TaskUnitDelRecv):
    task_id = await delete_task(session, token.user_email,
                                plan_id=info.plan_id, task_id=info.task_id)
    return response_data(data=task_id)
