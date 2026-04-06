"""
Модуль для создания клиента языковых моделей

(Возможно, в этот модуль будет удобно добавить функцию для создания агентов
Кажется, они создаются несколько похожим на клиентов способом
Хотя это потребудет некоторого merging'а)

Автор: Саша Жигулина <aazhigulina@edu.hse.ru>
"""

import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
 
load_dotenv()

class ModelConstructor:
    """Фабрика для создания клиентов языковых моделей.
    
    Предоставляет статические методы для инициализации моделей
    с единым интерфейсом.
    """

    @staticmethod
    def create_client(
        model_name: str, 
        provider: str = "openrouter", 
        base_url: str = "https://openrouter.ai/api/v1",
        **kwargs
    ):
        """Создаёт клиента для указанного провайдера.
        
        Args:
            model_name: идентификатор модели у провайдера
            provider: название провайдера (по умолчанию "opernouter")
            base_url: URL для доступа (по умолчанию для "opernouter")
            **kwargs: дополнительные параметры (температура, max_tokens и т.д.)
        
        Returns:
            Ollama: инициализированный клиент модели
            
        Raises:
            ValueError: если указан неподдерживаемый провайдер
        """
        if provider == "openrouter":
            return ChatOpenAI(
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1",
                model=model_name,
                **kwargs
            )
        elif provider == "ollama":
            return ChatOllama(
                model=model_name,
                base_url="http://localhost:11434",
                **kwargs
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
