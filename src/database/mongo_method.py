from odmantic import Model
from odmantic.session import AIOSession

from src.config import engine
from odmantic import ObjectId
from src.database import mongo_model as model
from typing import Optional, List, Literal, Dict, Any, Generator, Annotated
from datetime import datetime
from fastapi import HTTPException, Depends
from src.definitions import TaskProperty, Action


async def get_db() -> Generator[AIOSession, None, None]:
    async with engine.session() as session:
        yield session


SessionDep = Annotated[AIOSession, Depends(get_db)]


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


async def create_user_info(user: dict):
    async with engine.session() as session:
        async with session.transaction() as transaction:
            try:
                if await transaction.find_one(model.DBUser,
                                              model.DBUser.email == user["email"]) is not None:
                    raise HTTPException(409, detail="email exists")
                if await transaction.find_one(model.DBUser,
                                              model.DBUser.username == user["username"]) is not None:
                    raise HTTPException(409, detail="email exists")
                current_time = datetime.now()
                user_profile = model.DBUserProfile(create_time=current_time)
                user_contact = model.DBUserContact(phone_number=user["phone_number"])
                user_activities = model.DBUserActivities(actions=[model.DBAction(time=current_time,
                                                                                 type=Action.CREATE,
                                                                                 info=str(locals()))])
                user = model.DBUser(email=user["email"],
                                    username=user["username"],
                                    password=user["password"],
                                    profile=user_profile,
                                    contact=user_contact,
                                    activities=user_activities,
                                    folder_list=model.DBUserFolderList())
            except HTTPException as err:
                await transaction.abort()
                raise err
            except BaseException as err:
                await transaction.abort()
                raise HTTPException(503, detail="server error")
            else:
                await transaction.save(user)
                await transaction.commit()


async def update_user_sign(user_id: str, sign: str):
    async with engine.transaction() as transaction:
        try:
            user = await transaction.find_one(model.DBUser,
                                              model.DBUser.id == ObjectId(user_id))
            if user is None:
                raise HTTPException(404, detail="data not found")
            profile = user.profile
            activities = user.activities
            profile.personalized_signature = sign
            activities.actions.append(model.DBAction(time=datetime.now(),
                                                     type=Action.UPDATE,
                                                     info={"personalized_signature": sign}))
        except HTTPException as err:
            await transaction.abort()
            raise err
        else:
            await transaction.save_all([profile, activities])
            await transaction.commit()


async def update_user_contact(user_id: str, act_type: Literal["add", "delete", "update"],
                              pf_data: Dict[str, Any]):
    """
    修改Profile中的单个字段
    规则：
        phone number只能使用update
        address中add类型的数据为List[UserAddress]
                delete类型的数据为List[str]
                update类型的数据为UserAddress
    :param act_type:
    :param user_id:
    :param pf_data:
    :return:
    """
    async with engine.transaction() as transaction:
        try:
            user = await transaction.find_one(model.DBUser,
                                              model.DBUser.id == ObjectId(user_id))
            if user is None:
                raise HTTPException(404, detail="data not found")
            user_contact = user.contact
            for field, data in pf_data:
                if field == "phone number" and act_type == "update":
                    user_contact.phone_number = data
                elif field == "address":
                    if act_type == "add":
                        user_contact.address.extend(data)
                    elif act_type == "delete":
                        for index, addr in enumerate(user_contact.address):
                            if addr.uid in data:
                                user_contact.address.pop(index)
                    elif act_type == "update":
                        for index, addr in enumerate(user_contact.address):
                            if addr.uid == data.uid:
                                user_contact.address[index].model_update(data)
            activities = user.activities
            activities.actions.append(model.DBAction(time=datetime.now(),
                                                     type=Action.UPDATE,
                                                     info=str(locals())))
        except ValueError as err:
            await transaction.abort()
            raise HTTPException(409, detail="value error")
        except HTTPException as err:
            await transaction.abort()
            raise err
        else:
            await transaction.save_all([user, user_contact, activities])
            await transaction.commit()


