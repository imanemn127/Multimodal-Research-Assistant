import sys
sys.path.append(".")

from src.embeddings.embedder import Embedder
from src.embeddings.vector_store import VectorStore
from src.retrieval.retriever import Retriever
from src.retrieval.rag_pipeline import RAGPipeline

# load existing vector store (already populated in Phase 3)
embedder = Embedder()
store = VectorStore("data/vector_db")
retriever = Retriever(embedder, store, n_results=3)
pipeline = RAGPipeline(retriever)

# test questions
questions = [
    "What deep learning architecture did they use?",
    "What countries does the dataset cover?",
    "What is the F1 score of the best model?"
]

for q in questions:
    print(f"\n{'='*60}")
    print(f"QUESTION: {q}")
    print('='*60)
    result = pipeline.answer(q)
    print(result["answer"])
