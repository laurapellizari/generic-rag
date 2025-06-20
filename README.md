# PDF Question Answering with Retrieval-Augmented Generation (RAG)

This project implements a system that allows users to upload PDF documents and ask natural language questions based on their content. The system extracts and embeds content, stores it for retrieval, and uses a Large Language Model (LLM) to generate accurate, context-aware answers.

##  Features

-  Upload one or more PDF documents
-  Chunk and embed document text using Sentence Transformers
-  Store embeddings in Elasticsearch for semantic search
-  Query document content with LLM-powered answers
-  Retrieve source text used to generate each answer
-  Frontend using Streamlit for interaction
-  Dockerized for simple deployment

---

## 🧪 API Specification

### POST `/documents`

Uploads and indexes PDF files.

- **Request**
  - Content-Type: `multipart/form-data`
  - Field: `files` — one or more PDF documents

- **Response**
```json
{
  "message": "Documents processed successfully",
  "documents_indexed": 2,
  "total_chunks": 128
}
```

---

### POST `/question`

Asks a question and returns an answer based on uploaded documents.

- **Request**
  - Content-Type: `application/json`
```json
{
  "question": "What is the power consumption of the motor?",
  "openai_api_key": "your-openai-api-key"
}
```

- **Response**
```json
{
  "answer": "The motor's power consumption is 2.3 kW.",
  "references": [
    "the motor xxx has requires 2.3kw to operate at a 60hz line frequency"
  ]
}
```

---

##  Tech Stack

- Python + Flask (backend API)
- Streamlit (frontend UI)
- Elasticsearch (vector database)
- SentenceTransformers (`all-MiniLM-L6-v2`) for text embeddings
- OpenAI GPT-4 for answering questions
- Docling (for advanced PDF parsing with images)

---

## 🧩 Architecture Overview

```text
[PDF Upload]
     ↓
 [Docling Parsing + Chunking]
     ↓
[SentenceTransformer Embedding]
     ↓
   [Elasticsearch]
     ↓
[Question]
     ↓
[Retrieve Relevant Chunks]
     ↓
[Send to OpenAI GPT with Context]
     ↓
[Answer + References]
```

---

##  Project Structure

```
.
├── app.py                      # Flask backend
├── ui-streamlit.py                       # Streamlit frontend
├── services/
│   ├── extract_text.py         # PDF to text/image extraction
│   ├── embeddings.py           # Chunking and embedding logic
│   └── vector_database.py      # Elasticsearch indexing and retrieval
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Setup Instructions

### 1. Clone the repository


### 2. Create virtual environment
```bash
python -m venv env
source env/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## 4. Docker

You can run the backend and frontend in a Docker container:

```bash
# Build container
docker build --platform linux/arm64 -t generic-rag . 

# Run the container
 podman run --rm -p 5000:5000 -p 8501:8501 generic-rag
```

---

## Optional Enhancements

- Multi-provider LLM support (Watsonx, Claude, Mistral, etc.)
- Image summarization via base64 + prompt
- Stats/logging/monitoring
- PDF viewer on UI

---

