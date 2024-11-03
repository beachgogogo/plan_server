from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from src.model import Token
from src.user_authentication import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from datetime import timedelta


login_router = APIRouter()


@login_router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user_email = await authenticate_user(form_data.username, form_data.password)
    if not user_email:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

