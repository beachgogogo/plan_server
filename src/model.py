import uuid

from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Union, Dict
from datetime import datetime
from src.definitions import Gender


class UserRegister(BaseModel):
    email: str
    username: str
    password: str
    phone_number: Optional[str] = None


class UserShortInfo(BaseModel):
    email: str
    username: str
    phone_number: Optional[str] = None


class UserInfo(BaseModel):
    email: str
    username: str
    profile_photo: Optional[str] = None
    personalized_signature: Optional[str] = None
    birthday: Optional[datetime] = None
    gender: Optional[Gender] = None
    create_time: datetime
    phone_number: Optional[str] = None


class UserProfileInfo(BaseModel):
    username: str
    personalized_signature: Optional[str] = None
    birthday: Optional[datetime] = None
    gender: Optional[Gender] = None


# class UserAddress(BaseModel):
#     uid: Optional[str] = None
#     name: str
#     province: str
#     city: str
#     district: str
#     detailed_address: str
#     postal_code: Optional[str] = None
#     phone_number: str


class UserAddressInfo(BaseModel):
    action_type: Literal["add", "delete", "update"] = Field(exclude=True)
    addr_ptr: int
    addr_data: str


class UserAddrRespInfo(BaseModel):
    addr_ptr: int = 0
    addr1: str | None = Field(default=None, max_length=1024)
    addr2: str | None = Field(default=None, max_length=1024)
    addr3: str | None = Field(default=None, max_length=1024)
    addr4: str | None = Field(default=None, max_length=1024)
    addr5: str | None = Field(default=None, max_length=1024)
    addr6: str | None = Field(default=None, max_length=1024)
    addr7: str | None = Field(default=None, max_length=1024)
    addr8: str | None = Field(default=None, max_length=1024)
    addr9: str | None = Field(default=None, max_length=1024)
    addr10: str | None = Field(default=None, max_length=1024)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    待完善
    """
    user_email: Optional[str] = None


class NewPlanRecv(BaseModel):
    name: str
    task_list: List[str] = []
    status: bool
    parent_folder: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class TaskUnit(BaseModel):
    id: uuid.UUID
    name: str
    type_info: Literal["CyclicTask", "DBOneTimeTask"] = "OneTimeTask"
    current_round: int | None = None
    period: datetime | None = None
    task_property: Literal["optional", "required"] = "required"
    start_time: datetime
    end_time: datetime
    is_finish: bool = True
    status: bool = False
    award_detail: str | None = None
    award_fulfill: bool = False
    sub_exec_block: str | None = None


class TaskUnitCreateRecv(BaseModel):
    plan_id: str
    name: str
    type_info: Literal["CyclicTask", "DBOneTimeTask"] = "OneTimeTask"
    current_round: int | None = None
    period: datetime | None = None
    task_property: Literal["optional", "required"] = "required"
    start_time: datetime
    end_time: datetime
    is_finish: bool = True
    status: bool = False
    award_detail: str | None = None
    award_fulfill: bool = False
    sub_exec_block: str | None = None


class TaskUnitUpdate(BaseModel):
    name: str
    type_info: Literal["CyclicTask", "DBOneTimeTask"] = "OneTimeTask"
    current_round: int | None = None
    period: datetime | None = None
    task_property: Literal["optional", "required"] = "required"
    start_time: datetime
    end_time: datetime
    is_finish: bool = True
    status: bool = False
    award_detail: str | None = None
    award_fulfill: bool = False
    sub_exec_block: str | None = None


class TaskUnitUpdateRecv(BaseModel):
    task_id: str
    plan_id: str
    data: TaskUnitUpdate


class TaskUnitDelRecv(BaseModel):
    plan_id: str
    task_id: str
    task_name: str


class PlanInfo(BaseModel):
    plan_id: Optional[str] = None
    name: str
    task_list: List[Union[str, TaskUnit]] = []
    status: bool = True
    create_time: datetime
    award_detail: str | None = None
    award_fulfill: bool = False
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class PlanCreateRecv(BaseModel):
    folder_id: str
    plan_name: str
    visitable: bool = True
    is_finish: bool = False
    award_detail: str | None = None
    award_fulfill: bool = False
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    task_list: List[TaskUnit] = []


class PlanDeleteRecv(BaseModel):
    plan_name: str
    plan_id: str


class PlanUpdateProfileRecv(BaseModel):
    plan_id: str
    plan_name: str
    visitable: bool = True
    is_finish: bool = False
    award_detail: str | None = None
    award_fulfill: bool = False
    start_time: Optional[datetime]
    end_time: Optional[datetime]


class Folder(BaseModel):
    id: uuid.UUID
    name: str
    visitable: bool = True
    plans: List[Union[str, PlanInfo]] = []
    create_time: datetime


class UserFolderList(BaseModel):
    folder_list: List[Folder] = []


class UserPlanList(BaseModel):
    plan_list: List[PlanInfo] = []


class UserTaskList(BaseModel):
    task_list: List[TaskUnit] = []


class UserTaskCreateList(BaseModel):
    plan_id: str
    task_list: List[TaskUnitCreateRecv] = []


class FolderCreateRecv(BaseModel):
    name: str
    visitable: bool


class FolderDeleteRecv(BaseModel):
    folder_id: str


class FolderUpdateRecv(BaseModel):
    folder_id: str
    name: str
    visitable: str
    status: bool = True

