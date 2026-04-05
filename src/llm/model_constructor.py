"""
Модуль для создания клиента языковых моделей

(Возможно, в этот модуль будет удобно добавить функцию для создания агентов
Кажется, они создаются несколько похожим на клиентов способом
Хотя это потребудет некоторого merging'а)

Автор: Саша Жигулина <aazhigulina@edu.hse.ru>
"""

from langchain_ollama import ChatOllama


class ModelConstructor:
    """Фабрика для создания клиентов языковых моделей.
    
    Предоставляет статические методы для инициализации моделей
    с единым интерфейсом.
    """

    @staticmethod
    def create_client(
        model_name: str, 
        provider: str = "ollama", 
        base_url: str = "http://localhost:11434",
        **kwargs
    ):
        """Создаёт клиента для указанного провайдера.
        
        Args:
            model_name: идентификатор модели у провайдера
            provider: название провайдера (пока только 'ollama')
            base_url: URL сервера Ollama
            **kwargs: дополнительные параметры (температура, max_tokens и т.д.)
        
        Returns:
            Ollama: инициализированный клиент модели
            
        Raises:
            ValueError: если указан неподдерживаемый провайдер
        """
        if provider == "ollama":
            return ChatOllama(
                model=model_name,
                base_url=base_url,
                **kwargs
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
