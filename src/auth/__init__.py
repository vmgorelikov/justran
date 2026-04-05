import os
from datetime import datetime, timedelta, timezone
from logging import info, warning, error

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from time import time

from models.service_db import User
from schemas.auth import Token
from db import engine

_jwt_secret = os.getenv('JWT_SECRET')
_jwt_alg = 'HS256'


class AuthInvalidCredentialsException(Exception):
    pass

class AuthInvalidTokenException(Exception):
    pass

def get_current_user(token: str) -> User:
    '''
    Проверяет токен и возвращает пользователя.
    '''
    try:
        payload = jwt.decode(token,
                                _jwt_secret,
                                algorithms=[_jwt_alg])
        username = payload['sub']
    except jwt.InvalidTokenError as e:
        error('Invalid token')
        raise AuthInvalidTokenException from e

    with Session(engine) as session:
        db_user = session.exec(
            select(User).where(User.username == username)
        ).first()
    if not db_user:
        error('No user in DB for token')
        raise AuthInvalidTokenException

    return db_user

def get_token(user: OAuth2PasswordRequestForm) -> Token:
    '''
    Сверяет имя пользователя и пароль с БД, возвращает токен.
    '''
    with Session(engine) as session:
        db_user = session.exec(
            select(User).where(User.username == user.username)
        ).first()
    if not db_user:
        error('No user in DB for creds')
        raise AuthInvalidCredentialsException

    try:
        PasswordHasher().verify(db_user.password_hash, user.password)
    except (VerifyMismatchError, InvalidHashError) as e:
        error('Wrong password')
        raise AuthInvalidCredentialsException from e

    exp = datetime.now(timezone.utc) + timedelta(days=30)
    payload = {
        'sub': db_user.username,
        'exp': int(exp.timestamp())
    }
    token = jwt.encode(payload, _jwt_secret, algorithm=_jwt_alg)
    return Token(access_token=token, token_type='bearer')
