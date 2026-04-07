from sqlmodel import SQLModel
from typing import Any, Dict, Literal, Optional
from sqlmodel import Field, SQLModel
from pydantic import RootModel

class Original(SQLModel):
    '''
    Представление текста, получаемого от клиента.
    '''
    original: str

class Synonym(SQLModel):
    id: int
    start: int
    end: int
    options: list[str]
    selected: int
    russian_original: str

class Synonyms(RootModel):
    '''
    Представление списка синонимов к словам и выражением в переводе.
    '''
    root: list[Synonym]

class Properties(SQLModel):
    synonyms: Synonyms

class TranslationChunk(SQLModel):
    '''
    Представление чанка перевода и сопутствующих данных
    для отправки клиенту.
    '''
    id: int
    translated: str
    index: int
    properties: Properties

class TranslationResult:
    '''
    Представление полного перевода.
    '''
    id: int
    translated: str
    properties: list[Synonyms]

