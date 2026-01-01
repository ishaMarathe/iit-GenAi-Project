import re
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# -----------------------------
# Configuration
# -----------------------------
DATA_PATH = "data/sunbeam_complete_data.txt"

CHROMA_DB_DIR = "data/chroma_db"
COLLECTION_NAME = "sunbeam_chunks"

CHUNK_SIZE = 2000
CHUNK_OVERLAP = 500

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

PRINT_CHUNKS = 3
CHUNK_OUTPUT_FILE = "data/sunbeam_chunks.txt"


# -----------------------------
# Text Cleaning (FIXED)
# -----------------------------
def clean_text(text: str) -> str:
    noise_patterns = [
        r"CLICK TO REGISTER",
        r"REGISTER NOW",
        r"Powered by.*",

        r"\bdownload\b",
        r"download\s*:\s*['\"]?\s*['\"]?",
    ]

    for pattern in noise_patterns:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)

    # normalize spacing
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\s{2,}", " ", text)

    return text.strip()


# -----------------------------
# Chunking
# -----------------------------
def chunk_text(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n\n\n",
            "\n\n" ,        # sections
            "\n",     # paragraphs
                      
            " ",
            ""
        ]
    )

    base_doc = Document(
        page_content=text,
        metadata={"source": DATA_PATH}
    )

    chunks = splitter.split_documents([base_doc])

    for i, chunk in enumerate(chunks, start=1):
        chunk.metadata["chunk_id"] = i

    return chunks


# -----------------------------
# Save chunks to file
# -----------------------------
def save_chunks(chunks):
    with open(CHUNK_OUTPUT_FILE, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(f"CHUNK ID: {chunk.metadata['chunk_id']}\n")
            f.write(chunk.page_content.strip() + "\n\n")


# -----------------------------
# Main Pipeline
# -----------------------------
def main():
    print("Loading file...")
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw_text = f.read()

    print("Cleaning text...")
    cleaned_text = clean_text(raw_text)

    print("Chunking text...")
    chunks = chunk_text(cleaned_text)
    print(f"Generated {len(chunks)} chunks")

    print("Saving chunks to file...")
    save_chunks(chunks)
    print(f"Chunks saved to {CHUNK_OUTPUT_FILE}")

    print("Embedding & storing in ChromaDB...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    vectordb = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embeddings
    )

    vectordb.add_documents(chunks)
    vectordb.persist()

    print("RAG ingestion completed successfully!")


if __name__ == "__main__":
    main()
