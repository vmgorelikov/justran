from datetime import datetime, UTC
from sqlmodel import Field, SQLModel
from typing import Literal


class User(SQLModel, table=True):
    __tablename__ = 'users'

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(max_length=32, unique=True,
                          regex=r'[A-Za-z0-9_\-.]+')
    display_name: str | None = Field(default=None, max_length=160)
    password_hash: str
    created_at: datetime = Field(default_factory=
                                 lambda: datetime.now(UTC))

class UserCredentials(SQLModel, table=False):
    username: str
    password: str

class Token(SQLModel):
    access_token: str
    token_type: Literal['bearer']


class Translation(SQLModel, table=True):
    __tablename__ = 'translations'

    id: int | None = Field(default=None, primary_key=True)
    initiated_by: int = Field(foreign_key ='users.id')
    source_text: str
    full_text: str
    properties: str | None = None
    previous: int | None = Field(default=None,
                                 foreign_key='translation_patches.id')
    created_at: datetime = Field(default_factory=
                                 lambda: datetime.now(UTC))


class TranslationPatch(SQLModel, table=True):
    __tablename__ = 'translation_patches'

    id: int | None = Field(default=None, primary_key=True)
    for_translation: int = Field(foreign_key='translations.id')
    delta: str
    previous: int | None = Field(default=None, foreign_key='translation_patches.id')
    created_at: datetime = Field(default_factory =
                                 lambda: datetime.now(UTC))


