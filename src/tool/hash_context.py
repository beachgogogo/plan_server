from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_info(plain_info, hashed_info):
    return pwd_context.verify(plain_info, hashed_info)


def get_info_hash(info):
    return pwd_context.hash(info)
