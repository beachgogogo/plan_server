from src.config import engine
from odmantic import ObjectId
from src import database_model as model
from typing import Optional, List
from datetime import datetime
from src.tool.config_tool import increment_value, Key
from src.tool.hash_context import get_info_hash
from fastapi import HTTPException
from src.definitions import TaskProperty, TaskType

"""
======= 用户相关 =======
"""


async def user_email_exist(email_str):
    result = await engine.find_one(model.DBUser, model.DBUser.email == email_str)
    if result is not None:
        raise HTTPException(409, detail="email exists")


async def user_name_exist(username):
    result = await engine.find_one(model.DBUser, model.DBUser.username == username)
    if result is not None:
        raise HTTPException(409, detail="username exists")


async def phone_num_exist(phone_num):
    result = await engine.find_one(model.DBUser, model.DBUser.phone_number == phone_num)
    if result is not None:
        raise HTTPException(409, detail="phone_num exists")


async def create_user_info(email: str, username: str, password: str, phone_num: Optional[str] = None):
    try:
        await user_email_exist(email)
        await user_name_exist(username)
        user_num = increment_value(Key.user_num, 1)
        user = model.DBUser(num=user_num,
                            email=email,
                            username=username,
                            password=get_info_hash(password),
                            phone_number=phone_num,
                            create_time=datetime.now())
    except HTTPException as err:
        raise err
    else:
        await engine.save(user)


async def find_user_by_email(email: str):
    if email == "":
        return None
    user = await engine.find_one(model.DBUser, model.DBUser.email == email)
    return user


async def find_user_by_username(username: str):
    if username == "":
        return None
    user = await engine.find_one(model.DBUser, model.DBUser.username == username)
    return user


async def find_user_by_phonenum(phone_num: str):
    user = await engine.find_one(model.DBUser, model.DBUser.phone_number == phone_num)
    return user


""" 
====================
===== 任务相关 ======
====================
"""

"""
===== folder =====
"""


async def create_folder(doc_name: str):
    doc = model.DBFolder(name=doc_name, create_time=datetime.now())
    await engine.save(doc)


async def folder_remove_plan(doc_id: ObjectId, plan_id: ObjectId):
    doc = await engine.find_one(model.DBFolder, model.DBFolder.id == doc_id)
    if doc is None:
        raise HTTPException(404, detail="folder not exists")
    try:
        doc.tasks.remove(plan_id)  # if fail, raise ValueError
    except ValueError as err:
        raise HTTPException(404, detail="plan not in folder")
    await engine.save(doc)


async def del_folder(doc_id: ObjectId):
    doc = await engine.find_one(model.DBFolder, model.DBFolder.id == doc_id)
    if doc is None:
        raise HTTPException(404, detail="folder not exists")
    await engine.delete(doc)


async def folder_rename(doc_id: ObjectId, new_name: str):
    doc = await engine.find_one(model.DBFolder, model.DBFolder.id == doc_id)
    if doc is None:
        raise HTTPException(404, detail="folder not exists")
    doc.name = new_name
    await engine.save(doc)


async def folder_add_plan(doc_id: ObjectId, plan_id: ObjectId):
    doc = await engine.find_one(model.DBFolder, model.DBFolder.id == doc_id)
    if doc is None:
        raise HTTPException(404, detail="folder not exists")
    doc.tasks.append(plan_id)
    await engine.save(doc)


async def get_folder_name(doc_id: ObjectId):
    doc = await engine.find_one(model.DBFolder, model.DBFolder.id == doc_id)
    if doc is None:
        raise HTTPException(404, detail="folder not exists")
    return doc.name


async def get_folder_plan(doc_id: ObjectId):
    doc = await engine.find_one(model.DBFolder, model.DBFolder.id == doc_id)
    if doc is None:
        raise HTTPException(404, detail="folder not exists")
    return doc.tasks


async def get_folder_info(folder_id: ObjectId):
    folder = await engine.find_one(model.DBFolder, model.DBFolder.id == folder_id)
    if folder is None:
        raise HTTPException(404, detail="folder not exists")
    return folder

"""
===== plan =====
"""


async def create_plan(plan_name: str):
    plan = model.DBPlan(name=plan_name,
                        status=False,
                        create_time=datetime.now(),
                        start_time=None,
                        end_time=None)
    await engine.save(plan)
    return plan.id


async def del_plan(plan_id: ObjectId):
    plan = await engine.find_one(model.DBPlan, model.DBPlan.id == plan_id)
    if plan is None:
        raise HTTPException(404, detail="plan not exists")
    await engine.delete(plan)
    return plan_id


async def plan_rename(plan_id: ObjectId, new_name: str):
    plan = await engine.find_one(model.DBPlan, model.DBPlan.id == plan_id)
    if plan is None:
        raise HTTPException(404, detail="plan not exists")
    plan.name = new_name
    await engine.save(plan)
    return plan_id


async def plan_add_task_unit(plan_id: ObjectId, task_id: ObjectId):
    plan = await engine.find_one(model.DBPlan, model.DBPlan.id == plan_id)
    task = await engine.find_one(model.DBMinimumTaskUnit, model.DBMinimumTaskUnit.id == task_id)
    if plan is None or task is None:
        raise HTTPException(404, detail="plan not exists")
    plan.task_list.append(task.id)
    await engine.save(plan)
    return plan_id


