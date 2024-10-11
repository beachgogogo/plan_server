from typing import Optional, List, Dict
from src.definitions import Status
from fastapi.responses import ORJSONResponse


def response_data(data: Optional[Dict[str, any]],
                  message: Optional[str] = None,
                  status: Status = Status.FULL_SUCCEED) -> ORJSONResponse:
    """
    Args:
        data: 字段用于存放实际业务数据，如查询到的用户信息、商品列表等。
        status: 字段表示请求的状态，成功时为 “success”，失败时为 “error” 等类似标识，方便前端快速判断请求是否成功。
        message: 字段用于提供额外的信息，如失败时的错误原因、成功时的提示信息等。
    Returns:
        dict类型响应数据
    """
    resp = {
        "data": data,
        "status": status.value,
        "message": message
    }
    return ORJSONResponse([resp])


