from datetime import datetime, UTC
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy.dialects.postgresql import JSONB


class User(SQLModel, table=True):
    '''
    Пользователь.

    :vartype id: int
    :vartype username: str
    :vartype display_name: str
    :vartype password_hash: str
    :vartype created_at: datetime.datetime

    :var id: ID, возрастающий.
    :var username: Логин до 32 символов из `[A-Za-z0-9_\\-.]`.
    :var display_name: Отображаемое имя до 160 любых символов.
    :var password_hash: Argon2 хэш пароля.
    :var created_at: Дата и время регистрации пользователя.
    '''
    __tablename__ = 'users'

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(max_length=32, unique=True,
                          regex=r'[A-Za-z0-9_\-.]+')
    display_name: str | None = Field(default=None, max_length=160)
    password_hash: str
    created_at: datetime = Field(default_factory=
                                 lambda: datetime.now(UTC))
    
    translations: list['Translation'] =\
        Relationship(back_populates="initiator")


class Translation(SQLModel, table=True):
    __tablename__ = 'translations'

    id: Optional[int] = Field(default=None, primary_key=True)
    initiated_by: int = Field(foreign_key ='users.id')
    original: str
    translated: Optional[str]
    properties: str | None = Field(default=None,
                                   sa_column=Column(JSONB))
    previous: int | None = Field(default=None,
                                 foreign_key='translation_patches.id')
    created_at: datetime = Field(default_factory=
                                 lambda: datetime.now(UTC))
    
    initiator: User = Relationship(back_populates="translations")


class TranslationPatch(SQLModel, table=True):
    '''
    Не используется.
    '''
    __tablename__ = 'translation_patches'

    id: int | None = Field(default=None, primary_key=True)
    for_translation: int = Field(foreign_key='translations.id')
    delta: str
    previous: int | None = Field(default=None, foreign_key='translation_patches.id')
    created_at: datetime = Field(default_factory =
                                 lambda: datetime.now(UTC))


