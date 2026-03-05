import os
from typing import List

try:
    import fitz  # PyMuPDF
except Exception as e:
    raise RuntimeError("PyMuPDF (fitz) is required for PDF extraction") from e

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), 'processed_texts')
os.makedirs(PROCESSED_DIR, exist_ok=True)


def extract_pdf_pages(pdf_path: str) -> List[str]:
    doc = fitz.open(pdf_path)
    pages: List[str] = []
    for page in doc:
        pages.append(page.get_text("text") or "")
    doc.close()
    return pages


def write_raw_text(filename: str, pages: List[str]) -> str:
    raw_path = os.path.join(PROCESSED_DIR, f"{filename}.raw.txt")
    with open(raw_path, 'w', encoding='utf-8') as f:
        for i, page in enumerate(pages):
            f.write(page)
            if i < len(pages) - 1:
                f.write("\n\n")
    return raw_path
