from sqlmodel import SQLModel
from typing import Any, Dict, Literal, Optional
from sqlmodel import Field, SQLModel
from pydantic import RootModel

class Original(SQLModel):
    '''
    Представление текста, получаемого от клиента.
    '''
    original: str

class Synonyms(RootModel):
    '''
    Представление списка синонимов к словам и выражением в переводе.
    '''
    root: Dict[str, set[str]]

class TranslationChunk(SQLModel):
    '''
    Представление чанка перевода и сопутствующих данных
    для отправки клиенту.
    '''
    id: int
    translated: str
    index: int
    properties: list[Synonyms]
    is_final: bool

class TranslationResult:
    '''
    Представление полного перевода.
    '''
    id: int
    translated: str
    properties: list[Synonyms]

