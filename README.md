# Multi-Modal Scientific Research Assistant (MSRA)

RAG pipeline for scientific papers. Parses PDFs, embeds chunks into a vector store, and answers questions with citations.

---

## What it does

- Extracts text, tables, and figures from scientific PDFs
- Chunks and embeds content using sentence transformers
- Retrieves relevant sections using semantic search
- Answers questions grounded in the document with page citations
- Handles multimodal content: figures (captioned via vision model) and tables (parsed to markdown)

---

## Architecture

```
PDF
 ├── text    → chunk → embed → ChromaDB
 ├── tables  → markdown → embed → ChromaDB
 └── figures → LLaVA caption → embed → ChromaDB
                                          │
                                    semantic search
                                          │
                                   Groq LLaMA 3.3 70B
                                          │
                              structured answer + citations
```

---

## Stack

| Layer | Tool |
|---|---|
| PDF parsing | pdfplumber + PyMuPDF |
| Embeddings | all-MiniLM-L6-v2 (sentence-transformers) |
| Vector store | ChromaDB |
| LLM | Groq API — LLaMA 3.3 70B |
| Vision | LLaVA via Ollama |
| Backend | FastAPI |
| Frontend | Streamlit |

---

## Project structure

```
MSRA/
├── src/
│   ├── ingestion/       # PDF parsing — text, tables, figures
│   ├── chunking/        # Sentence-based splitting with overlap
│   ├── embeddings/      # Embedding generation + ChromaDB
│   ├── retrieval/       # Retriever + RAG pipeline
│   ├── multimodal/      # Figure captioning + table parsing
│   ├── agents/          # Reasoning agent layer
│   └── api/             # FastAPI backend
├── frontend/            # Streamlit app
├── notebooks/           # Dev and testing scripts
├── data/
│   ├── raw/             # Input PDFs (not committed)
│   ├── processed/       # Extracted figures (not committed)
│   └── vector_db/       # ChromaDB index (not committed)
├── environment.yml
└── .env.example
```

---

## Setup

```bash
git clone https://github.com/imanemn127/Multimodal-Research-Assistant.git
cd MSRA
conda env create -f environment.yml
conda activate msra
cp .env.example .env  # add your API keys
```

---

## Usage

```python
from src.ingestion.parser import PDFParser
from src.chunking.chunker import Chunker
from src.embeddings.embedder import Embedder
from src.embeddings.vector_store import VectorStore
from src.retrieval.retriever import Retriever
from src.retrieval.rag_pipeline import RAGPipeline

# ingest
parser = PDFParser("data/processed/figures")
doc = parser.parse("data/raw/paper.pdf")

chunker = Chunker(max_tokens=512, overlap=100)
chunks = chunker.chunk_document(doc)

embedder = Embedder()
store = VectorStore("data/vector_db")
store.add_chunks(chunks, embedder.embed_texts([c.text for c in chunks]))

# query
pipeline = RAGPipeline(Retriever(embedder, store))
result = pipeline.answer("What methodology did they use?")
print(result["answer"])
```

---

## Roadmap

- [x] PDF ingestion — text, tables, figures
- [x] Chunking with sentence splitting and overlap
- [x] Embeddings + ChromaDB vector store
- [x] RAG pipeline with citations
- [ ] Multimodal — figure captioning, table understanding
- [ ] Agent reasoning layer
- [ ] FastAPI + Streamlit + Docker

---

## Environment variables

```bash
GROQ_API_KEY=   # free at console.groq.com
```
