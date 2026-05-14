from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DocumentMetadata:
    title: str
    file_path: str
    num_pages: int
    authors: List[str] = field(default_factory=list)


@dataclass
class TextSection:
    content: str
    page_num: int
    heading: Optional[str] = None


@dataclass
class Table:
    table_id: str
    content: str          # stored as markdown string
    page_num: int
    caption: Optional[str] = None


@dataclass
class Figure:
    figure_id: str
    image_path: str
    page_num: int
    caption: Optional[str] = None


@dataclass
class Document:
    metadata: DocumentMetadata
    sections: List[TextSection] = field(default_factory=list)
    tables: List[Table] = field(default_factory=list)
    figures: List[Figure] = field(default_factory=list)
