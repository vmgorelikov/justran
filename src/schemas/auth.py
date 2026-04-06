'''
Схемы данных, используемые при авторизации.

:Authors: В. М. Гореликов <vmgorelikov@edu.hse.ru>
'''

from sqlmodel import SQLModel
from typing import Literal, Optional
from sqlmodel import Field, SQLModel

class UserCredentials(SQLModel, table=False):
    '''
    Пара логин:пароль пользователя.

    :vartype username: str
    :vartype password: str

    :var username: Логин до 32 символов из `[A-Za-z0-9_\\-.]`.
    :var password: Пароль в явном виде.
    '''
    username: str = Field(max_length=32, regex=r'[A-Za-z0-9_\-.]+')
    password: str

class Token(SQLModel, table=False):
    '''
    Токен для доступа к API.

    :vartype access_token: str
    :vartype token_type: str

    :var access_token: Токен.
    :var token_type: Тип токена (всегда Bearer).
    '''
    access_token: str
    token_type: Literal['bearer']

class AuthError(SQLModel, table=False):
    '''
    Ошибка авторизации.

    :vartype error: str
    :vartype error_description: str

    :var error: Код ошибки:
    * `invalid_token` — токен осутствует, истёк, принадлежит
    удалённому пользователю или просто неверный.
    * `invalid_credentials` — логин и/или пароль, представленные
    для получения токена, не подходят.

    :var error_description: Не используется.
    '''
    error: Literal['invalid_token'] | Literal['invalid_credentials']
    error_description: Optional[str]