async def update_user_profile(user_id: str, profile_data: dict):
    async with engine.transaction() as transaction:
        try:
            user = await transaction.find_one(model.DBUser,
                                              model.DBUser.id == ObjectId(user_id))
            if user is None:
                raise HTTPException(404, detail="data not found")
            user.username = profile_data["username"]
            user_profile = user.profile
            user_profile.model_update(profile_data)
            activities = inner_user_update_actions(user.activities, Action.UPDATE,
                                                   info=str(profile_data))
        except HTTPException as err:
            await transaction.abort()
            raise err
        else:
            await transaction.save_all([activities, user, user_profile])
            await transaction.commit()


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
            activities = user.activities
            activities.actions.append(model.DBAction(time=datetime.now(),
                                                     type=Action.UPDATE,
                                                     info={"phone_number": phone_num}))
        except HTTPException as err:
            await transaction.abort()
            raise err
        else:
            await transaction.save_all([contact, activities])
            await transaction.commit()


async def del_user(user_id: str):
    async with engine.transaction() as transaction:
        try:
            user = await transaction.find_one(model.DBUser,
                                              model.DBUser.id == ObjectId(user_id))
            if user is None:
                raise HTTPException(404, detail="data not found")
            await del_all_folder(user_id)
            profile = user.profile
            contact = user.contact
            activities = user.activities
            folder_list = user.folder_list
            await transaction.delete(folder_list)
            await transaction.delete(activities)
            await transaction.delete(contact)
            await transaction.delete(profile)
            await transaction.delete(user)
        except HTTPException as err:
            await transaction.abort()
            raise err
        except BaseException:
            await transaction.abort()
            raise HTTPException(503, "server error")
        else:
            await transaction.commit()


async def find_user_by_email(email: str):
    try:
        user = await engine.find_one(model.DBUser, model.DBUser.email == email)
    except BaseException:
        raise HTTPException(503, detail="database error")
    else:
        return user


async def find_user_by_username(username: str):
    try:
        user = await engine.find_one(model.DBUser, model.DBUser.username == username)
    except BaseException:
        raise HTTPException(503, detail="database error")
    else:
        return user


async def find_user_by_phonenum(phone_num: str):
    async with engine.transaction() as transaction:
        try:
            contact = await transaction.find_one(model.DBUserContact, model.DBUserContact.phone_number == phone_num)
            user = await transaction.find_one(model.DBUser, model.DBUser.contact == contact.id)
        except BaseException:
            raise HTTPException(503, detail="database error")
        else:
            return user


async def find_user_by_id(user_id: str):
    user = await engine.find_one(model.DBUser, model.DBUser.id == ObjectId(user_id))
    return user


def inner_user_update_actions(activities: model.DBUserActivities,
                              action_type: Action,
                              info: str,
                              time: Optional[datetime] = None) -> model.DBUserActivities:
    if time is None:
        time = datetime.now()
    activities.actions.append(model.DBAction(time=time,
                                             type=action_type,
                                             info=info))
    return activities


""" 
====================
===== 任务相关 ======
====================
"""

"""
===== folder =====
"""


async def create_folder(user_id: str, folder_name: str, status: bool):
    async with engine.transaction() as transaction:
        try:
            user = await transaction.find_one(model.DBUser,
                                              model.DBUser.id == ObjectId(user_id))
            if user is None:
                raise HTTPException(404, detail="data not found")
            current_time = datetime.now()
            fd_list = user.folder_list
            folder = model.DBFolder(name=folder_name,
                                                      status=status,
                                                      create_time=current_time)
            fd_list.folder_list.append(folder)
            activities = user.activities
            activities.actions.append(model.DBAction(time=current_time,
                                                     type=Action.UPDATE,
                                                     info={"folder_name": folder_name}))
        except HTTPException as err:
            await transaction.abort()
            raise err
        except BaseException:
            await transaction.abort()
            raise HTTPException(503, "server error")
        else:
            await transaction.save_all([fd_list, activities])
            await transaction.commit()
            return folder.model_dump_json()


