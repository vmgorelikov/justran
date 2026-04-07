
from logging import debug
import logging

from sqlmodel import Session, select

from models.lexical_db import Term
from schemas.lexicography import Terms
from tools.glossary_searcher import GlossarySearcher
from db import lexicography_engine

logging.basicConfig(level=logging.DEBUG)

def glossary_search(query: str | int) -> Terms:
    # замечательный оверлоадинг 10/10
    try:
        query = int(query)
    except ValueError:
        pass
    if isinstance(query, int):
        with Session(lexicography_engine) as session:
            statement = select(Term).where(Term.id == query)
            return Terms(terms=list(session.exec(statement).all()))
    if not isinstance(query, str):
        raise ValueError
    debug(str(lexicography_engine.url))

    db_url = str(lexicography_engine.url)
    if db_url.startswith('sqlite:///'):
        db_url = db_url[len('sqlite:///'):]

    glossary_searcher = GlossarySearcher(db_url)
    return Terms(terms=[Term(**kwargs)
                        for kwargs in glossary_searcher.search(query)])
