import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
from src.chunking.chunker import Chunk


class VectorStore:

    def __init__(self, persist_directory: str = "data/vector_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="msra_chunks",
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        self.collection.add(
            ids=[chunk.chunk_id for chunk in chunks],
            embeddings=embeddings,
            documents=[chunk.text for chunk in chunks],
            metadatas=[{
                "source": chunk.source,
                "page_num": chunk.page_num,
                "section": chunk.section,
                "token_count": chunk.token_count
            } for chunk in chunks]
        )
        print(f"Added {len(chunks)} chunks to vector store.")

    def query(self, query_embedding: List[float], n_results: int = 5) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        retrieved = []
        for i in range(len(results["documents"][0])):
            retrieved.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })

        return retrieved

    def count(self) -> int:
        return self.collection.count()
