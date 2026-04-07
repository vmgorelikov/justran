from sqlmodel import SQLModel
from typing import Any, Dict, Literal, Optional
from sqlmodel import Field, SQLModel
from pydantic import RootModel

class TranslationJob(SQLModel, table=False):
    '''
    Сведения о созданной задаче перевода.
    '''
    id: int

class Original(SQLModel):
    '''
    Представление текста, получаемого от клиента.
    '''
    original: str

class Synonym(SQLModel):
    '''
    Набор вариантов перевода для фрагмента текста.

    :var id: ID фрагмента.
    :var start: Начало фрагмента.
    :var end: Конец фрагмента (не включительно).
    :var options: Список вариантов перевода.
    :var selected: Индекс выбранного варианта перевода в `options`.
    :var russian_original: Фрагмент исходного текста, к которому
    относится этот набор вариантов перевода.
    '''
    id: int
    start: int
    end: int
    options: list[str]
    selected: int
    russian_original: str

class Synonyms(RootModel):
    '''
    Набор наборов вариантов перевода.
    '''
    root: list[Synonym]

class Properties(SQLModel):
    '''
    Дополнительная информация, передаваемая с текстом перевода.

    '''
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

