import uuid
from datetime import datetime
import src.database.pg_model as model
from sqlmodel import Session, select
from pydantic import EmailStr
from fastapi import HTTPException, Depends
from collections.abc import Generator
from src.config import engine
from typing import Annotated, List


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def start_db_session() -> Session:
    session = Session(engine)
    return session


def stop_db_session(session: Session):
    session.close()


SessionDep = Annotated[Session, Depends(get_db)]


async def check_email_exist(session: Session, email: str) -> bool:
    result = session.exec(select(model.User).where(model.User.email == email))
    return result.first() is not None


async def create_user_info(session: Session, data: dict):
    if not await check_email_exist(session, data["email"]):
        profile = model.UserProfile(create_time=datetime.now(), user=None)
        address = model.UserAddresses(user=None)
        user = model.User.model_validate(data)
        user.contact = address
        user.profile = profile
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    else:
        raise HTTPException(400, detail="email already exists in the system.")


async def inner_find_user_by_email(session: Session, email: str) -> model.User | None:
    result = session.exec(select(model.User).where(model.User.email == email))
    return result.first()


# async def delete_user(session: Session, email: str):
#     user = find_user_by_email(session, email)



async def update_user_profile(session: Session, user_email: str, data: dict):
    user = await inner_find_user_by_email(session, user_email)
    if user is None:
        raise HTTPException(404, detail="user not founded.")
    profile = user.profile
    profile = profile.model_validate(data)
    session.add(profile)
    session.commit()


async def get_user_addr(session: Session, user_email: str):
    user = await inner_find_user_by_email(session, user_email)
    if user is None:
        raise HTTPException(404, detail="user not founded.")
    addresses = user.contact
    return addresses


async def update_user_addr(session:Session, user_email: str,
                           addr_ptr: int, addr_data: str) -> model.UserAddresses:
    if addr_ptr > 10 or addr_ptr < 1:
        raise HTTPException(400, detail="addr pointer unavailable.")
    user = await inner_find_user_by_email(session, user_email)
    if user is None:
        raise HTTPException(404, detail="user not founded.")
    addresses = user.contact
    if not hasattr(addresses, f'addr{addr_ptr}'):
        addresses.num = addresses.num + 1
    setattr(addresses, f"addr{addr_ptr}", addr_data)
    session.add(addresses)
    session.commit()
    session.refresh(addresses)
    return addresses


async def delete_user_addr(session: Session, user_email: str,
                           addr_ptr: int) -> model.UserAddresses:
    if addr_ptr > 10 or addr_ptr < 1:
        raise HTTPException(400, detail="addr pointer unavailable.")
    user = await inner_find_user_by_email(session, user_email)
    if user is None:
        raise HTTPException(404, detail="user not founded.")
    addresses = user.contact
    if hasattr(addresses, f'addr{addr_ptr}'):
        addresses.num = addresses.num - 1
    setattr(addresses, f"addr{addr_ptr}", None)
    session.add(addresses)
    session.commit()
    session.refresh(addresses)
    return addresses


async def create_folder(session: Session, user_email: str, folder_info: dict) -> model.UserFolder:
    user = await inner_find_user_by_email(session, user_email)
    if user is None:
        raise HTTPException(404, detail="user not founded.")
    folder = model.UserFolder.model_validate(folder_info)
    folder.user = user
    session.add(folder)
    session.commit()
    session.refresh(folder)
    return folder


async def get_user_folder(session: Session, user_email: str) -> List[model.UserFolder]:
    user = await inner_find_user_by_email(session, user_email)
    if user is None:
        raise HTTPException(404, detail="user not founded.")
    return user.folder


async def inner_get_user_folder_by_id(session: Session, folder_id: str) -> model.UserFolder:
    folder = (session.exec(select(model.UserFolder).where(model.UserFolder.id == uuid.UUID(folder_id)))).first()
    return folder


async def update_folder_info(session: Session, user_email: str,
                             folder_id: str, folder_new_info: dict) -> model.UserFolder:
    folder = await inner_get_user_folder_by_id(session, folder_id)
    if folder is None:
        raise HTTPException(404, detail="user not founded.")
    if folder.user.email != user_email:
        raise HTTPException(400, detail="Unauthorized Operation.")
    folder = folder.model_validate(folder_new_info)
    session.add(folder)
    session.commit()
    session.refresh(folder)
    return folder


async def create_plan(session: Session, user_email: str,
                      folder_id: str, plan_data: dict) -> model.Plan:
    user = await inner_find_user_by_email(session, user_email)
    if user is None:
        raise HTTPException(404, detail="user not founded.")
    folder = await inner_get_user_folder_by_id(session, folder_id)
    task_list = []
    for task in plan_data["task_list"]:
        task_list.append(model.MinimumTaskUnit.model_validate(task))
    plan = model.Plan.model_validate(plan_data)
    plan.tasks.extend(task_list)
    plan.folder = folder
    plan.user = user
    plan.create_time = datetime.now()
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return plan


async def inner_get_plan_by_id(session: Session, plan_id: str) -> model.Plan:
    plan = (session.exec(select(model.Plan).where(model.Plan.id == uuid.UUID(plan_id)))).first()
    return plan


