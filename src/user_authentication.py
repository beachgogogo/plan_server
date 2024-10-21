from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from src.tool.time_tool import hash_from_time
from src.tool.hash_context import verify_info
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from model import TokenData, UserInfo
from database_method import find_user_by_id, find_user_by_email


SECRET_KEY = hash_from_time()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30    # 令牌维持30min


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def authenticate_user(email: str, password: str):
    user = await find_user_by_email(email)
    if user is None:
        return False
    if not verify_info(password, user["password"]):
        return False
    return str(user.id)


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
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except InvalidTokenError:
        raise credentials_exception
    if await find_user_by_id(token_data.user_id) is None:
        raise credentials_exception
    return token_data


# async def get_current_active_user(
#     current_user: Annotated[UserInfo, Depends(get_current_user)],
# ):
#     # if current_user.disabled:
#     #     raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user
