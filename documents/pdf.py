"""Extract text from a PDF while preserving page references."""

from dataclasses import dataclass
from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PyPdfError


@dataclass(frozen=True)
class PdfPage:
    """Store the extracted text and its one-based position in the PDF."""
    number: int
    text: str


def read_pdf_pages(content:bytes) -> list[PdfPage]:
    """Read PDF text in page order, retaining blank pages."""
    try:
        reader = PdfReader(BytesIO(content))

        if reader.is_encrypted:
            raise ValueError("The PDF is secured. Use a copy without password.")

        pages = [
            PdfPage(number=number, text=page.extract_text().strip())
            for number, page in enumerate(reader.pages, start=1)
        ]
    except (PyPdfError, OSError) as error:
        raise ValueError("PDF could not be read.") from error

    if not any(page.text for page in pages):
        raise ValueError("The PDF does not contains extractable text. Use a copy with text.")

    return pages
