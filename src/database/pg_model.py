from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
import uuid
from datetime import datetime
from src.definitions import Gender, Action
from typing import Optional, List, ClassVar, Literal, Dict
from enum import Enum


class Base(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    version: ClassVar[int] = 1


class UserBase(Base):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    username: str = Field(max_length=255)


class ItemBase(Base):
    name: str | None = None
    visitable: bool = True


class UserProfile(Base, table=True):
    profile_photo: str | None = None
    personalized_signature: str | None = None
    birthday: datetime | None = None
    gender: Gender | None = None
    create_time: datetime

    user: Optional["User"] | None = Relationship(back_populates="profile")


class UserAddresses(Base, table=True):
    addr_ptr: ClassVar[int] = 0
    num: int = 0
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
    user: Optional["User"] | None = Relationship(back_populates="contact")


class TaskType(str, Enum):
    CyclicTask = "CyclicTask"
    DBOneTimeTask = "DBOneTimeTask"


class MinimumTaskUnit(ItemBase, table=True):
    type_info: TaskType
    current_round: int | None = None
    period: datetime | None = None
    task_property: Literal["optional", "required"] = "required"
    start_time: datetime
    end_time: datetime
    is_finish: bool = False
    award_detail: str | None = None
    award_fulfill: bool = False
    sub_exec_block: str | None = Field(default=None, max_length=102400)

    plan_id: uuid.UUID | None = Field(default=None, foreign_key="plan.id")
    plan: Optional["Plan"] = Relationship(back_populates="tasks")


class Plan(Base, table=True):
    name: str = Field(max_length=255)
    visitable: bool = True
    is_finish: bool = False
    tasks: List[MinimumTaskUnit] | None = Relationship(back_populates="plan")
    award_detail: str | None = None
    award_fulfill: bool = False
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    create_time: datetime
    folder_id: uuid.UUID | None = Field(default=None, foreign_key="userfolder.id")
    user_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    folder: Optional["UserFolder"] = Relationship(back_populates="plans")
    user: Optional["User"] = Relationship(back_populates="plans")


class UserFolder(Base, table=True):
    name: str = Field(max_length=255)
    visitable: bool = True
    plans: List[Plan] | None = Relationship(back_populates="folder")
    create_time: datetime

    user_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="folder")


# class Activities(Base, table=True):
# # 非关系型数据库的特性没有类似列表的数据结构，如果不停的添加都会使操作数据主体不断变大，增加后期操作负担
# # 故暂时取消
#     info_list: List[str] = []
#     user: Optional["User"] = Relationship(back_populates="activities")


class User(UserBase, table=True):
    password: str
    phone_number: str | None = Field(default=None, max_length=11)

    profile_id: uuid.UUID | None = Field(default=None, foreign_key="userprofile.id")
    contact_id: uuid.UUID | None = Field(default=None, foreign_key="useraddresses.id")
    profile: UserProfile | None = Relationship(back_populates="user")
    contact: UserAddresses | None = Relationship(back_populates="user")
    folder: List[UserFolder] | None = Relationship(back_populates="user")
    plans: List[Plan] | None = Relationship(back_populates="user")
    # activities: Activities = Relationship(back_populates="user")