async def update_plan_profile(session: Session, user_email: str,
                              plan_id: str, plan_new_info: dict) -> model.Plan:
    plan = await inner_get_plan_by_id(session, plan_id)
    if plan is None:
        raise HTTPException(404, detail="plan not founded.")
    if plan.user.email != user_email:
        raise HTTPException(400, detail="Unauthorized Operation.")
    plan = plan.model_validate(plan_new_info)
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return plan


async def inner_get_tasks_by_plan_id(session: Session, plan_id: str) -> List[model.MinimumTaskUnit]:
    plan = await inner_get_plan_by_id(session, plan_id)
    if plan is None:
        raise HTTPException(404, detail="plan not founded.")
    return plan.tasks


async def inner_delete_plan(session: Session, plan: model.Plan):
    for task in plan.tasks:
        session.delete(task)
    session.delete(plan)


async def get_folder_plans(session:Session, folder_id: str) -> List[model.Plan]:
    folder = await inner_get_user_folder_by_id(session, folder_id)
    return folder.plans


async def delete_plan(session: Session, user_email: str,
                      plan_id: str, plan_name: str) -> Annotated[str, "plan_id"]:
    plan = await inner_get_plan_by_id(session, plan_id)
    if plan is None:
        raise HTTPException(404, detail="plan not founded.")
    if plan.user.email != user_email or plan.name != plan_name:
        raise HTTPException(400, detail="Unauthorized Operation.")
    for task in plan.tasks:
        session.delete(task)
    session.delete(plan)
    session.commit()
    return plan_id


async def inner_verify_plan_to_user(session: Session, user_email: str, plan_id: str) -> (model.User, model.Plan):
    user = await inner_find_user_by_email(session, user_email)
    plan = await inner_get_plan_by_id(session, plan_id)
    if user is None or plan is None:
        raise HTTPException(404, detail="data not founded.")
    plan = await inner_get_plan_by_id(session, plan_id)
    if plan.user.email != user_email:
        raise HTTPException(400, detail="Unauthorized Operation.")
    return user, plan


async def update_plan_info_by_id(session: Session, user_email: str, plan_id: str, plan_info: dict) -> model.Plan:
    user, plan = inner_verify_plan_to_user(session, user_email, plan_id)
    plan = plan.model_validate(plan_info)
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return plan


async def add_task(session: Session, user_email: str, plan_id: str, task_info: dict) -> model.MinimumTaskUnit:
    user, plan = inner_verify_plan_to_user(session, user_email, plan_id)
    task = model.MinimumTaskUnit.model_validate(task_info)
    task.plan = plan
    plan.tasks.append(task)
    session.add(plan)
    session.commit()
    session.refresh(task)
    return task


async def add_multi_tasks(session: Session, user_email: str, plan_id: str, task_list: List[dict]):
    user, plan = inner_verify_plan_to_user(session, user_email, plan_id)
    for task_info in task_list:
        task = model.MinimumTaskUnit.model_validate(task_info)
        task.plan = plan
        plan.tasks.append(task)
    session.add(plan)
    session.commit()


async def inner_find_task_by_id(session: Session, task_id: str) -> model.MinimumTaskUnit | None:
    task = (session.exec(select(model.MinimumTaskUnit).where(model.MinimumTaskUnit.id == uuid.UUID(task_id)))).first()
    return task


async def update_task(session: Session, user_email: str,
                      plan_id: str, task_id: str, task_info: dict) -> model.MinimumTaskUnit:
    inner_verify_plan_to_user(session, user_email, plan_id)
    task = await inner_find_task_by_id(session, task_id)
    if task is None:
        raise HTTPException(404, detail="task not founded.")
    if task.plan_id != plan_id:
        raise HTTPException(400, detail="Unauthorized Operation.")
    task = task.model_validate(task_info)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


async def delete_task(session: Session, user_email: str, plan_id: str, task_id: str) -> Annotated[str, "task_id"]:
    inner_verify_plan_to_user(session, user_email, plan_id)
    task = await inner_find_task_by_id(session, task_id)
    if task is None:
        raise HTTPException(404, detail="task not founded.")
    if task.plan_id != plan_id:
        raise HTTPException(400, detail="Unauthorized Operation.")
    session.delete(task)
    session.commit()
    return task_id


async def delete_user_folder(session: Session, user_email: str, folder_id: str) -> Annotated[str, "folder_id"]:
    user = await inner_find_user_by_email(session, user_email)
    folder = await inner_get_user_folder_by_id(session, folder_id)
    if user is None or folder_id is None:
        raise HTTPException(404, detail="user/folder not founded.")
    if folder.user.id != user.id:
        raise HTTPException(400, detail="Unauthorized Operation.")
    for plan in folder.plans:
        await inner_delete_plan(session, plan)
    session.delete(folder)
    session.commit()
    return folder_id


async def inner_delete_folder(session: Session, folder: model.UserFolder):
    for plan in folder.plans:
        await inner_delete_plan(session, plan)
    session.delete(folder)


async def delete_user(session: Session, user_email: str) -> Annotated[str, "user.email"]:
    user = await inner_find_user_by_email(session, user_email)
    if user is None:
        raise HTTPException(404, detail="user not founded.")
    for folder in user.folder:
        await inner_delete_folder(session, folder)
    session.delete(user.profile)
    session.delete(user.contact)
    session.delete(user)
    session.commit()
    return user_email
