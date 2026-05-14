from typing import List, Dict, Any
from src.embeddings.embedder import Embedder
from src.embeddings.vector_store import VectorStore


class Retriever:

    def __init__(self, embedder: Embedder, vector_store: VectorStore, n_results: int = 5):
        self.embedder = embedder
        self.vector_store = vector_store
        self.n_results = n_results

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        query_vector = self.embedder.embed_query(query)
        results = self.vector_store.query(query_vector, n_results=self.n_results)
        return results

    def format_context(self, results: List[Dict[str, Any]]) -> str:
        context_parts = []

        for i, result in enumerate(results):
            source = result["metadata"]["source"]
            page = result["metadata"]["page_num"]
            text = result["text"]

            context_parts.append(
                f"[Source {i+1} | Page {page}]\n{text}"
            )

        return "\n\n---\n\n".join(context_parts)
