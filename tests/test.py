from typing_extensions import Unpack

import asyncio
from datetime import datetime, date
from pydantic import BaseModel
from odmantic import AIOEngine, Model, Reference, ObjectId, EmbeddedModel
from typing import List, Literal, Dict


class Publisher(BaseModel):
    name: str
    founded: int
    location: str


class Book(BaseModel):
    title: str
    pages: int
    publish_time: datetime
    publisher: Publisher = Reference()


class Tester(Model):
    num: int
    publish_list: List[ObjectId] = []


class Tester2(BaseModel):
    publish_list: List[str] = []


class Music(Model):
    name: str

tester = Tester(num=3, publish_list=[ObjectId("6715fc608f18f2755899ce89"), ObjectId("6715fe3e3a3f578f596599fd"),
                               ObjectId("6715fe3e3a3f578f596599fe")])
hachette = Publisher(name="Hachette Livre", founded=1826, location="FR")
harper = Publisher(name="HarperCollins", founded=1989, location="US")
ha_dump = hachette.model_dump(exclude={"name"})
print(ha_dump)
ret = harper.model_validate(ha_dump)

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
