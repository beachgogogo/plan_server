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


async def find_user_by_email(session: Session, email: str) -> model.User | None:
    result = session.exec(select(model.User).where(model.User.email == email))
    return result.first()


# async def delete_user(session: Session, email: str):
#     user = find_user_by_email(session, email)



async def update_user_profile(session: Session, user_email: str, data: dict):
    user = await find_user_by_email(session, user_email)
    if user is None:
        raise HTTPException(404, detail="user not founded.")
    profile = user.profile
    profile = profile.model_validate(data)
    session.add(profile)
    session.commit()


async def get_user_addr(session: Session, user_email: str):
    user = await find_user_by_email(session, user_email)
    if user is None:
        raise HTTPException(404, detail="user not founded.")
    addresses = user.contact
    return addresses


async def update_user_addr(session:Session, user_email: str,
                           addr_ptr: int, addr_data: str) -> model.UserAddresses:
    if addr_ptr > 10 or addr_ptr < 1:
        raise HTTPException(400, detail="addr pointer unavailable.")
    user = await find_user_by_email(session, user_email)
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
    user = await find_user_by_email(session, user_email)
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


async def create_folder(session: Session, user_email: str, folder_name: str) -> model.UserFolder:
    user = await find_user_by_email(session, user_email)
    if user is None:
        raise HTTPException(404, detail="user not founded.")
    folder = model.UserFolder(name=folder_name, create_time=datetime.now(), user=user)
    session.add(folder)
    session.commit()
    session.refresh(folder)
    return folder


async def get_user_folder(session: Session, user_email: str) -> List[model.UserFolder]:
    user = await find_user_by_email(session, user_email)
    if user is None:
        raise HTTPException(404, detail="user not founded.")
    return user.folder


async def get_user_folder_by_id(session: Session, folder_id: str) -> model.UserFolder:
    folder = (session.exec(select(model.UserFolder).where(model.UserFolder.id == uuid.UUID(folder_id)))).first()
    return folder


async def create_plan(session: Session, user_email: str, folder_id: str, plan_data: dict) -> model.Plan:
    user = await find_user_by_email(session, user_email)
    if user is None:
        raise HTTPException(404, detail="user not founded.")
    folder = await get_user_folder_by_id(session, folder_id)
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


async def get_plan_by_id(session: Session, plan_id: str) -> model.Plan:
    plan = (session.exec(select(model.Plan).where(model.Plan.id == uuid.UUID(plan_id)))).first()
    return plan


async def get_tasks_by_plan_id(session: Session, plan_id: str) -> List[model.MinimumTaskUnit]:
    plan = await get_plan_by_id(session, plan_id)
    if plan is None:
        return []
    return plan.tasks


async def verify_plan_to_user(session: Session,user_email: str, plan_id: str) -> (model.User, model.Plan):
    user = await find_user_by_email(session, user_email)
    plan = await get_plan_by_id(session, plan_id)
    if user is None or plan is None:
        raise HTTPException(404, detail="data not founded.")
    plan = await get_plan_by_id(session, plan_id)
    if plan.user.id != user.id:
        raise HTTPException(400, detail="Unauthorized Operation.")
    return user, plan


async def update_plan_info_by_id(session: Session,user_email: str, plan_id: str, plan_info: dict) -> model.Plan:
    user, plan = verify_plan_to_user(session, user_email, plan_id)
    plan = plan.model_validate(plan_info)
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return plan


async def add_task(session: Session,user_email: str, plan_id: str, task_info: dict) -> model.MinimumTaskUnit:
    user, plan = verify_plan_to_user(session, user_email, plan_id)

