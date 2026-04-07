import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Any
from langchain_core.tools import tool
import difflib

class GlossarySearcher:
    """Поиск по глоссарию с fuzzy matching через триграммы."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def _generate_trigrams(self, text: str) -> List[str]:
        """Генерирует триграммы из строки."""
        text = text.lower()
        return [text[i:i+3] for i in range(len(text)-2)]
    
    def search_by_trigrams(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Поиск терминов через существующую таблицу триграмм
        
        Args:
        query (str): Поисковый запрос (слово или фраза для поиска в глоссарии).
        max_results (int, optional): Максимальное количество возвращаемых результатов, по умолчанию 3.
        
        Returns:
            List[Dict[str, Any]]: Список словарей, каждый из которых содержит:
                - id (int): Уникальный идентификатор термина
                - term (str): Найденный термин
                - definition (str): Определение термина
            
            Если совпадений не найдено, возвращается пустой список.
        """
        trigrams = self._generate_trigrams(query)
        
        if not trigrams:
            return []
        
        print(f"Connecting to DB: {self.db_path}") 

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Используем существующую таблицу glossary_trigrams
            placeholders = ','.join('?' * len(trigrams))
            cursor.execute(f"""
                SELECT 
                    g.id, 
                    g.term, 
                    g.definition,
                    COUNT(gt.trigram) as match_count
                FROM glossary g
                JOIN glossary_trigrams gt ON g.id = gt.term_id
                WHERE gt.trigram IN ({placeholders})
                GROUP BY g.id
                ORDER BY match_count DESC
                LIMIT ?
            """, (*trigrams, max_results))
            
            return [
                {
                    "id": row['id'],
                    "term": row['term'],
                    "definition": row['definition']
                }
                for row in cursor.fetchall()
            ]
        
    def search_by_fuzzy(self, query: str, max_results: int = 3, min_ratio: float = 0.6) -> List[Dict[str, Any]]:
        """Выполняет нечёткий поиск терминов в глоссарии.
    
        Args:
            query: Поисковый запрос (слово или фраза).
            max_results: Максимальное количество результатов. По умолчанию 3.
            min_ratio: Минимальный коэффициент схожести (0.0-1.0). По умолчанию 0.6.
        
        Returns:
            Список словарей с ключами: id, term, definition, score.
            Сортировка по убыванию score.
    """

        print(f"Connecting to DB: {self.db_path}")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, term, definition FROM glossary")
            all_terms = cursor.fetchall()
            print(f"Fetched {len(all_terms)} terms from glossary table")
            
            # Распечатаем первые 5 терминов для проверки
            for i, term in enumerate(all_terms[:5]):
                print(f"  Term {i+1}: ID={term[0]}, term='{term[1]}'")
        
        if not all_terms:
            print("No terms found in glossary table!")
            return []
        
        # Вычисляем коэффициенты схожести
        matches = []
        for term_id, term, definition in all_terms:
            # Используем SequenceMatcher для сравнения строк
            ratio = difflib.SequenceMatcher(None, query.lower(), term.lower()).ratio()
            if ratio >= min_ratio:
                matches.append({
                    "id": term_id,
                    "term": term,
                    "definition": definition,
                    "score": round(ratio * 100, 2)
                })
        
        # Сортируем по убыванию score и берем top max_results
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:max_results]
    
    def search(self, query: str, max_results: int = 3, mode: str = "fuzzy") -> List[Dict[str, Any]]:
        """Поиск с выбором режима.
        
        Args:
            query: поисковый запрос
            max_results: максимальное количество результатов
            mode: "trigrams" (быстрый) или "fuzzy" (точный, по умолчанию)
        """
        if mode == "trigrams":
            return self.search_by_trigrams(query, max_results)
        else:
            return self.search_by_fuzzy(query, max_results)


def search_glossary_base(query: str, max_results: int = 3) -> str:
    """Базовая функция поиска в глоссарии.
    
    Args:
        query: Поисковый запрос.
        max_results: Максимальное количество результатов.
    
    Returns:
        Отформатированная строка с результатами поиска или сообщением об ошибке.
    """

    print(f"Tool called: search_glossary('{query}', {max_results})")

    # скорее всего тут будут проблемы с путём
    # db_path = os.getenv("GLOSSARY_DB_PATH", "glossary.db")
    db_path = Path(__file__).parent / "data" / "glossary.db"
    
    try:
        searcher = GlossarySearcher(db_path)
        results = searcher.search(query, max_results)

        print(results)
        
        if not results:
            return f"No matches found for '{query}' in glossary."
        
        output = []
        for r in results:
            output.append(f"ID: {r['id']}\nTerm: {r['term']}\nDefinition: {r['definition']}\n")
        
        return "\n".join(output)
        
    except Exception as e:
        return f"Error searching glossary: {str(e)}"


@tool
def search_glossary(query: str, max_results: int = 3) -> str:
    """Searches a glossary for a word or expression and returns the closest matches with their definitions and unique IDs.
    
    Args:
        query: The word or phrase to look up in the glossary (e.g., 'API' or 'Large Language Model').
        max_results: The maximum number of fuzzy matches to return.
    
    Returns:
        Formatted string with search results.
    """
    return search_glossary_base(query, max_results)
