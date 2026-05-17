# MSRA — Multi-Modal Scientific Research Assistant

This is a multimodal RAG system for scientific PDFs. It ingests papers, extracts text, tables, and figures, and allows question answering over the document with page-level citations.

The system is built as a full retrieval pipeline: PDF ingestion → chunking → embedding → vector search → generation, with a lightweight agent layer that decomposes complex queries into sub-questions.

---

## What it does

- Parses PDFs: text (pdfplumber), tables (converted to markdown), figures (PyMuPDF, saved as images)
- Chunks text with sentence splitting and configurable overlap
- Captions figures using a Groq-hosted vision LLM, then embeds captions alongside text
- Stores everything in a persistent ChromaDB collection with cosine similarity
- Retrieves semantically relevant chunks at query time
- Answers questions via Groq LLaMA 3.3 70B with page citations
- Agent mode: decomposes complex questions into sub-questions, runs RAG on each, synthesizes a final answer

---

## Architecture

```
PDF
 ├── text    ──→ sentence-split chunks ──→ embed ──→ ChromaDB
 ├── tables  ──→ markdown               ──→ embed ──→ ChromaDB
 └── figures ──→ Groq vision (LLaMA 4 Scout) captions ──→ embed ──→ ChromaDB
                                                                       │
                                                              cosine similarity search
                                                                       │
                                                          Groq LLaMA 3.3 70B
                                                                       │
                                                    answer + page citations
```

**Agent mode** adds a reasoning layer before retrieval:

```
question
   └──→ _plan()     — LLM decomposes into 2-3 sub-questions
   └──→ _execute()  — RAG pipeline runs on each sub-question independently
   └──→ _synthesize() — LLM combines sub-answers into a structured final answer
```

---

## Stack

| Layer | Tool |
|---|---|
| PDF parsing | pdfplumber (text/tables) + PyMuPDF (figures) |
| Embeddings | all-MiniLM-L6-v2 — sentence-transformers, runs locally |
| Vector store | ChromaDB — persistent, cosine similarity (hnsw:space=cosine) |
| Text LLM | Groq API — llama-3.3-70b-versatile |
| Vision LLM | Groq API — meta-llama/llama-4-scout-17b-16e-instruct |
| Backend | FastAPI |
| Frontend | Streamlit |

Embeddings are generated locally (no API cost). All LLM inference goes through Groq's free tier.

---

## Project structure

```
MSRA/
├── src/
│   ├── ingestion/       # PDFParser — text, tables, figures
│   ├── chunking/        # Sentence-based chunker with overlap
│   ├── embeddings/      # Embedder + VectorStore (ChromaDB)
│   ├── retrieval/       # Retriever + RAGPipeline
│   ├── multimodal/      # FigureCaptioner (vision LLM)
│   ├── agents/          # ResearchAgent — plan/execute/synthesize
│   └── api/             # FastAPI app
├── frontend/            # Streamlit app
├── notebooks/           # Dev scripts
├── data/
│   ├── raw/             # Input PDFs (gitignored)
│   ├── processed/       # Extracted figures (gitignored)
│   └── vector_db/       # ChromaDB index (gitignored)
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
cp .env.example .env    # add your Groq API key
```

Get a free Groq API key at [console.groq.com](https://console.groq.com).

---

## Running

```bash
# terminal 1 — backend
uvicorn src.api.main:app --reload

# terminal 2 — frontend
streamlit run frontend/app.py
```

Open `http://localhost:8501`. Upload a PDF, then ask questions.

---

## Pipeline details

### Chunking

Sentence-based splitting with a sliding window. Parameters: `max_tokens=512`, `overlap=100`. Token count is approximated as `len(text) // 4`. Overlap is carried forward as a sentence buffer, not a character slice — so chunk boundaries stay at sentence edges.

### Embeddings

`all-MiniLM-L6-v2` produces 384-dimensional vectors. Two methods: `embed_texts()` for batch ingestion, `embed_query()` for single-query retrieval. Embeddings are computed locally using sentence-transformers (no external API dependency).

### Figure captioning

Figures are extracted per-page using PyMuPDF, saved as PNG. Each image is base64-encoded and sent to the Groq vision endpoint. The caption is stored as a chunk with a `[FIGURE: fig_X]` prefix so the retriever can surface it like any text chunk. Capped at 4 figures per upload to stay within free-tier rate limits.

### Agent reasoning

`ResearchAgent` wraps `RAGPipeline`. The `_plan()` step prompts the LLM to return a JSON array of 2-3 sub-questions. Each sub-question goes through a full retrieval + generation cycle. `_synthesize()` sends all sub-answers back to the LLM for a structured final answer. Simple but effective for multi-part questions.

---

## Known limitations

- **Two-column PDF layouts** produce noisy chunks. pdfplumber reads across columns, so text from adjacent columns gets merged. Partial workaround: lines under 40 characters are filtered out. Proper fix would require layout-aware parsing (e.g. marker or nougat).
- **Figure count** is capped at 4 per upload — Groq free tier rate limits.
- **Duplicate chunks** accumulate if the same PDF is uploaded multiple times. `notebooks/reset_db.py` wipes the collection.
- **Title extraction** falls back to filename — most PDFs don't embed structured metadata.
- **No Docker setup** yet.

---

## Roadmap

- [x] PDF ingestion — text, tables, figures
- [x] Sentence-based chunking with overlap
- [x] Local embeddings + ChromaDB vector store
- [x] RAG pipeline with page citations
- [x] Figure captioning via vision LLM
- [x] Agent reasoning layer
- [x] FastAPI backend + Streamlit frontend
- [ ] Docker

---

## Environment variables

```bash
GROQ_API_KEY=   # console.groq.com — free tier
```
