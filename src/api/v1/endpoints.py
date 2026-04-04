import os
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from sqlmodel import Field, Session, SQLModel, select
from time import time

from db.models import UserCredentials
from db.models import Token, User as UserTable
from db import engine


_jwt_secret = os.getenv("JWT_SECRET")
_jwt_alg = "HS256"

router = APIRouter()


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return ""


@router.get('/time', status_code=status.HTTP_200_OK)
async def test_method():
    '''Возвращает текущее время на сервере.'''
    return {'time': time()}


@router.post('/token', status_code=200, response_model=Token)
async def give_token(user: UserCredentials, request: Request):
    with Session(engine) as session:
        db_user = session.exec(
            select(UserTable).where(UserTable.username == user.username)
        ).first()
    if db_user is None:
        return JSONResponse(
            status_code=400,
            content={
                "error": "invalid_grant",
                "error_description": "Invalid username or password.",
            },
        )
    try:
        PasswordHasher().verify(db_user.password_hash, user.password)
    except (VerifyMismatchError, InvalidHashError):
        return JSONResponse(
            status_code=400,
            content={
                "error": "invalid_grant",
                "error_description": "Invalid username or password.",
            },
        )
    now = datetime.now(timezone.utc)
    exp = now + timedelta(days=30)
    ip = _client_ip(request)
    payload = {
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "ip": ip,
    }
    token = jwt.encode(payload, _jwt_secret, algorithm=_jwt_alg)
    return {"token": token}
