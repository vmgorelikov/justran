from json import dumps

from sqlmodel import Session, select

from llm.model_constructor import ModelConstructor
from llm.prompt_constructor import PromptTemplates
from llm.translation import TextChunker, TranslationProcessor, BaseChatModel, TranslationChunk
from schemas.translation import Original
from models.service_db import User, Translation
from db import engine

client = ModelConstructor.create_client("translategemma:4b")

chunker = TextChunker(overlap_sentences=1)

class TranslationSession():
    def __init__(self, user: User, original: Original) -> None:
        # соотв. /new/
        self.translation_processor = TranslationProcessor(
            model_client=client,
            chunker=chunker,
            max_chunk_size=2000,
            prompt_template=PromptTemplates.TRANSLATE_SYNONYMS,
            text=Original.original
        )

        self.translation = Translation(
            initiator=user,
            original=original.original
        )

        with Session(engine) as session:
            session.add(self.translation)
            session.commit()
            session.refresh(self.translation)

    def __iter__(self) -> 'TranslationSession':
        iter(self.translation_processor)
        return self

    def __next__(self) -> TranslationChunk | None:
        try:
            return next(self.translation_processor)
        except StopIteration:
            pass

        full_translated = ' '.join(chunk.translated
                                for chunk 
                                in self.translation_processor.results)
        
        properties = {'synonyms': alternative
                        for alternative
                        in [chunk.alternatives
                        for chunk
                        in self.translation_processor.results]}
        
        with Session(engine) as session:
            statement = select(Translation)\
                .where(Translation.id == self.translation.id)
            translation = session.exec(statement).first()

            if translation:
                translation.translated = full_translated
                translation.properties = dumps(properties)
                session.add(translation)
                session.commit()
                session.refresh(translation)