async def folder_remove_plan(user_id: str, folder_name: str, plan_name: str):
    async with engine.transaction() as transaction:
        try:
            user = await transaction.find_one(model.DBUser,
                                              model.DBUser.id == ObjectId(user_id))
            if user is None:
                raise HTTPException(404, detail="data not found")
            fd_list = user.folder_list
            for fd in fd_list.folder_list:
                if fd.name == folder_name:
                    plan = transaction.find_one(model.DBPlan, model.DBPlan.id.in_(fd.plans),
                                                model.DBPlan.name == plan_name)
                    await inner_del_plan_by_id(str(plan.id))
        except HTTPException as err:
            await transaction.abort()
            raise err
        except ValueError:
            await transaction.abort()
            raise HTTPException(404, detail="plan not in folder")
        else:
            # save
            await transaction.commit()


async def del_all_folder(user_id: str):
    async with engine.transaction() as transaction:
        try:
            user = await transaction.find_one(model.DBUser,
                                              model.DBUser.id == ObjectId(user_id))
            if user is None:
                raise HTTPException(404, detail="data not found")
            folder_list = user.folder_list
            for fd in folder_list.folder_list:
                for plan_id in fd.plans:
                    await inner_del_plan_by_id(plan_id)
                folder_list.folder_list.remove(fd)
            act = inner_user_update_actions(user.activities, Action.DELETE,
                                            info=str(locals()))
        except HTTPException as err:
            await transaction.abort()
            raise err
        else:
            transaction.save_all([act, folder_list])
            await transaction.commit()


async def del_folder(user_id: str, folder_name: str):
    async with engine.transaction() as transaction:
        try:
            user = await transaction.find_one(model.DBUser,
                                              model.DBUser.id == ObjectId(user_id))
            if user is None:
                raise HTTPException(404, detail="data not found")
            folder_list = user.folder_list
            is_find = False
            for fd in folder_list.folder_list:
                if fd.name == folder_name:
                    for plan_id in fd.plans:
                        await inner_del_plan_by_id(plan_id)
                    folder_list.folder_list.remove(fd)
                    is_find = True
                    break
            if is_find is False:
                raise HTTPException(404, detail="folder not exists")
            act = inner_user_update_actions(user.activities, Action.DELETE,
                                            info=str(locals()))
        except HTTPException as err:
            await transaction.abort()
            raise err
        else:
            transaction.save_all([act, folder_list])
            await transaction.commit()


async def get_all_folder(user_id: str):
    async with engine.transaction() as transaction:
        user = await transaction.find_one(model.DBUser,
                                          model.DBUser.id == ObjectId(user_id))
        if user is None:
            raise HTTPException(404, detail="data not found")
        fd_list = user.folder_list
        return fd_list.model_dump_json()


async def folder_update_info(user_id: str, old_name: str, new_name: str, status: bool):
    async with engine.transaction() as transaction:
        try:
            user = await transaction.find_one(model.DBUser,
                                              model.DBUser.id == ObjectId(user_id))
            if user is None:
                raise HTTPException(404, detail="data not found")
            fd_list = user.folder_list
            is_find = False
            for fd in fd_list.folder_list:
                if fd.name == old_name:
                    fd.name = new_name
                    fd.status = status
                    is_find = True
                    break
            if is_find is False:
                raise HTTPException(404, detail="folder not exists")
            act = inner_user_update_actions(user.activities, Action.UPDATE, str(locals()))
        except HTTPException as err:
            await transaction.abort()
            raise err
        except ValueError:
            await transaction.abort()
            raise HTTPException(409, detail="value error")
        else:
            await transaction.commit()
            await transaction.save_all([fd_list, act])


