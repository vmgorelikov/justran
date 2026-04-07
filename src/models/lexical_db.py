from datetime import datetime, UTC
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel, Column


class Term(SQLModel, table=True):
    __tablename__ = 'glossary'
    '''
    Термин из глоссария.
    '''
    id: int = Field(primary_key=True)
    term: str
    definition: str
