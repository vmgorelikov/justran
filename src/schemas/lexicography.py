from sqlmodel import SQLModel

from models.lexical_db import Term

class Terms(SQLModel):
    '''
    Список терминов из глоссария.
    '''
    terms: list[Term]
