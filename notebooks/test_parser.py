from src.ingestion.parser import PDFParser
from src.chunking.chunker import Chunker

parser = PDFParser("data/processed/figures")
doc = parser.parse("data/raw/AI4SmallFarms_paper.pdf")
chunker = Chunker(max_tokens=512, overlap=100)
chunks = chunker.chunk_document(doc)

print(f"Total chunks: {len(chunks)}")
print(f"\n--- Chunk 0 last 200 chars ---")
print(chunks[0].text[-200:])
print(f"\n--- Chunk 1 first 200 chars ---")
print(chunks[1].text[:200:])



