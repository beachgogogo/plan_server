from odmantic import Model, ObjectId
from typing import Optional, List
from datetime import datetime
from src.definitions import TaskType, TaskProperty


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
    sub_exec_block: 可执行块列表
    """
    name: str
    task_type: TaskType
    task_property: TaskProperty
    is_available: bool
    status: bool
    sub_exec_block: List[ObjectId] = []


class DBPlan(Model):
    """
    计划模型
    name: 计划名
    task_list: 计划/最小任务单元序列号子节点列表
    create_time: 创建时间
    """
    name: str
    task_list: List[ObjectId] = []
    status: bool
    create_time: datetime
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class DBFolder(Model):
    """
    文件夹模型，可包含若干计划和文件夹
    name: 文件夹名称
    tasks: 计划id列表
    docs: 文件夹id列表
    create_time: 时间
    """
    name: str
    tasks: List[ObjectId] = []
    docs: List[ObjectId] = []
    create_time: datetime


class DBUser(Model):
    """
    用户模型
    num: 当前创建的第num个用户
    email: 邮箱\n
    username:\n
    password:\n
    create_time: datetime 创建时间\n
    phone_number:\n
    profile_photo: = 头像\n
    personalized_signature: 个性签名\n
    file_set: 拥有文件列表\n
    other: 待补充
    """
    num: int
    email: str
    username: str
    password: str
    create_time: datetime
    phone_number: Optional[str] = None
    profile_photo: Optional[str] = None
    personalized_signature: Optional[str] = None
    file_set: List[ObjectId] = []
