"""
Модуль для анализа перевода

Позволяет получить лексикографическую справку по синонимам

Автор: Саша Жигулина <aazhigulina@edu.hse.ru>
"""

import re
from langchain_core.language_models.chat_models import BaseChatModel
from typing import List, Dict, Tuple, Any
from prompt_constructor import PromptTemplates

class LexicalAssistant:
    """Лексикографический ассистент на основе LLM"""
    def __init__(self, 
                 model_client: BaseChatModel, 
                 prompt_template: str = PromptTemplates.WORD_USAGE
    ):
        """
        Инициализирует ассистента.
        
        Args:
            model_client: Клиент языковой модели
            prompt_template: Шаблон промпта (по умолчанию PromptTemplates.WORD_USAGE)
        """
        self.model = model_client
        self.prompt_template = prompt_template

    def get_word_usage(self, word: str, context: str) -> Dict[str, Any]:
        """
        Возвращает лексикографическую справку о слове в контексте.
        
        Args:
            word: Анализируемое слово или фраза
            context: Окружающий текст (предложение или абзац)
            
        Returns:
            Dict с ключами: word, context, explanation, examples, notes
            
        Raises:
            ValueError: Если word или context пустые
            RuntimeError: Если вызов модели не удался
        """
        if not word or not context:
            raise ValueError("Word and context must not be empty")
        
        prompt = self.prompt_template.format(word=word.strip(), context=context.strip())
        
        try:
            response = self.model.invoke(prompt)
            content = getattr(response, 'content', str(response))
        except Exception as e:
            raise RuntimeError(f"Model invocation failed: {e}")
        
        # Парсинг ответа
        explanation = ''
        examples = []
        notes = ''
        
        # Извлечение explanation
        expl_match = re.search(r'Explanation:\s*(.+?)(?=\n\n|\nExamples:|\Z)', content, re.DOTALL | re.IGNORECASE)
        if expl_match:
            explanation = expl_match.group(1).strip()
        
        # Извлечение examples
        ex_section = re.search(r'Examples:\s*\n((?:- .+?\n?)+)', content, re.DOTALL | re.IGNORECASE)
        if ex_section:
            examples = [ex.strip() for ex in re.findall(r'-\s*(.+?)(?=\n-|\n\n|\Z)', ex_section.group(1), re.DOTALL)]
        
        # Извлечение notes
        notes_match = re.search(r'Notes:\s*(.+?)(?=\n\n|\Z)', content, re.DOTALL | re.IGNORECASE)
        if notes_match:
            notes = notes_match.group(1).strip()
        
        # Fallback
        if not explanation and not examples:
            explanation = content.strip()
            notes = "Warning: Response was not in expected format"
        
        return {
            'word': word.strip(),
            'context': context.strip(),
            'explanation': explanation,
            'examples': examples,
            'notes': notes
        }