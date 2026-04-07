"""
Модуль для создания клиентов языковых моделей и агентов с инструментами.

Автор: Саша Жигулина <aazhigulina@edu.hse.ru>
"""

import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from typing import List, Optional
from llm.prompt_constructor import PromptTemplates
 
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
        
    @staticmethod
    def create_agent(
        model_name: str,
        tools: List,
        system_prompt: Optional[str] = None,
        provider: str = "openrouter",
        **model_kwargs
    ):
        """Создаёт агента с инструментами.
        
        Args:
        model_name: идентификатор модели у провайдера
        tools: список инструментов (функции с декоратором @tool)
        system_prompt: системный промпт для агента (опционально)
        provider: название провайдера (по умолчанию "openrouter")
        **model_kwargs: дополнительные параметры (температура, max_tokens и т.д.)
    
        Returns:
            Agent: инициализированный агент LangChain
            
        Raises:
            ValueError: если указан неподдерживаемый провайдер
        """
        client = ModelConstructor.create_client(model_name, provider, **model_kwargs)
        return create_agent(
            model=client,
            tools=tools,
            system_prompt=PromptTemplates.AGENT_SYSTEM_PROMPT
        )
