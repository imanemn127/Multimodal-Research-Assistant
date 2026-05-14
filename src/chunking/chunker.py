from dataclasses import dataclass
from typing import List
from src.ingestion.models import Document, TextSection


@dataclass
class Chunk:
    chunk_id: str
    text: str
    source: str
    page_num: int
    section: str
    token_count: int


class Chunker:

    def __init__(self, max_tokens: int = 512, overlap: int = 50):
        self.max_tokens = max_tokens
        self.overlap = overlap

    def chunk_document(self, document: Document) -> List[Chunk]:
        all_chunks = []
        source = document.metadata.file_path

        for section in document.sections:
            chunks = self._split_section(section, source)
            all_chunks.extend(chunks)

        return all_chunks

    def _split_section(self, section: TextSection, source: str) -> List[Chunk]:
        sentences = section.content.split('. ')

        chunks = []
        current_sentences = []
        current_tokens = 0
        chunk_index = 0

        for sentence in sentences:
            sentence_tokens = self._count_tokens(sentence)

            if current_tokens + sentence_tokens > self.max_tokens and current_sentences:
                text = '. '.join(current_sentences)
                chunks.append(Chunk(
                    chunk_id=f"{source}_p{section.page_num}_chunk{chunk_index}",
                    text=text,
                    source=source,
                    page_num=section.page_num,
                    section=section.heading or "unknown",
                    token_count=current_tokens
                ))
                chunk_index += 1

                # carry overlap sentences into the next chunk
                overlap_sentences = []
                overlap_tokens = 0
                for s in reversed(current_sentences):
                    if overlap_tokens + self._count_tokens(s) <= self.overlap:
                        overlap_sentences.insert(0, s)
                        overlap_tokens += self._count_tokens(s)
                    else:
                        break

                current_sentences = overlap_sentences
                current_tokens = overlap_tokens

            current_sentences.append(sentence)
            current_tokens += sentence_tokens

        if current_sentences:
            chunks.append(Chunk(
                chunk_id=f"{source}_p{section.page_num}_chunk{chunk_index}",
                text='. '.join(current_sentences),
                source=source,
                page_num=section.page_num,
                section=section.heading or "unknown",
                token_count=current_tokens
            ))

        return chunks

    def _count_tokens(self, text: str) -> int:
        return len(text) // 4
