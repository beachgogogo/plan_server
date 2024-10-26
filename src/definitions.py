from enum import Enum


"""
异常
"""


class DataDuplicationException(Exception):
    """数据重复异常 409"""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class DataNotFoundException(Exception):
    """找不到数据 404"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class NotAcceptableException(Exception):
    """
    无法根据客户端请求内容特性完成请求 406
    """
    def __init__(self, message):
        super().__init__(message)
        self.message = message


"""
相关定义
"""


class TaskType(Enum):
    """
    任务类型
    1 周期型任务
    2 单次型任务
    """
    CYCLICTASK = 0
    ONETIMETASK = 1


class TaskProperty(Enum):
    """
    任务属性
    可选(完成一项即可)
    必选(都得完成)
    """
    OPTIONAL = 0
    REQUIRED = 1


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class Action(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    VIEW = "view"
    DELETE = "delete"


class Status(Enum):
    """
    除RESTFUL状态码之外的状态记录。
    "FULL_SUCCEED": 完全成功
    "PARTIAL_SUCCEED": 部分成功
    "VALI_ERROR"：表示验证错误。通常发生在前端传入的数据不符合后端接口的要求，例如注册新用户时，
                          输入的密码不符合强度要求（长度、包含字符类型等方面的要求），或者必填字段缺失等情况。
    "AUTHN_ERROR"：认证错误。用于当用户试图访问需要认证的资源但认证失败时。
                              比如用户登录时提供了错误的用户名或密码，或者身份验证令牌（如 JWT 令牌）无效等情况。
    "AUTHZ_ERROR"：授权错误。与认证错误不同，授权错误发生在用户已经通过认证但没有足够的权限执行特定操作时。
                            例如，普通用户试图访问管理员才能访问的资源，或者用户没有足够的权限修改某些数据等情况。
    "RES_NOT_FOUND"：资源未找到。当客户端请求的特定资源（如某个用户、某个文件、某个数据库记录等）在服务器上不存在时使用。
                            例如，根据特定的用户 ID 查询用户信息，但数据库中不存在该 ID 对应的用户记录。
    "SERV_ERROR"：服务器错误。这表示在服务器端发生了内部错误，可能是由于程序逻辑错误、数据库故障、服务器过载等原因导致无法正常处理请求。
                     例如，在处理订单创建请求时，服务器内部的订单处理逻辑出现异常，导致无法创建订单。
    "NETWORK_ERROR"：网络错误。这种状态可以用来表示由于网络相关问题导致的请求失败，虽然这种情况通常更多地由 HTTP 协议本身的状态码
                     （如 503 - Service Unavailable，表示服务器暂时不可用，可能是网络问题导致）来体现，
                     但在返回数据中的状态字段也可以使用这个值来更详细地告知前端是网络方面的原因导致的失败。
                     例如，在进行文件上传时，由于网络中断导致上传失败。
    "TIMEOUT_ERROR"：超时错误。当服务器处理请求的时间超过了预先设定的时间限制时使用。
                      例如，一个长时间运行的数据库查询操作没有在规定的时间内返回结果，就可以标记为超时错误。
                      这种情况有助于前端区分是请求被拒绝（例如因为权限问题）还是仅仅是处理时间过长。
    """
    FULL_SUCCEED = "full - success"
    PARTIAL_SUCCEED = "partial - success"
    VALI_ERROR = "validation - error"
    AUTHN_ERROR = "authentication - error"
    AUTHZ_ERROR = "authorization - error"
    RES_NOT_FOUND = "resource - not - found"
    SERV_ERROR = "server - error"
    NETWORK_ERROR = "network - error"
    TIMEOUT_ERROR = "timeout - error"

