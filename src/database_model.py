from odmantic import Model, ObjectId, Reference, EmbeddedModel
from typing import Optional, List, Union, Literal
from datetime import datetime
from src.definitions import Gender, Action
from pydantic import model_validator
from src.tool.packaging_tool import email_checking


class DBExecutableAction(EmbeddedModel):
    """
    可执行操作
    name: 操作名称
    status: 操作状态 [已完成， 未完成]
    """
    version: int = 1
    name: str
    status: bool = False


class DBAward(EmbeddedModel):
    """
    :param detail: 奖励内容
    :param is_fulfill: 是否实现
    """
    version: int = 1
    detail: Optional[str] = None
    is_fulfill: bool = False


class DBCyclicTask(EmbeddedModel):
    type = "cyclic_task"
    current_round: int = 0
    period: datetime
    start_time: datetime
    end_time: datetime


class DBOneTimeTask(EmbeddedModel):
    type = "one_time_task"
    start_time: datetime
    end_time: datetime


class DBMinimumTaskUnit(Model):
    """
    最小任务单元模型
    version: 当前模型设计版本号
    name: 目标
    task_type: 任务类型
    task_property: 任务属性 [周期，可选]
    is_available: 当前任务使能状态
    status: 当前任务完成状态
    award: 奖励设置
    user: 归属用户
    sub_exec_block: 可执行块列表
    """
    version: int = 1
    name: str
    type_info: Union[DBCyclicTask, DBOneTimeTask]
    task_property: Literal["optional", "required"]
    is_available: bool = True
    status: bool = False
    award: Optional[DBAward] = None
    plan: Reference()
    user: Reference()
    sub_exec_block: List[DBExecutableAction] = []


class DBPlan(Model):
    """
    计划模型
    name: 计划名
    task_list: 计划/最小任务单元序列号子节点列表
    status: 公开状态
    phase: 当前阶段（未/已经超时）
    position： 完成情况（未/已完成）
    user: 归属用户
    create_time: 创建时间
    """
    version: int = 1
    name: str
    task_list: List[ObjectId] = []
    status: bool = True
    create_time: datetime
    user: Reference()
    award: DBAward
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


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


class DBUserAddress(EmbeddedModel):
    uid: str
    name: str
    province: str
    city: str
    district: str
    detailed_address: str
    postal_code: Optional[str] = None
    phone_number: str


class DBUserContact(Model):
    phone_number: Optional[str] = None
    address: Optional[List[DBUserAddress]] = []


class DBAction(EmbeddedModel):
    time: datetime
    type: Action
    info: str


class DBUserActivities(Model):
    login_record: Optional[List[str]] = []
    actions: Optional[List[DBAction]] = []


class DBFolder(EmbeddedModel):
    """
    文件夹模型，可包含若干计划和文件夹
    name: 文件夹名称
    status: 公开状态
    tasks: 计划id列表
    create_time: 时间
    """
    version: int = 1
    name: str
    status: bool = True
    plans: List[ObjectId] = []
    create_time: datetime


class DBUserFolderList(Model):
    folder_list: List[DBFolder] = []
