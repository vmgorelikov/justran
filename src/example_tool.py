from tools.glossary_searcher import search_glossary
from llm.model_constructor import ModelConstructor


# Создаем агента с тулом
agent = ModelConstructor.create_agent(
    model_name="openai/gpt-oss-120b:free",
    tools=[search_glossary],
    provider="openrouter",
    system_prompt="You are a legal assistant. Use search_glossary to find definitions of legal terms."
)

# Вызов для юридического термина
response = agent.invoke({
    "messages": [("user", "What does 'GDPR' mean in law?")]
})

print(response['messages'][-1].content)