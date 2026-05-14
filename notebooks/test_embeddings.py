import sys
sys.path.append(".")

from src.ingestion.parser import PDFParser
from src.chunking.chunker import Chunker
from src.embeddings.embedder import Embedder
from src.embeddings.vector_store import VectorStore

# Step 1: parse
parser = PDFParser("data/processed/figures")
doc = parser.parse("data/raw/AI4SmallFarms_paper.pdf")

# Step 2: chunk
chunker = Chunker(max_tokens=512, overlap=100)
chunks = chunker.chunk_document(doc)
print(f"Chunks: {len(chunks)}")

# Step 3: embed
embedder = Embedder()
texts = [chunk.text for chunk in chunks]
embeddings = embedder.embed_texts(texts)
print(f"Embeddings shape: {len(embeddings)} x {len(embeddings[0])}")

# Step 4: store
store = VectorStore("data/vector_db")
store.add_chunks(chunks, embeddings)
print(f"Total in vector store: {store.count()}")

# Step 5: query
query = "What deep learning architecture did they use?"
query_vec = embedder.embed_query(query)
results = store.query(query_vec, n_results=3)

print(f"\n--- Query: {query} ---")
for i, r in enumerate(results):
    print(f"\nResult {i+1} (distance: {r['distance']:.4f})")
    print(f"Source: page {r['metadata']['page_num']}")
    print(f"Text: {r['text'][:300]}")
