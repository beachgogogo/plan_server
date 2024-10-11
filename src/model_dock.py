"""
用于提取数据库模型和fastapi模型信息为其他仅包含关键信息的模型，
防止出现携带大量信息不断传递的情况
"""
# import model
from database_model import DBUser
from model import UserInfo


def get_DBUser_info(user: DBUser):
    """
    将DBUser转换成dict格式
    :param user:
    :return: dict(email, password)
    """
    return {"email": user.email,
            "password": user.password}


def get_DBUser_info_to_UserInfo(user: DBUser):
    """
    将DBUser转换成UserInfo格式
    :param user:
    :return:
    """
    return UserInfo(email=user.email, username=user.username, phone_number=user.phone_number)
