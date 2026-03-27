"""
Пример использования translation.py и translation_langchain.py

Автор: Саша Жигулина <aazhigulina@edu.hse.ru>
"""

# версия для отладки translation.py
# from translation import OllamaClient, TranslationProcessor, TextChunker
# client = OllamaClient("translategemma:4b")


# версия с поддержкой langchain translation_langchain.py 
from model_constructor import ModelConstructor
from translation_langchain import TranslationProcessor, TextChunker

client = ModelConstructor.create_client("translategemma:4b")

# Создаем чанкер с перекрытием в 1 предложение
chunker = TextChunker(overlap_sentences=1)

# Создаем процессор перевода
translator = TranslationProcessor(
    model_client=client,
    chunker=chunker,
    max_chunk_size=2000 # примерно 2000 символов на чанк
)

# Полный перевод
legal_text_contract = """
                    Статья 2. Основные права и свободы человека и гражданина
1. Права и свободы человека и гражданина являются непосредственно действующими. Они определяют смысл, содержание и применение законов, деятельность законодательной и исполнительной власти, местного самоуправления и обеспечиваются правосудием.
2. Государство гарантирует равенство прав и свобод человека и гражданина независимо от пола, расы, национальности, языка, происхождения, имущественного и должностного положения, места жительства, отношения к религии, убеждений, принадлежности к общественным объединениям, а также других обстоятельств.
3. Ограничение прав и свобод человека и гражданина допускается только федеральным законом и только в той мере, в какой это необходимо в целях защиты основ конституционного строя, нравственности, здоровья, прав и законных интересов других лиц, обеспечения обороны страны и безопасности государства.
                    """

result = translator.process_full(legal_text_contract)
print(result.translated)

# Просмотр чанков
for chunk in result.chunks:
    print(chunk.index, chunk)