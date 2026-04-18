import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

#Cliente LLM
client = OpenAI(
    base_url=os.getenv("GITHUB_ENDPOINT"),
    api_key=os.getenv("GITHUB_TOKEN"),
)

MODEL = os.getenv("GITHUB_MODEL", "gpt-4o-mini")


#Streaming response con validación segura, manejo de errores y mensajes de estado para mejorar UX en la terminal
def thinking(msg):
    print(f"\n {msg}...", flush=True)
    time.sleep(0.5)

def searching(msg):
    print(f"{msg}...", flush=True)
    time.sleep(0.5)

def generating(msg):
    print(f" {msg}...\n", flush=True)
    time.sleep(0.3)


#buscar documentos relevantes en el vectorstore usando la consulta, si se detecta modelo intentar filtrar por ese modelo para mejorar relevancia, sino usar los más similares
def retrieve_documents(query, vectorstore, k=4, modelo=None):
    try:
        docs = vectorstore.similarity_search(query, k=8)

        if modelo:
            docs_modelo = [
                d for d in docs
                if modelo.lower() in d.metadata.get("modelo", "").lower()
            ]

            if docs_modelo:
                return docs_modelo[:k]

        return docs[:k]

    except Exception as e:
        print(f"Retrieval falló: {e}")
        return []


#construir contexto a partir de los documentos recuperados, agregar metadata de modelo y sección para mejorar claridad y relevancia en la generación
def build_context(docs):
    if not docs:
        return ""

    context_parts = []

    for i, doc in enumerate(docs):
        content = doc.page_content.strip()
        metadata = doc.metadata if hasattr(doc, "metadata") else {}

        modelo = metadata.get("modelo", "Desconocido")
        seccion = metadata.get("seccion", "General")

        context_parts.append(
            f"[Doc {i+1} | {modelo} | {seccion}]\n{content}"
        )

    return "\n\n".join(context_parts)


#Streaming response
def stream_response(prompt):
    try:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Asistente técnico Samsung."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            stream=True
        )

        respuesta = ""

        for chunk in stream:
            #validacion de seguridad para evitar errores por chunks vacíos o sin contenido
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            if hasattr(delta, "content") and delta.content:
                texto = delta.content
                print(texto, end="", flush=True)
                respuesta += texto

        print()
        return respuesta

    except Exception as e:
        print(f"Streaming falló: {e}")
        return "Error generando respuesta."


#proceso de stream de resolución de consulta con pasos claros, manejo de casos sin información relevante y mejora de consulta si se detecta modelo para mejorar respuestas
def rag_pipeline(query, vectorstore, modelo=None):

    #pensar
    thinking("Analizando consulta")

    #buscar
    searching("Buscando información relevante")
    docs = retrieve_documents(query, vectorstore, k=4, modelo=modelo)

    if not docs:
        return "No encontré información relevante en los documentos."

    #crear contexto
    context = build_context(docs)

    if not context or len(context.strip()) < 30:
        return "No encontré suficiente información útil."

    #genrar respuesta
    generating("Generando respuesta")

    prompt = f"""
Eres un asistente técnico de Samsung basado en documentos.

REGLAS OBLIGATORIAS:
- Solo para detectar modelos de celulares puedes usar informacion externa, 
    pero para responder la consulta SOLO puedes usar la información que encuentres en el CONTEXTO
- SOLO puedes usar la información del CONTEXTO y armar tu respuesta a partir de eso
- NO puedes usar conocimiento externo a menos que el usuario lo mencione explícitamente en la consulta
- NO puedes inferir ni completar información faltante
- Si la respuesta no está en el contexto, di claramente:
  "que no ha podido encontrar la información en los documentos que tengo disponibles"

COMPORTAMIENTO:
- Responde claro y útil
- Si hay información parcial, responde SOLO con eso
- NO agregues nada extra

CONTEXTO:
{context}

PREGUNTA:
{query}

RESPUESTA:
"""

    return stream_response(prompt)