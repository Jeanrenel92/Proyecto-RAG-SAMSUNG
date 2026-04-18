Asistente Samsung con RAG (LLM + FAISS)
Descripción
Este proyecto implementa un asistente inteligente para soporte técnico de dispositivos Samsung utilizando:
•	Modelos de lenguaje (LLM)
•	Arquitectura RAG (Retrieval-Augmented Generation)
•	Base vectorial FAISS
El sistema permite responder consultas de usuarios utilizando información real proveniente de documentos técnicos.
________________________________________
Funcionalidades
•	Búsqueda semántica en documentos
•	Memoria de conversación
•	Detección automática de modelo (Galaxy S, A, Tab)
•	Soporte técnico y configuración
•	Respuestas en streaming (tipo ChatGPT)
________________________________________
Arquitectura
Usuario → Agent Logic → RAG Pipeline → FAISS → LLM → Respuesta
________________________________________
Estructura del proyecto
project/
│
├── engine/
│   ├── agent_logic.py
│   └── rag_pipeline.py
│
├── data/
│   ├── galaxy_s25.docx
│   ├── galaxy_a57.docx
│   └── tab_s11.docx
│
├── vectorstore/
│
├── main.py
├── create_vectorstore.py
└── .env
________________________________________
 Requisitos
•	Python 3.10 o 3.11
•	pip
________________________________________
 Instalación
pip install -r requirements.txt
Si no tienes requirements:
pip install langchain openai faiss-cpu python-dotenv unstructured
________________________________________
Configuración
Crear archivo .env:
GITHUB_TOKEN=tu_token
GITHUB_ENDPOINT=tu_endpoint
GITHUB_MODEL=gpt-4o-mini
________________________________________
Crear base de conocimiento
python create_vectorstore.py
Esto:
•	Lee documentos
•	Genera embeddings
•	Crea FAISS
________________________________________
Ejecutar el sistema
python main.py
________________________________________
Ejemplo de uso
Tú: como mejorar la bateria del galaxy a57
Asistente:
...
________________________________________
Limitaciones
•	Depende de la calidad de los documentos
•	No responde fuera del contexto
•	Puede fallar con consultas ambiguas
________________________________________
Mejoras futuras
•	Citas de fuentes
•	Ranking de documentos
•	Integración con APIs reales
________________________________________
Autor
Jr Darius– Evaluación 1 RAG + LLM

