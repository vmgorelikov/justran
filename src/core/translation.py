from json import dumps

from sqlmodel import Session, select

from llm.model_constructor import ModelConstructor
from llm.prompt_constructor import PromptTemplates
from llm.translation import Alternative, TextChunker, TranslationProcessor, BaseChatModel
from llm.translation import TranslationChunk as TranslationChunkLLM
from schemas.translation import Properties, Synonyms, TranslationChunk as\
                                         TranslationChunkSendable
from schemas.translation import Original
from models.service_db import User, Translation
from db import engine

client = ModelConstructor.create_client("translategemma:4b")

chunker = TextChunker(overlap_sentences=1)

class TranslationSession():
    def __init__(self, user: User, original: Original) -> None:
        # соотв. /new/
        
        self.translation = Translation(
            initiator=user,
            original=original.original
        )

        with Session(engine) as session:
            session.add(self.translation)
            session.commit()
            session.refresh(self.translation)

        self.translation_processor = TranslationProcessor(
            model_client=client,
            chunker=chunker,
            max_chunk_size=2000,
            prompt_template=PromptTemplates.TRANSLATE_SYNONYMS,
            text=original.original
        )


    def __iter__(self) -> 'TranslationSession':
        self.chunk_index = -1
        self.full_alternatives: list[Alternative] = []
        return self

    def __next__(self) -> TranslationChunkSendable | None:
        try:
            chunk = next(self.translation_processor)
            self.full_alternatives.extend(chunk.alternatives)
            self.chunk_index += 1
            return TranslationChunkSendable(
                id = self.translation.id,
                translated=chunk.translated,
                index=self.chunk_index,
                properties=Properties(synonyms=Synonyms(
                    root=chunk.alternatives)
                    )  # CORRECT
            )
        except StopIteration as e:
            full_translated = ' '.join(chunk.translated
                                    for chunk 
                                    in self.translation_processor.results)
            
            properties = Properties(synonyms=Synonyms(
                root=self.full_alternatives))

            
            with Session(engine) as session:
                statement = select(Translation)\
                    .where(Translation.id == self.translation.id)
                translation = session.exec(statement).first()

                if translation:
                    translation.translated = full_translated
                    translation.properties = properties.model_dump_json()
                    session.add(translation)
                    session.commit()
                    session.refresh(translation)

            raise StopIteration from e
