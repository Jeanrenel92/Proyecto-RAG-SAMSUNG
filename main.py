import os
from dotenv import load_dotenv

# Vectorstore
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# Agente
from engine.agent_logic import handle_query


#cargar variables de entorno para conexión con OpenAI.
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_BASE_URL = os.getenv("GITHUB_BASE_URL")


#inicializar embeddings y vectorstore.
def load_embeddings():
    try:
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=GITHUB_TOKEN,
            base_url=GITHUB_BASE_URL
        )
        print("Embeddings cargados correctamente")
        return embeddings

    except Exception as e:
        print(f"Error cargando embeddings: {e}")
        exit()


#cargar vectorstore FAISS creado previamente.
def load_vectorstore(embeddings):
    try:
        vectorstore = FAISS.load_local(
            "vectorstore", 
            embeddings,
            allow_dangerous_deserialization=True
        )
        #print("Vectorstore cargado correctamente")
        return vectorstore

    except Exception as e:
        print(f"Error cargando vectorstore: {e}")
        print("Asegúrate de haber creado el vectorstore primero")
        exit()


#Loop inicial del asistente.
def main():
    print("Asistente Virtual de Samsung ")
    print("Hola! Soy tu asistente virtual de Samsung. ¿En qué puedo ayudarte?")

    # 1. Inicializar
    embeddings = load_embeddings()
    vectorstore = load_vectorstore(embeddings)

    # 2. Loop de chat
    while True:
        query = input("Tú: ")

        if query.lower() in ["salir", "exit", "quit"]:
            print("Cerrando asistente...")
            break

        try:
            print("\n Asistente:\n")

            _ = handle_query(query, vectorstore)

            print("\n" + "-" * 50)

        except Exception as e:
            print(f"Error procesando la consulta: {e}")


#Ejecutar el asistente
if __name__ == "__main__":
    main()