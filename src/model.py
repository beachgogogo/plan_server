from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class User(BaseModel):
    num: Optional[int] = None
    email: str
    username: str
    password: str
    phone_number: Optional[str] = None


class UserInfo(BaseModel):
    email: str
    username: str
    phone_number: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    待完善
    """
    email: Optional[str] = None


class Folder(BaseModel):
    name: str
    tasks: List[str] = []
    docs: List[str] = []
    create_time: datetime
