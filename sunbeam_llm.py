import requests
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


# Configuration

CHROMA_DB_DIR = "data/chroma_db"
COLLECTION_NAME = "sunbeam_chunks"

LLM_URL = "http://127.0.0.1:1234/v1/chat/completions"
LLM_MODEL = "phi-3-mini-4k-instruct"

# Embeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# Load existing Chroma DB

vectordb = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=CHROMA_DB_DIR,
    embedding_function=embeddings
)


# Prompt

PROMPT = """
You are a helpful Sunbeam Infotech Assistant for students.

Answer ONLY using the information below.
Do NOT add external knowledge.
If information is missing, reply exactly:
"Information not available in provided data."

Context:
{context}

Question:
{question}

Answer:
"""


# Ask Question Function

def ask_question(question: str) -> str:
    
    retriever = vectordb.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 5,        
            "fetch_k": 12  
        }
    )

    # 
    docs = retriever.invoke(question)

    if not docs:
        return "Information not available in provided data."

    # Combine multiple chunks
    context = "\n\n".join(doc.page_content for doc in docs)

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "user",
                "content": PROMPT.format(
                    context=context,
                    question=question
                )
            }
        ],
        "temperature": 0.1,
        "max_tokens": 350
    }

    try:
        response = requests.post(
            LLM_URL,
            json=payload,
            timeout=60
        )
        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"].strip()

    except Exception as e:
        return f"LLM Error: {e}"
