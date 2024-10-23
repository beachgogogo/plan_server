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


class Folder(BaseModel):
    name: str
    tasks: List[str] = []
    docs: List[str] = []
    create_time: datetime


class FolderUpdateInfo(BaseModel):
    """
    待完善
    """
    folder_name: str


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
