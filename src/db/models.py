from datetime import datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(max_length=32, unique=True)
    display_name: str | None = Field(default=None, max_length=160)
    password_hash: str
    created_at: datetime

class UserCredentials(SQLModel):
    username: str = Field(max_length=32)
    password: str

class Token(SQLModel):
    token: str

class Translation(SQLModel, table=True):
    __tablename__ = "translations"

    id: int | None = Field(default=None, primary_key=True)
    initiated_by: int = Field(foreign_key="users.id")
    source_text: str
    full_text: str
    properties: str | None = None
    previous: int | None = Field(default=None, foreign_key="translation_patches.id")
    created_at: datetime


class TranslationPatch(SQLModel, table=True):
    __tablename__ = "translation_patches"

    id: int | None = Field(default=None, primary_key=True)
    for_translation: int = Field(foreign_key="translations.id")
    delta: str
    previous: int | None = Field(default=None, foreign_key="translation_patches.id")
    created_at: datetime


