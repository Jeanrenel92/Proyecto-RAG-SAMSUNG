import os
from dotenv import load_dotenv

# Loaders
from langchain_community.document_loaders import UnstructuredWordDocumentLoader

# Splitter
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Vectorstore
from langchain_community.vectorstores import FAISS

# Embeddings
from langchain_openai import OpenAIEmbeddings

load_dotenv()


#crear vectorstore a partir de documentos DOCX, luego cargarlo en main.py para usarlo en el agente
DATA_FOLDER = "data"
VECTORSTORE_PATH = "vectorstore"


#cargar documentos y agregar metadata de modelo
def load_documents():
    documents = []

    for file in os.listdir(DATA_FOLDER):
        if file.endswith(".docx"):
            path = os.path.join(DATA_FOLDER, file)

            loader = UnstructuredWordDocumentLoader(path)
            docs = loader.load()

            # Normalizar nombre del modelo
            modelo = file.replace(".docx", "").replace("_", " ").upper()

            for doc in docs:
                doc.metadata["modelo"] = modelo

            documents.extend(docs)

    print(f"Documentos cargados: {len(documents)}")
    return documents


#dividir documentos en chunks para mejorar embeddings, agregar metadata de modelo a cada chunk para mejorar respuestas
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(documents)

    print(f"Chunks creados: {len(chunks)}")
    return chunks


#crear embeddings usando OpenAI y luego crear vectorstore FAISS a partir de los chunks, guardar localmente para cargar en main.py
def create_embeddings():
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=os.getenv("GITHUB_TOKEN"),
        base_url=os.getenv("GITHUB_BASE_URL")
    )

    return embeddings


#crear vectorstore FAISS a partir de los chunks y embeddings, guardar localmente para cargar en main.py
def create_vectorstore(chunks, embeddings):
    print("Generando embeddings por lotes...")

    BATCH_SIZE = 50
    vectorstore = None

    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]

        print(f"Procesando lote {i} - {i + len(batch)}")

        if vectorstore is None:
            vectorstore = FAISS.from_documents(batch, embeddings)
        else:
            vectorstore.add_documents(batch)

    vectorstore.save_local(VECTORSTORE_PATH)

    print("Vectorstore creado correctamente")


#cargar los docs en main.py, dividirlos en chunks, crear embeddings y luego vectorstore para usarlo en el agente
def main():
    docs = load_documents()

    if not docs:
        print(" No se encontraron documentos en la carpeta 'data'")
        return

    chunks = split_documents(docs)
    embeddings = create_embeddings()
    create_vectorstore(chunks, embeddings)


if __name__ == "__main__":
    main()