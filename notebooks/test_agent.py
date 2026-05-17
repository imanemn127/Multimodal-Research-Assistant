import sys
sys.path.append(".")

from src.embeddings.embedder import Embedder
from src.embeddings.vector_store import VectorStore
from src.retrieval.retriever import Retriever
from src.retrieval.rag_pipeline import RAGPipeline
from src.agents.research_agent import ResearchAgent

embedder = Embedder()
store = VectorStore("data/vector_db")
retriever = Retriever(embedder, store, n_results=3)
pipeline = RAGPipeline(retriever)
agent = ResearchAgent(pipeline)

# complex question that benefits from decomposition
result = agent.answer(
    "Compare the performance of the S2 and GM models — which is better and why?"
)

print("\n" + "="*60)
print("FINAL ANSWER:")
print("="*60)
print(result["final_answer"])
