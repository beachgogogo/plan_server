from typing import Optional, Dict, Union
from pydantic import BaseModel
from src.definitions import Status
from fastapi.responses import ORJSONResponse
import re


def response_data(data: Optional[Union[BaseModel, str, dict]] = None,
                  message: Optional[str] = None,
                  status: Status = Status.FULL_SUCCEED) -> ORJSONResponse:
    """
    Args:
        data: 字段用于存放实际业务数据，如查询到的用户信息、商品列表等。
        status: 除HTTP状态码外的内部状态信息
        message: 字段用于提供额外的信息，如失败时的错误原因、成功时的提示信息等。
    Returns:
        dict类型响应数据
    """
    # resp = RespData(data=data, message=message, status=status)
    if isinstance(data, BaseModel):
        resp = {
            "data": data.model_dump(),
            "status": status.value,
            "message": message
        }
    else:
        resp = {
            "data": data,
            "status": status.value,
            "message": message
        }
    # resp_json = jsonable_encoder(resp)
    return ORJSONResponse(resp)


def email_checking(email: str) -> bool:
    """
    邮箱账号字符串验证，如果符合邮箱账号规则返回true，否则返回false
    :param email:
    :return: bool
    """
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))
