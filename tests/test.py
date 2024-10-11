from odmantic import Model, ObjectId
from datetime import datetime
from typing import List, Optional


from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hash_code1 = pwd_context.hash("a")
hash_code2 = pwd_context.hash("a")
print(hash_code1)
print(hash_code2)



