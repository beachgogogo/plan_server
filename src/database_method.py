from odmantic.exceptions import DocumentParsingError
from odmantic import Model
from src.config import engine
from odmantic import ObjectId
from src import database_model as model
from typing import Optional, List, Union
from datetime import datetime
from src.tool.config_tool import increment_value, Key
from fastapi import HTTPException
from src.definitions import TaskProperty, TaskType, Action
from src import model as pyt_model

"""
======= 用户相关 =======
"""


async def user_email_exist(email_str: str):
    result = await engine.find_one(model.DBUser, model.DBUser.email == email_str)
    if result is not None:
        raise HTTPException(409, detail="email exists")


async def user_name_exist(username: str):
    result = await engine.find_one(model.DBUser, model.DBUser.username == username)
    if result is not None:
        raise HTTPException(409, detail="username exists")


async def phone_num_exist(phone_num: str):
    result = await engine.find_one(model.DBUserContact, model.DBUserContact.phone_number == phone_num)
    if result is not None:
        raise HTTPException(409, detail="phone_num exists")


async def count_coll_num(ins: Model):
    return await engine.count(ins)


async def create_user_info(user: pyt_model.User):
    async with engine.transaction() as transaction:
        try:
            if await transaction.find_one(model.DBUser,
                                          model.DBUser.email == user.email) is None:
                raise HTTPException(409, detail="email exists")
            if await transaction.find_one(model.DBUser,
                                          model.DBUser.username == user.username) is None:
                raise HTTPException(409, detail="email exists")
            current_time = datetime.now()
            user_profile = model.DBUserProfile(create_time=current_time)
            user_contact = model.DBUserContact(phone_number=user.phone_number)
            user_activities = model.DBUserActivities(actions=[model.DBAction(time=current_time,
                                                                             type=Action,
                                                                             info=str(locals()))])
            user = model.DBUser(email=user.email,
                                username=user.username,
                                password=user.password,
                                profile=user_profile,
                                contact=user_contact,
                                activities=user_activities,
                                folder_list=model.DBUserFolderList())
        except HTTPException as err:
            transaction.abort()
            raise err
        except BaseException as err:
            transaction.abort()
            raise HTTPException(503, detail="server error")
        else:
            await transaction.save(user)
            await transaction.commit()


async def update_user_sign(user_id: str, sign: str):
    async with engine.transaction() as transaction:
        try:
            user = await transaction.find_one(model.DBUser,
                                              model.DBUser.id == user_id)
            if user is None:
                raise HTTPException(404, detail="data not found")
            profile = user.profile
            profile.personalized_signature = sign
        except HTTPException as err:
            transaction.abort()
            raise err
        else:
            transaction.save(profile)
            transaction.commit()


async def update_user_profile(user_id: str, profile_info: pyt_model.UserProfileInfo):
    async with engine.transaction() as transaction:
        try:
            user = await transaction.find_one(model.DBUser,
                                              model.DBUser.id == user_id)
            if user is None:
                raise HTTPException(404, detail="data not found")
            user.username = profile_info.username
            user_profile = user.profile
            user_profile.model_update(profile_info, exclude={"username"})
        except ValueError as err:
            transaction.abort()
            raise HTTPException(409, detail="value error")
        except HTTPException as err:
            transaction.abort()
            raise err
        else:
            transaction.save_all([user, user_profile])
            transaction.commit()


async def update_user_phone_num(user_id: str, phone_num: str):
    async with engine.transaction() as transaction:
        try:
            if await transaction.find_one(model.DBUserContact,
                                          model.DBUserContact.phone_number == phone_num) is not None:
                raise HTTPException(409, "phone number exist")
            user = await transaction.find_one(model.DBUser,
                                              model.DBUser.id == user_id)
            if user is None:
                raise HTTPException(404, detail="data not found")
            contact = user.contact
            contact.phone_number = phone_num
        except HTTPException as err:
            transaction.abort()
            raise err
        else:
            transaction.save(contact)
            transaction.commit()


async def find_user_by_email(email: str):
    try:
        user = await engine.find_one(model.DBUser, model.DBUser.email == email)
    except BaseException:
        raise HTTPException(503, detail="server error")
    else:
        return user


