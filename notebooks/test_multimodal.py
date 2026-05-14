import sys
sys.path.append(".")

from src.ingestion.parser import PDFParser
from src.chunking.chunker import Chunk
from src.multimodal.figure_captioner import FigureCaptioner
from src.embeddings.embedder import Embedder
from src.embeddings.vector_store import VectorStore
from src.retrieval.retriever import Retriever
from src.retrieval.rag_pipeline import RAGPipeline

# parse document to get Figure objects with correct page numbers
parser = PDFParser("data/processed/figures")
doc = parser.parse("data/raw/AI4SmallFarms_paper.pdf")

embedder = Embedder()
store = VectorStore("data/vector_db")
captioner = FigureCaptioner()

print(f"Found {len(doc.figures)} figures. Captioning first 4...")

figure_chunks = []

for figure in doc.figures[:4]:  # limit to 4 to save API quota
    print(f"  Captioning {figure.figure_id} (page {figure.page_num})...")

    caption = captioner.caption_figure(figure.image_path)

    chunk = Chunk(
        chunk_id=f"caption_{figure.figure_id}",
        text=f"[FIGURE: {figure.figure_id}] {caption}",
        source=doc.metadata.file_path,
        page_num=figure.page_num,
        section="figure",
        token_count=len(caption) // 4
    )
    figure_chunks.append(chunk)

embeddings = embedder.embed_texts([c.text for c in figure_chunks])
store.add_chunks(figure_chunks, embeddings)
print(f"Added {len(figure_chunks)} figure captions to vector store.")
print(f"Total chunks in store: {store.count()}")

# test a figure question
retriever = Retriever(embedder, store, n_results=3)
pipeline = RAGPipeline(retriever)

result2 = pipeline.answer("What does figure 1 show?")
print(f"\nQuestion: What does figure 1 show?")
print(f"\nAnswer:\n{result2['answer']}")