async def find_folder_by_name(user_id: str, folder_name: str):
    async with engine.transaction() as transaction:
        try:
            user = await transaction.find_one(model.DBUser,
                                              model.DBUser.id == ObjectId(user_id))
            if user is None:
                raise HTTPException(404, detail="data not found")
            fd_idx = inner_find_folder_by_name(user.folder_list, folder_name)
            fd_data = user.folder_list.folder_list[fd_idx]
        except HTTPException as err:
            await transaction.abort()
            raise err
        else:
            await transaction.commit()
            return fd_data.model_dump_json(exclude={"version"})


def inner_find_folder_by_name(folder_list: model.DBUserFolderList,
                              folder_name: str) -> Optional[int]:
    """
    查找是否存在对应folder，如果有返回对应索引
    :param folder_list:
    :param folder_name:
    :return:
    """
    index = None
    for idx, fd in enumerate(folder_list.folder_list):
        if fd.name == folder_name:
            index = idx
            break
    return index


"""
===== plan =====
"""


async def create_plan(user_id: str, folder_name: str, plan_name: str,
                      award_detail: str, status: bool):
    async with engine.transaction() as transaction:
        try:
            user = await transaction.find_one(model.DBUser,
                                              model.DBUser.id == ObjectId(user_id))
            if user is None:
                raise HTTPException(404, detail="user not found")
            fd_list = user.folder_list
            fd_idx = inner_find_folder_by_name(fd_list, folder_name)
            if fd_idx is None:
                raise HTTPException(404, detail="folder not found")
            current_time = datetime.now()
            plan = model.DBPlan(name=plan_name,
                                create_time=current_time,
                                user=user,
                                status=status,
                                award=model.DBAward(detail=award_detail))
            fd_list.folder_list[fd_idx].plans.append(plan)
            action = inner_user_update_actions(user.activities, Action.CREATE,
                                               str(locals()), current_time)
        except HTTPException as err:
            await transaction.abort()
            raise err
        else:
            await transaction.save_all([fd_list, action])
            await transaction.commit()
            return plan.model_dump_json()


async def inner_del_plan_by_id(plan_id: str):
    plan = await engine.find_one(model.DBPlan, model.DBPlan.id == plan_id)
    if plan is None:
        raise HTTPException(404, detail="plan not exists")
    task_list = engine.find(model.DBMinimumTaskUnit,
                            model.DBMinimumTaskUnit.id.in_(plan.task_list))
    for task in task_list:
        await engine.delete(task)
    await engine.delete(plan)


async def plan_update_profile(user_id:str, plan_id: str, plan_name:str, status: bool,
                              award_detail: str, fulfill: bool,
                              start_time: datetime, end_time: datetime):
    async with engine.transaction() as transaction:
        user = transaction.find_one(model.DBUser,
                                    model.DBUser.id == ObjectId(user_id))
        plan = transaction.find_one(model.DBPlan,
                                    model.DBPlan.id == ObjectId(plan_id),
                                    model.DBPlan.user == ObjectId(user_id))
        if user is None or plan is None:
            transaction.abort()
            raise HTTPException(404, detail="data not exists")
        plan.name = plan_name
        plan.status = status
        plan.award.detail = award_detail
        plan.award.is_fulfill = fulfill
        plan.start_time = start_time
        plan.end_time = end_time
        activities = inner_user_update_actions(user.activities, Action.UPDATE,
                                               info=str(locals()),
                                               time=datetime.now())
        transaction.save_all([plan, activities])
        transaction.commit()


