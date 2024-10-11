from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from src.tool.time_tool import hash_from_time
from src.tool.hash_context import verify_info
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from model import TokenData, UserInfo
from database_method import find_user_by_email
from model_dock import get_DBUser_info, get_DBUser_info_to_UserInfo


SECRET_KEY = hash_from_time()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30    # 令牌维持30s


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def authenticate_user(email: str, password: str):
    user = get_DBUser_info(await find_user_by_email(email))
    if not user:
        return False
    if not verify_info(password, user["password"]):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user_token(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = await find_user_by_email(token_data.email)
    if user is None:
        raise credentials_exception
    return token_data


# async def get_current_active_user(
#     current_user: Annotated[UserInfo, Depends(get_current_user)],
# ):
#     # if current_user.disabled:
#     #     raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user
