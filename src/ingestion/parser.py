import pdfplumber
import fitz  # pymupdf
from pathlib import Path
from typing import List
from .models import Document, DocumentMetadata, TextSection, Table, Figure


class PDFParser:

    def __init__(self, figures_output_dir: str):
        self.figures_output_dir = Path(figures_output_dir)
        self.figures_output_dir.mkdir(parents=True, exist_ok=True)

    def parse(self, pdf_path: str) -> Document:
        with pdfplumber.open(pdf_path) as pdf:
            metadata = self._extract_metadata(pdf, pdf_path)
            sections = self._extract_text(pdf)
            tables = self._extract_tables(pdf)

        figures = self._extract_figures(pdf_path)

        return Document(
            metadata=metadata,
            sections=sections,
            tables=tables,
            figures=figures
        )

    def _extract_metadata(self, pdf, pdf_path: str) -> DocumentMetadata:
        info = pdf.metadata or {}
        title = info.get("Title", Path(pdf_path).stem)

        return DocumentMetadata(
            title=title,
            file_path=str(pdf_path),
            num_pages=len(pdf.pages)
        )

    def _extract_text(self, pdf) -> List[TextSection]:
        sections = []

        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()

            if text and text.strip():
                # remove header/footer noise: lines shorter than 40 chars
                lines = text.split('\n')
                cleaned_lines = [l for l in lines if len(l.strip()) > 40]
                cleaned_text = '\n'.join(cleaned_lines).strip()

                if cleaned_text:
                    sections.append(TextSection(
                        content=cleaned_text,
                        page_num=page_num
                    ))

        return sections

    def _extract_tables(self, pdf) -> List[Table]:
        tables = []
        table_counter = 1

        for page_num, page in enumerate(pdf.pages, start=1):
            for raw_table in page.extract_tables():
                markdown = self._table_to_markdown(raw_table)

                tables.append(Table(
                    table_id=f"table_{table_counter}",
                    content=markdown,
                    page_num=page_num
                ))
                table_counter += 1

        return tables

    def _table_to_markdown(self, raw_table: list) -> str:
        if not raw_table:
            return ""

        rows = []
        for i, row in enumerate(raw_table):
            cleaned = [str(cell) if cell is not None else "" for cell in row]
            rows.append("| " + " | ".join(cleaned) + " |")

            if i == 0:
                separator = "| " + " | ".join(["---"] * len(row)) + " |"
                rows.append(separator)

        return "\n".join(rows)

    def _extract_figures(self, pdf_path: str) -> List[Figure]:
        figures = []
        figure_counter = 1

        doc = fitz.open(pdf_path)

        for page_num, page in enumerate(doc, start=1):
            for image in page.get_images(full=True):
                xref = image[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                extension = base_image["ext"]

                figure_id = f"figure_{figure_counter}"
                image_filename = f"{figure_id}.{extension}"
                image_path = self.figures_output_dir / image_filename

                with open(image_path, "wb") as f:
                    f.write(image_bytes)

                figures.append(Figure(
                    figure_id=figure_id,
                    image_path=str(image_path),
                    page_num=page_num
                ))
                figure_counter += 1

        doc.close()
        return figures
