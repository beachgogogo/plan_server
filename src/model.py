from pydantic import BaseModel
from typing import Optional, List
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


class PlanUID(BaseModel):
    plan_id: str
