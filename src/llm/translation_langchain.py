"""
Модуль перевода текста с интеграцией LangChain

Предоставляет классы для разбиения текста на чанки и перевода
с использованием LangChain моделей (Ollama и др.)

Автор: Саша Жигулина <aazhigulina@edu.hse.ru>
"""

import re
from dataclasses import dataclass
from typing import List
from langchain_core.language_models.chat_models import BaseChatModel


@dataclass
class Chunk:
    """Чанк текста для перевода"""
    text: str
    index: int
    boundary_type: str  # "sentence", "paragraph"
    overlap: str  # текст перекрытия с предыдущим чанком


@dataclass
class TranslationChunk:
    """Результат перевода одного чанка"""
    original: str
    translated: str
    index: int


@dataclass
class TranslationResult:
    """Полный результат перевода"""
    original: str
    translated: str
    chunks: List[TranslationChunk]


class PromptTemplates:
    """Шаблоны промптов для модели"""
    
    TRANSLATE = """Translate the following text from Russian to English. 
                    Return only the translation, no explanations.

                    Text: {text}

                    Translation:"""


class TextChunker:
    """Разбивает текст на чанки"""
    
    def __init__(self, overlap_sentences: int = 1):
        """
        Инициализирует чанкер.
        
        Args:
            overlap_sentences: Количество предложений для перекрытия между чанками
        """
        self.overlap_sentences = overlap_sentences
    
    def _create_chunk(
        self, 
        sentences: List[str], 
        chunk_index: int,
        is_last: bool = False
    ) -> Chunk:
        """
        Создает чанк из списка предложений.
        
        Args:
            sentences: Список предложений в чанке
            chunk_index: Индекс чанка
            is_last: Является ли чанк последним
            
        Returns:
            Chunk: Созданный чанк с текстом и метаданными
        """
        chunk_text = ' '.join(sentences)
        
        # Определяем перекрытие
        overlap = ''
        if self.overlap_sentences > 0 and chunk_index > 0 and not is_last:
            # Для непоследних чанков берем перекрытие из текущего чанка
            overlap_sentences = sentences[-self.overlap_sentences:]
            overlap = ' '.join(overlap_sentences)
        
        return Chunk(
            text=chunk_text,
            index=chunk_index,
            boundary_type="sentence",
            overlap=overlap
        )
    
    def split(self, text: str, max_tokens: int) -> List[Chunk]:
        """
        Разбивает текст на чанки по предложениям 
        (по точкам, вопросительным и восклицательным знакам)
        
        Args:
            text: Исходный текст для разбиения
            max_tokens: Максимальный размер чанка в символах
            
        Returns:
            List[Chunk]: Список чанков с перекрытием для сохранения контекста
            
        Raises:
            ValueError: Если text пустой или max_tokens меньше 1
        """
        if not text:
            raise ValueError("Text cannot be empty")
        if max_tokens < 1:
            raise ValueError("max_tokens must be at least 1")
        
        chunks = []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = []
        current_size = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            
            if current_size + sentence_size > max_tokens and current_chunk:
                # сохраняем текущий чанк
                chunks.append(self._create_chunk(current_chunk, chunk_index))

                # создаем новый чанк
                current_chunk = [sentence]
                current_size = sentence_size
                chunk_index += 1
            else:
                # увеличиваем текущий чанк на одно предложение
                current_chunk.append(sentence)
                current_size += sentence_size
        
        # последний чанк
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, chunk_index, is_last=True))
        
        return chunks


class TranslationProcessor:
    """Основной класс для перевода текста"""
    
    def __init__(
        self,
        model_client: BaseChatModel,
        chunker: TextChunker,
        max_chunk_size: int = 2000
    ):
        """
        Инициализирует процессор перевода.
        
        Args:
            model_client: Клиент для работы с языковой моделью
            chunker: Объект для разбиения текста на чанки
            max_chunk_size: Максимальный размер чанка в символах
        """
        self.model = model_client
        self.chunker = chunker
        self.max_chunk_size = max_chunk_size
        self._chunks: List[Chunk] = []
        self._current_index = 0
        self._results: List[TranslationChunk] = []
    
    def __iter__(self) -> "TranslationProcessor":
        """
        Подготавливает процессор к итерации по чанкам.
        
        Returns:
            TranslationProcessor: Ссылка на себя для использования в итерации
        """
        self._current_index = 0
        self._results = []
        return self
    
    def __next__(self) -> TranslationChunk:
        """
        Возвращает следующий переведенный чанк.
        
        Returns:
            TranslationChunk: Результат перевода очередного чанка
            
        Raises:
            StopIteration: Если все чанки уже обработаны
            RuntimeError: Если произошла ошибка при переводе чанка
        """
        if not self._chunks:
            raise StopIteration
        
        if self._current_index >= len(self._chunks):
            raise StopIteration
        
        chunk = self._chunks[self._current_index]
        
        # Формируем промпт с учетом перекрытия
        text_to_translate = chunk.text
        if chunk.overlap:
            text_to_translate = f"(Context from previous part: {chunk.overlap})\n\n{chunk.text}"
        
        prompt = PromptTemplates.TRANSLATE.format(text=text_to_translate)
        
        try:
            response = self.model.invoke(prompt)
            if hasattr(response, 'content'):
                translated = response.content
            else:
                translated = str(response)
        except Exception as e:
            raise RuntimeError(f"Translation failed for chunk {chunk.index}: {e}")
        
        # Сохраняем результат
        result = TranslationChunk(
            original=chunk.text,
            translated=translated,
            index=chunk.index
        )
        self._results.append(result)
        self._current_index += 1
        
        return result
    
    def process_full(self, text: str) -> TranslationResult:
        """
        Выполняет полный перевод текста.
        
        Args:
            text: Исходный текст для перевода
            
        Returns:
            TranslationResult: Объект с полным переводом и чанками
            
        Raises:
            ValueError: Если текст пустой
            RuntimeError: Если произошла ошибка при переводе
        """
        if not text:
            raise ValueError("Text cannot be empty")
        
        # Разбиваем на чанки
        self._chunks = self.chunker.split(text, self.max_chunk_size)
        
        # Переводим все чанки
        results = []
        for chunk in self._chunks:
            text_to_translate = chunk.text
            if chunk.overlap:
                text_to_translate = f"(Context from previous part: {chunk.overlap})\n\n{chunk.text}"
            
            prompt = PromptTemplates.TRANSLATE.format(text=text_to_translate)
            response = self.model.invoke(prompt)

            if hasattr(response, 'content'):
                translated = response.content
            else:
                translated = str(response)
            
            results.append(TranslationChunk(
                original=chunk.text,
                translated=translated,
                index=chunk.index
            ))
        
        # Собираем полный перевод
        full_translation = ' '.join(r.translated for r in sorted(results, key=lambda x: x.index))
        
        return TranslationResult(
            original=text,
            translated=full_translation,
            chunks=results
        )