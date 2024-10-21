from odmantic import Model, ObjectId, Reference
from typing import Optional, List
from datetime import datetime
from src.definitions import TaskType, TaskProperty, Gender, Action
from pydantic import ValidationError, model_validator
from src.tool.packaging_tool import email_checking


class DBExecutableAction(Model):
    """
    可执行操作
    name: 操作名称
    status: 操作状态 [已完成， 未完成]
    """
    name: str
    status: bool


class DBMinimumTaskUnit(Model):
    """
    最小任务单元模型
    name: 目标
    task_type: 任务类型
    task_property: 任务属性 [周期，可选]
    is_available: 当前任务使能状态
    status: 当前任务完成状态
    user: 归属用户
    sub_exec_block: 可执行块列表
    """
    name: str
    task_type: TaskType
    task_property: TaskProperty
    is_available: bool
    status: bool
    plan_id: ObjectId
    sub_exec_block: List[DBExecutableAction] = []


class DBPlan(Model):
    """
    计划模型
    name: 计划名
    task_list: 计划/最小任务单元序列号子节点列表
    user: 归属用户
    create_time: 创建时间
    """
    name: str
    parent_folder: Optional[ObjectId] = None
    task_list: List[ObjectId] = []
    status: bool
    create_time: datetime
    user_id: ObjectId
    award: List[str] = []
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class DBFolder(Model):
    """
    文件夹模型，可包含若干计划和文件夹
    name: 文件夹名称
    status: 公开状态
    tasks: 计划id列表
    docs: 文件夹id列表
    create_time: 时间
    """
    name: str
    status: bool = True
    tasks: List[ObjectId] = []
    folders: List[ObjectId] = []
    create_time: datetime


class DBUser(Model):
    schemaVersion: int = 1
    num: Optional[int] = None
    email: str
    username: str
    password: str
    profile: Reference()  # DBUserProfile
    contact: Reference()  # DBUserContact
    activities: Reference()  # DBUserActivities
    folder_list: Reference()  # DBUserFolderList

    @model_validator(mode="before")
    def check_email_form(cls, values):
        email = values.get("email", 0)
        if email_checking(email) is False:
            raise ValueError("email format is incorrect")
        return values


class DBUserProfile(Model):
    profile_photo: Optional[str] = None
    personalized_signature: Optional[str] = None
    birthday: Optional[datetime] = None
    gender: Optional[Gender] = None
    create_time: datetime


class DBUserContact(Model):
    phone_number: Optional[str] = None
    address: Optional[List[str]] = []


class DBAction(Model):
    time: datetime
    type: Action
    info: str


class DBUserActivities(Model):
    login_record: Optional[List[str]] = []
    actions: Optional[List[DBAction]] = []


class DBUserFolderList(Model):
    folder_list: List[DBFolder] = []
