from sqlmodel import SQLModel
from typing import Literal, Optional

class UserCredentials(SQLModel, table=False):
    username: str
    password: str

class Token(SQLModel, table=False):
    access_token: str
    token_type: Literal['bearer']

class AuthError(SQLModel, table=False):
    error: Literal['invalid_token'] | Literal['invalid_credentials']
    error_description: Optional[str]
