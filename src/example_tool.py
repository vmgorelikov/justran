from tools.glossary_searcher import search_glossary
from llm.model_constructor import ModelConstructor
from langchain_core.messages import HumanMessage


# Создаем агента с тулом
agent = ModelConstructor.create_agent(
    model_name="openai/gpt-oss-120b:free",
    tools=[search_glossary],
    provider="openrouter",
    system_prompt="You are a legal assistant. Use search_glossary to find definitions of legal terms."
)

text="В соответствии с GDPR, главное учреждение контроллера определяется как место его центрального административного управления на территории Европейского Союза, если только решения о целях и средствах обработки персональных данных не принимаются в другом учреждении контроллера на территории Союза, и если это другое учреждение имеет полномочия обеспечивать выполнение таких решений, то такое другое учреждение следует рассматривать как главное учреждение. В случае контроллера с учреждениями на территории нескольких государств-членов, главным учреждением является место его центрального административного управления, где осуществляются основные операции по обработке персональных данных. При этом главное учреждение процессора определяется как место его центрального административного управления на территории Союза или, если у процессора нет центрального административного управления на территории Союза, то учреждение процессора на территории Союза, где осуществляются основные операции по обработке, при условии, что процессор подпадает под обязательства GDPR. Понятие главного учреждения является ключевым для применения механизма 'единой точки контакта' (one-stop-shop), позволяющего взаимодействовать с одним ведущим надзорным органом вместо множества национальных органов. Следует отличать главное учреждение от простого головного офиса, поскольку главное учреждение определяется не формальным юридическим статусом, а фактическим местом принятия решений об обработке персональных данных и осуществления основной деятельности по такой обработке."
# Вызов для юридического термина
# try:
#     print('start')
#     agent_response = agent.invoke({
#         "messages": [HumanMessage(content=f"Find and translate legal terms in this text: {text}")]
#     })
#     thesaurus = agent_response['messages'][-1].content
#     print(thesaurus)
# except Exception as e:
#     thesaurus = ""
#     print('thesaurus is empty')


from langchain_core.messages import HumanMessage, SystemMessage
from llm.prompt_constructor import PromptTemplates

with open("C:/Users/user/repos/justran/data/Art.4 GDPR.txt", 'r', encoding='utf-8') as f:
    data = f.read()

client = ModelConstructor.create_client("openai/gpt-oss-120b:free")
prompt = PromptTemplates.DEFINITION_LOOKUP_PROMPT.format(glossary=data, text=text)


print('start')

# Прямой вызов модели
response = client.invoke(prompt)

thesaurus = response.content
print(thesaurus)
