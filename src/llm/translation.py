"""
Модуль перевода текста с интеграцией LangChain

Предоставляет классы для разбиения текста на чанки и перевода
с использованием LangChain моделей (Ollama и др.)

Автор: Саша Жигулина <aazhigulina@edu.hse.ru>
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Any
from langchain_core.language_models.chat_models import BaseChatModel
from llm.prompt_constructor import PromptTemplates
from langchain_core.messages import HumanMessage
from schemas.translation import Synonym

Alternative = Synonym

with open("C:/Users/user/repos/justran/data/Art.4 GDPR.txt", 'r', encoding='utf-8') as f:
    data = f.read()

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
    alternatives: list[Alternative]


@dataclass
class TranslationResult:
    """Полный результат перевода"""
    original: str
    translated: str
    chunks: List[TranslationChunk]
    global_alternatives: List[Dict[str, Any]] = field(default_factory=list)


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
        # model_agent,
        chunker: TextChunker,
        max_chunk_size: int = 2000,
        prompt_template: str = PromptTemplates.TRANSLATE_TESTING,
        max_retries: int = 2,
        min_alternatives: int = 1,
        *,
        text: str | None,
    ):
        """
        Инициализирует процессор перевода.
        
        Args:
            model_client: Клиент для работы с языковой моделью
            chunker: Объект для разбиения текста на чанки
            max_chunk_size: Максимальный размер чанка в символах
            term_agent_model: Отдельная модель для агента терминов (опционально)
                            Если не указана, используется model_client
        """
        self.model = model_client
        self.chunker = chunker
        self.max_chunk_size = max_chunk_size
        self.prompt_template = prompt_template
        self._chunks: List[Chunk] = []
        self._current_index = 0
        self.results: List[TranslationChunk] = []
        self.max_retries = max_retries
        self.min_alternatives = min_alternatives
        self._next_alternative_id = 0
        # self.model_agent = model_agent
        
        if type(text) is str:
            self.chunk(text)

    def chunk(self, text: str) -> 'TranslationProcessor':
        '''
        Делит текст на чанки и сохраняет их для перевода.
        '''
        if not text:
            raise ValueError("Text cannot be empty")
        self._chunks = self.chunker.split(text, self.max_chunk_size)
        return self

    def _parse_synonyms_markers(self, text: str) -> Tuple[str, List[Dict]]:
        """
        Извлекает альтернативы из маркеров /start/.../end/, где маркеры находятся
        после основного перевода и содержат русский оригинал и английские варианты.
        
        Формат блока с альтернативами:
        /start/русский_оригинал | английский_перевод | английский_вариант1 | английский_вариант2 | ... /end/
        
        Returns:
            (очищенный_текст_перевода, список_альтернатив)
        """
        # Поиск первого маркера
        first_marker = re.search(r'/start/', text)
        if not first_marker:
            return text, []
        
        # Отделяем основной перевод от блока с альтернативами
        cleaned = text[:first_marker.start()].strip()
        alternatives_block = text[first_marker.start():]
        
        # Извлекаем все пары из блока альтернатив
        pairs = []
        pattern = r'/start/(.*?)/end/'
        
        for match in re.finditer(pattern, alternatives_block, re.DOTALL):
            parts = [p.strip() for p in match.group(1).split('|')]
            if len(parts) < 2:
                continue
            
            pairs.append({
                'russian_original': parts[0],
                'english_variants': parts[2:],
                'selected': 0,
                'translation_to_search': parts[1]
            })
        
        # Ищем позиции вариантов в тексте перевода (с учётом регистра)
        alternatives = []
        current_pos = 0
        cleaned_lower = cleaned.lower()
        
        for pair in pairs:
            target = pair['translation_to_search']
            target_lower = target.lower()
            pos = cleaned_lower.find(target_lower, current_pos)
            
            if pos != -1:
                # Находим оригинальный спан с сохранением регистра
                original_span = cleaned[pos:pos + len(target)]
                alternatives.append(Alternative(**{
                    "id": self._next_alternative_id,
                    "start": pos,
                    "end": pos + len(target),
                    "options": pair['english_variants'],
                    "selected": 0,
                    "russian_original": pair['russian_original']
                }))
                
                self._next_alternative_id += 1
                current_pos = pos + len(target)
        
        return cleaned, alternatives
    
    def _add_retry_hint(self, text: str, attempt: int) -> str:
        """
        Добавляет инструкцию для модели при повторной попытке.
        """
        hint = f"\n\n[Instruction: Previous attempt had no synonyms marked. \
            Please mark at least one word with /start/русское слово|translation1|translation2|translation3/end/ format.]"
        return text + hint
        
    def __aiter__(self) -> "TranslationProcessor":
        """
        Подготавливает процессор к итерации по чанкам.
        
        Returns:
            TranslationProcessor: Ссылка на себя для использования в итерации
        """
        self._current_index = 0
        self.results: list[TranslationChunk] = []
        return self
    
    async def __anext__(self) -> TranslationChunk:
        """
        Возвращает следующий переведенный чанк.
        
        Returns:
            TranslationChunk: Результат перевода очередного чанка
            
        Raises:
            StopAsyncIteration: Если все чанки уже обработаны
            RuntimeError: Если произошла ошибка при переводе чанка
        """
        if not self._chunks:
            raise StopAsyncIteration
        
        if self._current_index >= len(self._chunks):
            raise StopAsyncIteration
        
        chunk = self._chunks[self._current_index]

        # вызываем агента
        # try:
        #     agent_response = await self.model_agent.ainvoke({
        #         "messages": [HumanMessage(content=f"Find and translate legal terms in this text: {chunk.text}")]
        #     })
        #     thesaurus = agent_response['messages'][-1].content
        # except Exception as e:
        #     thesaurus = ""
        
        # Формируем промпт с учетом перекрытия
        text_to_translate = chunk.text
        if chunk.overlap:
            text_to_translate = f"(Context from previous part: {chunk.overlap})\n\n{chunk.text}"
        
        prompt = self.prompt_template.format(glossary=data, text=text_to_translate)
        
        try:
            for attempt in range(self.max_retries + 1):
                prompt = self.prompt_template.format(glossary=data, text=text_to_translate)
                response = await self.model.ainvoke(prompt)
                raw_translated = response.content if hasattr(response, 'content') else str(response)
                cleaned, alts = self._parse_synonyms_markers(raw_translated)
                
                if len(alts) >= self.min_alternatives:
                    break
                
                # если не последняя попытка, добавляет подсказку в следующий промпт
                if attempt < self.max_retries:
                    text_to_translate = self._add_retry_hint(text_to_translate, attempt)

        except Exception as e:
            raise RuntimeError(f"Translation failed for chunk {chunk.index}: {e}")
        
        # Сохраняем результат
        result = TranslationChunk(
            original=chunk.text,
            translated=cleaned,
            index=chunk.index,
            alternatives=alts
        )
        self.results.append(result)
        self._current_index += 1
        
        return result
    
    async def process_full(self, text: str) -> TranslationResult:
        """Выполняет полный перевод текста."""
        if not text:
            raise ValueError("Text cannot be empty")
        
        self.chunk(text)
        
        full_translation_parts = []
        all_alternatives = []
        
        # используем как итератор
        async for chunk_result in self:
            full_translation_parts.append(chunk_result.translated)
            all_alternatives.extend(chunk_result.alternatives)
        
        return TranslationResult(
            original=text,
            translated=' '.join(full_translation_parts),
            chunks=self.results,
            global_alternatives=all_alternatives
        )
