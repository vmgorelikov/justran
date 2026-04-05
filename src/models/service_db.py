from datetime import datetime, UTC
from sqlmodel import Field, SQLModel


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


class Translation(SQLModel, table=True):
    __tablename__ = 'translations'

    id: int | None = Field(default=None, primary_key=True)
    initiated_by: int = Field(foreign_key ='users.id')
    original: str
    translated: str
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


