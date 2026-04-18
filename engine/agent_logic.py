from engine.rag_pipeline import rag_pipeline

last_modelo = None


#detectar modelo mencionado en la consulta para mejorar respuesta, si no se menciona usar el último modelo detectado
import re

def detectar_modelo(query):
    query = query.lower()

    patrones = [
        r"s\d{2}",     
        r"a\d{2}",     
        r"tab\s?s\d{2}",
    ]

    for patron in patrones:
        match = re.search(patron, query)
        if match:
            return match.group().upper()

    return None

#detectar si la consulta es sobre soporte, configuración o general para mejorar respuesta
def detectar_intent(query):
    query = query.lower()

    soporte_keywords = [
        "problema", "no funciona", "error", "falla",
        "solucion", "arreglar", "mejorar", "reparar",
        "no sirve", "no enfoca", "no carga",
        "bateria", "calienta", "rendimiento"
    ]

    configuracion_keywords = [
        "activar", "configurar", "encender", "desactivar"
    ]

    if any(x in query for x in soporte_keywords):
        return "soporte"

    if any(x in query for x in configuracion_keywords):
        return "configuracion"

    return "general"

#definir tipo de consulta para mejorar respuesta, si es una pregunta general, una consulta sobre un modelo específico o una conversación
def tipo_consulta(query):
    query = query.lower()

    if any(x in query for x in ["porque", "por qué", "como eres", "quien eres"]):
        return "conversacion"

    if any(x in query for x in ["fuera del documento", "que sabes", "en general"]):
        return "general_libre"
    return "rag"

#mejorar consulta agregando modelo si se detecta
def enhance_query(query, modelo):
    if modelo:
        return f"{query} en {modelo}"
    return query


def handle_query(query, vectorstore):
    global last_modelo

    intent = detectar_intent(query)
    modelo = detectar_modelo(query)
    tipo = tipo_consulta(query)

    print(f"[DEBUG] Intent: {intent} | Modelo: {modelo} | Tipo: {tipo}")

# Si no detecta modelo pero ya se había mencionado uno antes, usar el último modelo detectado
    if not modelo and last_modelo:
        modelo = last_modelo
        print(f"Usando modelo anterior: {modelo}")

    if modelo:
        last_modelo = modelo


    if tipo == "conversacion":
        return "Intento ser directo para darte información útil, pero puedo explicarlo más claro si quieres"

    if tipo == "general_libre":
        return (
            "Puedo usar información general además de los documentos. "
            "Dime exactamente qué quieres saber y te ayudo."
        )


    query_mejorada = enhance_query(query, modelo)
    respuesta = rag_pipeline(query_mejorada, vectorstore, modelo)


    if (
        "No encontré" in respuesta
        or "No tengo información" in respuesta
        or "No hay información" in respuesta
    ):
        print("Intentando sin modelo...")

        respuesta = rag_pipeline(query, vectorstore, None)

        if (
            "No encontré" in respuesta
            or "No tengo información" in respuesta
        ):
            return (
                "No encontré esa información en los documentos. "
                "Si quieres, puedo explicarte de forma general o ayudarte con algo relacionado."
            )

    return respuesta