async def find_user_by_username(username: str):
    try:
        user = await engine.find_one(model.DBUser, model.DBUser.username == username)
    except BaseException:
        raise HTTPException(503, detail="server error")
    else:
        return user


async def find_user_by_phonenum(phone_num: str):
    async with engine.transaction() as transaction:
        try:
            contact = await engine.find_one(model.DBUserContact, model.DBUserContact.phone_number == phone_num)
            user = await engine.find_one(model.DBUser, model.DBUser.contact == contact.id)
        except BaseException:
            raise HTTPException(503, detail="server error")
        else:
            return user


async def find_user_by_id(user_id: str):
    user = await engine.find_one(model.DBUser, model.DBUser.id == ObjectId(user_id))
    return user


""" 
====================
===== 任务相关 ======
====================
"""

"""
===== folder =====
"""


async def create_folder(user_email: str, doc_name: str):
    folder = model.DBFolder(name=doc_name, create_time=datetime.now())
    user = await find_user_by_email(user_email)
    user.file_set.append(folder)
    await engine.save_all([folder, user])
    return folder.id


async def folder_remove_plan(doc_id: ObjectId, plan_id: ObjectId):
    doc = await engine.find_one(model.DBFolder, model.DBFolder.id == doc_id)
    if doc is None:
        raise HTTPException(404, detail="folder not exists")
    try:
        doc.tasks.remove(plan_id)  # if fail, raise ValueError
    except ValueError as err:
        raise HTTPException(404, detail="plan not in folder")
    await engine.save(doc)


async def del_folder(folder_id: ObjectId):
    folder = await engine.find_one(model.DBFolder, model.DBFolder.id == folder_id)
    if folder is None:
        raise HTTPException(404, detail="folder not exists")
    await engine.delete(folder)
    return folder.id


async def del_folder_by_user(user_email: str, folder_id: ObjectId):
    user = await find_user_by_email(user_email)
    if folder_id not in user.file_set:
        raise HTTPException(404, detail="folder not in user set")
    folder_id = await del_folder(folder_id)
    await engine.save(user)
    return folder_id


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


async def find_folder_by_name(folder_name: str):
    folder = await engine.find_one(model.DBFolder, model.DBFolder.name == folder_name)
    if folder is None:
        raise HTTPException(404, detail="folder not exists")
    return folder


async def find_folder_name(folder_id: ObjectId):
    folder = await engine.find_one(model.DBFolder, model.DBFolder.id == folder_id)
    if folder is None:
        raise HTTPException(404, detail="folder not exists")
    return folder.name


async def find_folder_plan(folder_id: ObjectId):
    folder = await engine.find_one(model.DBFolder, model.DBFolder.id == folder_id)
    if folder is None:
        raise HTTPException(404, detail="folder not exists")
    return folder.tasks


async def find_folder_info(folder_id: ObjectId):
    folder = await engine.find_one(model.DBFolder, model.DBFolder.id == folder_id)
    if folder is None:
        raise HTTPException(404, detail="folder not exists")
    return folder


"""
===== plan =====
"""


async def create_plan_by_name(plan_name: str):
    plan = model.DBPlan(name=plan_name,
                        status=False,
                        create_time=datetime.now(),
                        start_time=None,
                        end_time=None)
    await engine.save(plan)
    return plan.id


async def create_plan_by_doc(doc_data: dict):
    if doc_data["parent_folder"] is not None:
        doc_data["parent_folder"] = ObjectId(doc_data["parent_folder"])
    try:
        doc_data["create_time"] = str(datetime.now())
        plan = model.DBPlan.model_validate_doc(doc_data)
    except DocumentParsingError:
        raise HTTPException(406, "could not save to database")
    await engine.save(plan)
    return plan.model_dump_json()


async def del_plan(plan_id: Union[ObjectId, str]):
    id_copy = plan_id
    if type(plan_id) is str:
        id_copy = ObjectId(plan_id)
    plan = await engine.find_one(model.DBPlan, model.DBPlan.id == id_copy)
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


"""
base
"""


def str_to_objectid(data: str):
    return ObjectId(data)
