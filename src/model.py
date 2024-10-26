from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Union, Dict
from datetime import datetime
from src.definitions import Gender


class User(BaseModel):
    num: Optional[int] = None
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


class UserAddress(BaseModel):
    uid: Optional[str] = None
    name: str
    province: str
    city: str
    district: str
    detailed_address: str
    postal_code: Optional[str] = None
    phone_number: str


class UserContactInfo(BaseModel):
    action_type: Literal["add", "delete", "update"] = Field(exclude=True)
    data: Dict[Literal["phone number", "address"]: Union[List[str], List[UserAddress], UserAddress]]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    待完善
    """
    user_id: Optional[str] = None


class NewPlanRecv(BaseModel):
    name: str
    task_list: List[str] = []
    status: bool
    parent_folder: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class TaskType(BaseModel):
    task_type: Literal["cyclic_task", "one_time_task"] = "one_time_task"
    start_time: datetime
    end_time: datetime
    # 以下是周期型使用参数
    current_round: Optional[int] = None
    period: Optional[datetime] = None
    is_available: bool = True


class ExecutableAction(BaseModel):
    """
    可执行操作
    name: 操作名称
    status: 操作状态 [已完成， 未完成]
    """
    name: str
    status: bool = False


class CyclicTask(BaseModel):
    type = "cyclic_task"
    current_round: int = 0
    period: datetime
    start_time: datetime
    end_time: datetime


class OneTimeTask(BaseModel):
    type = "one_time_task"
    start_time: datetime
    end_time: datetime


class Award(BaseModel):
    detail: Optional[str] = None
    is_fulfill: bool = False


class TaskUnit(BaseModel):
    name: str
    type_info: Union[CyclicTask, OneTimeTask]
    task_property: Literal["optional", "required"]
    is_available: bool = True
    status: bool = False
    award: Optional[Award] = None
    sub_exec_block: List[ExecutableAction] = []


class PlanInfo(BaseModel):
    plan_id: Optional[str] = None
    name: str
    task_list: List[str, TaskUnit] = []
    status: bool = True
    create_time: datetime
    award: Award
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class PlanCreateRecv(BaseModel):
    folder_name: str
    plan_name: str
    status: bool = True
    award_detail: Optional[Award] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class PlanDeleteRecv(BaseModel):
    folder_name: str
    plan_name: str


class PlanUpdateProfileRecv(BaseModel):
    plan_id: str
    plan_name: str
    status: bool = True
    award: Award
    start_time: Optional[datetime]
    end_time: Optional[datetime]


class Folder(BaseModel):
    name: str
    status: bool = True
    plans: List[str, PlanInfo] = []
    create_time: datetime


class UserFolderList(BaseModel):
    folder_list: List[Folder] = []


class FolderCreateRecv(BaseModel):
    folder_name: str
    status: bool


class FolderDeleteRecv(BaseModel):
    folder_name: str


class FolderUpdateRecv(BaseModel):
    old_name: str
    new_name: str
    status: bool = True

