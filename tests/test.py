import uvicorn
from fastapi import Depends, FastAPI
from fastapi.encoders import jsonable_encoder
from odmantic.session import AIOSession, AIOTransaction
from typing_extensions import Unpack

import asyncio
from datetime import datetime, date
from pydantic import BaseModel
from odmantic import AIOEngine, Model, Reference, ObjectId, EmbeddedModel
from typing import List, Literal, Dict, Generator, Annotated, Optional, ClassVar
from sqlmodel import SQLModel, Field, Relationship
import uuid


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



addr = UserAddresses(addr1="123123123")
addr_ptr_value = 2  # 假设的指针值
address = getattr(addr, f'addr{addr_ptr_value}') if hasattr(
    addr, f'addr{addr_ptr_value}') else None
print(address)

# class User(Base, table=True):
#     name: str = "root"
#
#
# user = User(version=2, name="tom")
# print(user)


# class Base(BaseModel):
#     version: int = 1
#
#
# class BasePublisher(Base):
#     name: str
#     founded: int
#     location: str
#
#
# class Publisher(BasePublisher):
#     out: Optional[str] = None
#
#
# class Book(BaseModel):
#     title: str
#     pages: int
#     publish_time: datetime
#     publisher: Publisher = Reference()
#
#
# class Tester(Model):
#     num: int
#     publish_list: List[ObjectId] = []
#     fisher: ObjectId
#
#
# class Tester2(BaseModel):
#     publish_list: List[str] = []
#
#
# class Music(Model):
#     name: str


# if __name__ == '__main__':
#     uvicorn.run("test:app", host="127.0.0.1", port=8080, reload=True)
#######
# loop = asyncio.get_event_loop()
# start_time = datetime.now()
# publisher = loop.run_until_complete(engine.save_all([peter, tester]))
# end_time = datetime.now()
# print((end_time - start_time).microseconds)
# start_time = datetime.now()
# ret_test = loop.run_until_complete(engine.find_one(Tester, Tester.num == 1))
# end_time = datetime.now()
# print((end_time - start_time).microseconds)
# print(f"ret_test: {ret_test}")
# loop.close()

# print(Book.model_fields)
# def func(data: Literal[Unpack[list(Book.model_fields.keys())]]):
#     print(data)
# try:
#     func(data="name")
# except BaseException as err:
#     print(err)


# tester = Tester(publish_list=[ObjectId("6715fc608f18f2755899ce89"), ObjectId("6715fe3e3a3f578f596599fd"),
#                               ObjectId("6715fe3e3a3f578f596599fe")])
#
#
# hachette = Publisher(name="Hachette Livre", founded=1826, location="FR")
# harper = Publisher(name="HarperCollins", founded=1989, location="US")
#
# books = [
#     Book(title="They Didn't See Us Coming", pages=304, publish_time=datetime.combine(date.today(), datetime.min.time()), publisher=hachette),
#     Book(title="This Isn't Happening", pages=256, publish_time=datetime.combine(date.today(), datetime.min.time()), publisher=hachette),
#     Book(title="Prodigal Summer", pages=464, publish_time=datetime.combine(date.today(), datetime.min.time()), publisher=harper),
# ]
#
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(engine.save_all(books))
# loop.close()

# _id = ObjectId("6715f5d775ca53023ee6d27a")
#
# loop = asyncio.get_event_loop()
# start_time = datetime.now()
# book = loop.run_until_complete(engine.find_one(Book, Book.pages == 304))
# end_time = datetime.now()
# print(type(book.publisher))
# print((end_time - start_time).microseconds)
# loop.close()

# 28610 long
# 13659 short
