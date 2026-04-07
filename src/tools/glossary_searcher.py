import sqlite3
import os
from typing import List, Dict, Any
from langchain_core.tools import tool


class GlossarySearcher:
    """Поиск по глоссарию с fuzzy matching через триграммы."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def _generate_trigrams(self, text: str) -> List[str]:
        """Генерирует триграммы из строки."""
        text = text.lower()
        return [text[i:i+3] for i in range(len(text)-2)]
    
    def search(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Поиск терминов через существующую таблицу триграмм."""
        trigrams = self._generate_trigrams(query)
        
        if not trigrams:
            return []
        
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

def search_glossary_base(query: str, max_results: int = 3) -> str:
    # для отладки
    # print(f"\n>>> TOOL CALLED: search_glossary('{query}', {max_results})")

    # скорее всего тут будут проблемы с путём
    db_path = os.getenv("GLOSSARY_DB_PATH", "glossary.db")
    
    try:
        searcher = GlossarySearcher(db_path)
        results = searcher.search(query, max_results)
        
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