async def plan_del_task_unit(plan_id: ObjectId, task_id: ObjectId):
    plan = await engine.find_one(model.DBPlan, model.DBPlan.id == plan_id)
    if plan is None:
        raise HTTPException(404, detail="plan not exists")
    try:
        plan.task_list.remove(task_id)
    except ValueError:
        raise HTTPException(404, detail="task not in plan")
    else:
        await engine.save(plan)
        return plan_id


async def plan_get_info(plan_id: ObjectId, attribute_name: str):
    plan = await engine.find_one(model.DBPlan, model.DBPlan.id == plan_id)
    if plan is None or not hasattr(plan, attribute_name):
        raise HTTPException(404, detail="plan not exists")
    return getattr(plan, attribute_name)


async def plan_multi_operation(plan_id: ObjectId,
                               add_task_list: Optional[List[ObjectId]] = None,
                               del_task_list: Optional[List[ObjectId]] = None,
                               status: Optional[bool] = None,
                               start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None):
    """
    修改单个用户的多个信息
    :param plan_id: Plan实例的id
    :param add_task_list: 要添加的task unit实例列表
    :param del_task_list: 要删除的task unit实例列表
    :param status: 改变的状态
    :param start_time: 改变开始时间
    :param end_time: 改变结束时间
    :return: plan.id
    """
    plan = await engine.find_one(model.DBPlan, model.DBPlan.id == plan_id)
    if plan is None:
        raise HTTPException(404, detail="plan not exists")
    if add_task_list is not None:
        unique_items = set(add_task_list) - set(plan.task_list)
        plan.task_list.extend(list(unique_items))
    if del_task_list is not None:
        for item in del_task_list:
            if item in plan.task_list:
                plan.task_list.remove(item)
            else:
                raise HTTPException(404, detail="delete task item not found")
    if status is not None:
        plan.status = status
    if start_time is not None:
        plan.start_time = start_time
    if end_time is not None:
        plan.end_time = end_time
    # check time setting
    if start_time or end_time:
        if plan.end_time is None or plan.start_time is None:
            raise HTTPException(404, detail="start_time/end_time setting error")
        elif plan.start_time > plan.end_time:
            raise HTTPException(404, detail="start_time/end_time setting error")
    await engine.save(plan)
    return plan.id


"""
===== task unit =====
"""


async def create_task_unit(task_name: str):
    task = model.DBMinimumTaskUnit(name=task_name,
                                   task_type=TaskType,
                                   task_property=TaskProperty,
                                   is_available=True,
                                   status=False)
    await engine.save(task)


async def del_task_unit(task_id: ObjectId):
    task = await engine.find_one(model.DBMinimumTaskUnit, model.DBMinimumTaskUnit.id == task_id)
    if task is None:
        raise HTTPException(404, detail="plan not exists")
    await engine.delete(task)
    return task_id


async def task_insert_action(task_id: ObjectId, action_name: str):
    if str == "":
        raise HTTPException(406, detail="unexpected action name")
    action = model.DBExecutableAction(name=action_name,
                                      status=False)
    task = await engine.find_one(model.DBMinimumTaskUnit, model.DBMinimumTaskUnit.id == task_id)
    if task is None:
        raise HTTPException(404, detail="plan not exists")
    task.sub_exec_block.append(action.id)
    return action.id


async def task_del_action(task_id: ObjectId, action_name: str):
    task = await engine.find_one(model.DBMinimumTaskUnit, model.DBMinimumTaskUnit.id == task_id)
    if task is None:
        raise HTTPException(404, detail="plan not exists")
    action = await engine.find_one(model.DBExecutableAction, model.DBExecutableAction.name == action_name)
    if action is None:
        raise HTTPException(404, detail="action not exists")
    task.sub_exec_block.remove(action.id)


async def task_multi_operation(task_id: ObjectId,
                               name: Optional[str] = None,
                               task_type: Optional[TaskType] = None,
                               task_property: Optional[TaskProperty] = None,
                               aval: Optional[bool] = None,
                               status: Optional[bool] = None,
                               add_action_list: Optional[List[ObjectId]] = None,
                               del_action_list: Optional[List[ObjectId]] = None):
    task = await engine.find_one(model.DBMinimumTaskUnit, model.DBMinimumTaskUnit.id == task_id)
    if task is None:
        raise HTTPException(404, detail="plan not exists")
    if name is not None:
        task.name = name
    if task_type is not None:
        task.task_type = task_type
    if task_property is not None:
        task.task_property = task_property
    if aval is not None:
        task.is_available = aval
    if status is not None:
        task.status = status
    if add_action_list is not None:
        unique_items = set(add_action_list) - set(task.sub_exec_block)
        task.sub_exec_block.extend(list(unique_items))
    if del_action_list is not None:
        for item in del_action_list:
            if item in task.sub_exec_block:
                task.sub_exec_block.remove(item)
            else:
                raise HTTPException(404, detail="delete action item not found")
