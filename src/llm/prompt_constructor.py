"""
Модуль для хранения и компиляции промптов.

Автор: Саша Жигулина <aazhigulina@edu.hse.ru>
"""

class PromptTemplates:
    """Шаблоны промптов для модели"""
    
    TRANSLATE_TESTING = """Translate the following text from Russian to English. 
    Return only the translation, no explanations.

    Text: {text}

    Translation:"""
    
    TRANSLATE_SYNONYMS = """You are a professional translator.
    Translate the following legal text from Russian to English.
    For all legal terms and phrases that have multiple possible translations, you must mark in the same order they appear in your translation.

    Use ONLY the following template to mark the synonyms:

    /start/русское слово|translation1|translation2|translation3/end/

    The first option should be the most context-appropriate translation.

    Text: {text}

    Translation:"""
    
    FIND_SYNONYMS = """You are a professional translator.
    In this text, find words that can be translated in more than one way. 
    Write each of them in a new paragraph. DO NOT TRANSLATE THE TEXT ITSELF.

    Text: {text}

    Answer:"""

    
    WORD_USAGE = """You are a lexicographer. Explain the usage of the word/phrase "{word}" in the given context.

    Context: "{context}"

    Provide:
    1. A brief explanation of how the word is used in this context
    2. Three example sentences showing similar usage
    3. Any relevant notes about register (formal/informal) or regional variations

    Response format:
    Explanation: [your explanation]
    Examples:
    - [example 1]
    - [example 2]
    - [example 3]
    Notes: [notes if any]
    """