"""
Пример использования модуля LLM

Автор: Саша Жигулина <aazhigulina@edu.hse.ru>
"""

from model_constructor import ModelConstructor
from prompt_constructor import PromptTemplates
from translation import TranslationProcessor, TextChunker
from lexical_assistant import LexicalAssistant

# инициализируем клиента
client = ModelConstructor.create_client("translategemma:4b")

# Создаем чанкер с перекрытием в 1 предложение
chunker = TextChunker(overlap_sentences=1)

# Создаем процессор перевода
translator = TranslationProcessor(
    model_client=client,
    chunker=chunker,
    max_chunk_size=2000,
    prompt_template=PromptTemplates.TRANSLATE_SYNONYMS
)

assistant = LexicalAssistant(model_client=client)

legal_text_contract = """
В соответствии с настоящим соглашением, сторона обязуется предоставить встречное удовлетворение в размере, определяемом на основании добросовестной оценки. 
В случае возникновения спора, вопрос подлежит рассмотрению в суде общей юрисдикции по месту нахождения ответчика. 
Исполнение обязательств может быть обеспечено задатком, неустойкой или поручительством. 
Просрочка исполнения влечет за собой применение мер ответственности, включая возмещение убытков и потерь, понесенных кредитором. 
Стороны пришли к соглашению о конфиденциальности информации, составляющей коммерческую тайну.
"""

# Перевод
result = translator.process_full(legal_text_contract)
print(result.translated, '\n\n')

# Просмотр чанков
for chunk in result.chunks:
    print(chunk.index, chunk, '\n\n')

# Анализ слов из перевода
sample_word = "agreement"
sample_context = result.translated.split('.')[0] + '.'
info = assistant.get_word_usage(sample_word, sample_context)

print(f"\n{info['explanation']}")
for ex in info['examples'][:2]:
    print(f"- {ex}")