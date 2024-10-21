import asyncio
from datetime import datetime, date
from pydantic import BaseModel
from odmantic import AIOEngine, Model, Reference, ObjectId


class Publisher(Model):
    name: str
    founded: int
    location: str


class BPublisher(BaseModel):
    rename: str
    founded: int
    location: str


class Book(Model):
    title: str
    pages: int
    publish_time: datetime
    publisher: Publisher = Reference()


class Music(Model):
    name: str


hachette = Publisher(name="Hachette Livre", founded=1826, location="FR")
harper = Publisher(name="HarperCollins", founded=1989, location="US")
copyer = BPublisher(rename="Tom", founded=1997, location="CHN")
music = Music(name="200%")
# hachette.model_update(harper, exclude={"rename"})
# print(hachette)


engine = AIOEngine(database="test")
loop = asyncio.get_event_loop()
start_time = datetime.now()
# loop.run_until_complete(engine.save_all([hachette, music]))
end_time = datetime.now()
print((end_time - start_time).microseconds)
loop.close()
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