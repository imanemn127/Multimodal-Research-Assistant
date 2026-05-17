import os
import shutil
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.ingestion.parser import PDFParser
from src.chunking.chunker import Chunker, Chunk
from src.embeddings.embedder import Embedder
from src.embeddings.vector_store import VectorStore
from src.retrieval.retriever import Retriever
from src.retrieval.rag_pipeline import RAGPipeline
from src.agents.research_agent import ResearchAgent
from src.multimodal.figure_captioner import FigureCaptioner

app = FastAPI(title="MSRA — Multi-Modal Scientific Research Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# initialize components once at startup
embedder = Embedder()
store = VectorStore("data/vector_db")
retriever = Retriever(embedder, store, n_results=3)
pipeline = RAGPipeline(retriever)
agent = ResearchAgent(pipeline)
captioner = FigureCaptioner()
parser = PDFParser("data/processed/figures")
chunker = Chunker(max_tokens=512, overlap=100)


class QuestionRequest(BaseModel):
    question: str
    use_agent: bool = True


class AnswerResponse(BaseModel):
    question: str
    answer: str
    sources: list


@app.get("/")
def root():
    return {"status": "running", "chunks_indexed": store.count()}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    pdf_path = f"data/raw/{file.filename}"
    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    doc = parser.parse(pdf_path)
    chunks = chunker.chunk_document(doc)
    embeddings = embedder.embed_texts([c.text for c in chunks])
    store.add_chunks(chunks, embeddings)

    figure_chunks = []
    for figure in doc.figures[:4]:
        caption = captioner.caption_figure(figure.image_path)
        figure_chunks.append(Chunk(
            chunk_id=f"caption_{figure.figure_id}_{file.filename}",
            text=f"[FIGURE: {figure.figure_id}] {caption}",
            source=doc.metadata.file_path,
            page_num=figure.page_num,
            section="figure",
            token_count=len(caption) // 4
        ))

    if figure_chunks:
        fig_embeddings = embedder.embed_texts([c.text for c in figure_chunks])
        store.add_chunks(figure_chunks, fig_embeddings)

    return {
        "filename": file.filename,
        "title": doc.metadata.title,
        "pages": doc.metadata.num_pages,
        "text_chunks": len(chunks),
        "figures_captioned": len(figure_chunks),
        "total_indexed": store.count()
    }


@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    if store.count() == 0:
        raise HTTPException(status_code=400, detail="No documents indexed. Upload a PDF first.")

    if request.use_agent:
        result = agent.answer(request.question)
        return AnswerResponse(
            question=result["question"],
            answer=result["final_answer"],
            sources=result["sub_answers"]
        )
    else:
        result = pipeline.answer(request.question)
        return AnswerResponse(
            question=result["question"],
            answer=result["answer"],
            sources=result["sources"]
        )
