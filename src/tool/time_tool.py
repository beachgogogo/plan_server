import hashlib
from datetime import datetime, date
from typing import Optional


# 比较字符串函数
# 返回值： True相同，False不同
def compare_str(str1, str2):
    if (type(str1) != str) or (type(str2) != str):
        return False
    return str1 == str2


def hash_from_time():
    """
    根据当前时间戳生成SHA-256码
    :return: str类型SHA-256码
    """
    timestamp = datetime.now().timestamp()
    timestamp_str = str(timestamp)
    hash_object = hashlib.sha256(timestamp_str.encode())
    sha256_hash = hash_object.hexdigest()
    return sha256_hash


def hash_from_info(info: str):
    hash_object = hashlib.sha256(info.encode())
    sha256_hash = hash_object.hexdigest()
    return sha256_hash


def get_datetime(date_data: Optional[date] = None) -> datetime:
    ret_time = None
    if date_data is None:
        ret_time = datetime.combine(date.today(), datetime.min.time())
    else:
        ret_time = datetime.combine(date_data, datetime.min.time())
    return ret_time
