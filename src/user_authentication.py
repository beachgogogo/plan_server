from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from src.tool.time_tool import hash_from_time
from src.tool.hash_context import verify_info
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from model import TokenData
# from src.database.mongo_method import find_user_by_id, find_user_by_email
from src.database.pg_method import find_user_by_email, start_db_session, stop_db_session


SECRET_KEY = hash_from_time()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30    # 令牌维持30min


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def authenticate_user(email: str, password: str):
    session = start_db_session()
    user = await find_user_by_email(session, email)
    stop_db_session(session)
    if user is None:
        return False
    if not verify_info(password, user.password):
        return False
    return str(user.email)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user_token(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    """
    仅做验证，返回仅带用户email的Token
    :param token:
    :return:
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
        token_data = TokenData(user_email=user_email)
    except InvalidTokenError:
        raise credentials_exception
    session = start_db_session()
    if await find_user_by_email(session, token_data.user_email) is None:
        raise credentials_exception
    stop_db_session(session)
    return token_data


GetToken = Annotated[TokenData, Depends(get_current_user_token)]

# async def get_current_active_user(
#     current_user: Annotated[UserInfo, Depends(get_current_user)],
# ):
#     # if current_user.disabled:
#     #     raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user
