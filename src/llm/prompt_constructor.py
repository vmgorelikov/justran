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

    Use thesaurus to help you. If you see a word that is included in thesaurus, use provided translation as the first option.

    Thesaurus: {thesaurus}


    For all legal terms and phrases that have multiple possible translations: 
    you must mark them after providing full translation, in the same order they appear in your translation.

    Use ONLY the following template to mark the synonyms:

    /start/русское слово|translation1(like in text)|translation1(normal form)|translation2|translation3/end/

    The first option should be the most context-appropriate translation.
    Translation1(like in text) must be in the exact form it is in text.
    Translation1(normal form) must be the normal form of translation1(like in text)
    Russian word and all three types of translation must be in their normal form.

    Tranlation and synonym block must be divided only by a new line.

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

    AGENT_SYSTEM_PROMPT = """You are a legal term translator and glossary specialist.

    Your task:
    1. Identify legal terms in the user's text
    2. For each legal term, try to translate it.
    3. Then use search_glossary to look up similar terms and their definitions.
    4. Return ONLY a list of found terms in the exact format:

    термин1, transaltion1, definition1, id1
    термин2, transaltion2, definition2, id2
    термин3, transaltion3, definition3, id3
    ...

    Rules:
    - One term per line
    - Use comma (,) as separator
    - No extra text, no explanations, no markdown
    - If no terms found, return empty string
    """