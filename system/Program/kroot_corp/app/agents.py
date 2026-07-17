from langchain_core.prompts import ChatPromptTemplate
from app.llm_config import llm_instance

# 1. El Investigador
researcher_prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un Investigador de Mercado Senior. Tu objetivo es encontrar datos precisos, reales y tendencias actualizadas. Responde solo con hechos y datos clave, sin inventar información."),
    ("human", "Investiga a fondo sobre: '{topico}'. {lecciones_previas}")
])
researcher_chain = researcher_prompt | llm_instance

# 2. El Redactor
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un Redactor de Informes Ejecutivos. Transformas datos crudos en informes profesionales, claros y en formato Markdown."),
    ("human", "Basado en esta investigación:\n\n{investigacion}\n\nRedacta un informe ejecutivo profesional con Introducción, Puntos Clave y Conclusiones.")
])
writer_chain = writer_prompt | llm_instance

# 3. El Crítico (QA)
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un Director de Calidad (QA). Revisas informes, encuentras fallos y das feedback constructivo. Si es bueno, apruébalo. Si es malo, explica por qué y cómo mejorarlo."),
    ("human", "Revisa este informe y emite tu veredicto:\n\n{informe}")
])
critic_chain = critic_prompt | llm_instance