async def get_plan_info_by_name(user_id: str, folder_name: str, plan_name: str):
    async with engine.transaction() as transaction:
        try:
            user = await transaction.find_one(model.DBUser,
                                              model.DBUser.id == ObjectId(user_id))
            fd_idx = inner_find_folder_by_name(user.folder_list, folder_name)
            plan = transaction.find_one(model.DBPlan,
                                        model.DBPlan.id.in_(user.folder_list.folder_list[fd_idx].plans),
                                        model.DBPlan.name == plan_name)
            if plan is None:
                raise HTTPException(404, detail="plan not found")
        except HTTPException as err:
            await transaction.abort()
            raise err
        else:
            await transaction.commit()
            return plan.model_dump_json(exclude={"version", "user"})


async def get_plan_info_by_id(plan_id: str):
    try:
        plan = await engine.find_one(model.DBPlan,
                                     model.DBPlan.id == ObjectId(plan_id))
    except ValueError as err:
        raise HTTPException(404, detail="plan not found")
    else:
        return plan.model_dump_json(exclude={"version", "user"})


async def plan_get_info(plan_id: ObjectId, attribute_name: str):
    plan = await engine.find_one(model.DBPlan, model.DBPlan.id == plan_id)
    if plan is None or not hasattr(plan, attribute_name):
        raise HTTPException(404, detail="plan not exists")
    return getattr(plan, attribute_name)


"""
===== task unit =====
"""


async def create_task_unit(user_id: str, plan_name: str,
                           task_name: str, task_property: Literal["optional", "required"],
                           table_action_list: List[str],
                           task_type: Literal["cyclic_task", "one_time_task"],
                           start_time: datetime, end_time: datetime,
                           current_round: Optional[int], period: Optional[datetime],
                           is_available: bool):
    async with engine.transaction() as transaction:
        try:
            user = await transaction.find_one(model.DBUser,
                                              model.DBUser.id == user_id)
            if user is None:
                raise HTTPException(404, detail="data not found")
            plan = await transaction.find_one(model.DBPlan,
                                              model.DBPlan.user == user_id, model.DBPlan.name == plan_name)
            if plan is None:
                raise HTTPException(404, detail="plan not found")
            type_ins = None
            if task_type == "cyclic_task":
                type_ins = model.DBCyclicTask(current_round=current_round,
                                              period=period,
                                              start_time=start_time,
                                              end_time=end_time)
            else:
                type_ins = model.DBOneTimeTask(start_time=start_time,
                                               end_time=end_time)
            table_list = []
            for table_action_str in table_action_list:
                table_list.append(model.DBExecutableAction(name=table_action_str))
            task = model.DBMinimumTaskUnit(name=task_name,
                                           type_info=type_ins,
                                           task_property=TaskProperty,
                                           is_available=True,
                                           plan=plan.id,
                                           sub_exec_block=table_list)
            plan.task_list.append(task.id)
            action = inner_user_update_actions(user.activities, Action.CREATE,
                                               info=str(locals()))
        except HTTPException as err:
            await transaction.abort()
            raise err
        else:
            await transaction.save_all([user, plan, task, action])
            await transaction.commit()


async def del_task_by_id(user_id: str, plan_id: str, task_unit_id: str):
    async with engine.transaction() as transaction:
        try:
            task = await transaction.find_one(model.DBMinimumTaskUnit,
                                              model.DBMinimumTaskUnit.id == ObjectId(task_unit_id),
                                              model.DBMinimumTaskUnit.plan == ObjectId(plan_id),
                                              model.DBMinimumTaskUnit.user == ObjectId(user_id))
            if task is None:
                raise HTTPException(404, detail="plan not exists")
            plan = task.plan
            plan.task_list.remove(task_unit_id)
        except HTTPException as err:
            transaction.abort()
            raise err
        else:
            transaction.save_all([task, plan])
            transaction.commit()


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


async def get_task_by_id(task_id: str):
    task = await engine.find_one(model.DBMinimumTaskUnit, model.DBMinimumTaskUnit.id == task_id)
    if task is None:
        raise HTTPException(404, detail="plan not exists")
    return task.model_dump_json(exclude={"version", "plan", "user"})


"""
base
"""


def str_to_objectid(data: str):
    return ObjectId(data)
