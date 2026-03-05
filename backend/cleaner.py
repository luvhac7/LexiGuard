import os
import re
from typing import List

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), 'processed_texts')
os.makedirs(PROCESSED_DIR, exist_ok=True)

HEADER_FOOTER_SAMPLE_LINES = 4
MAJORITY_THRESHOLD = 0.5


def normalize_newlines(text: str) -> str:
    # Normalize line endings and trim BOM
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    if text.startswith('\ufeff'):
        text = text[1:]
    return text


def detect_repetitive_headers_footers(pages: List[str]) -> set:
    """Detect lines appearing in >50% of pages (first/last 4 lines per page)."""
    line_counts = {}
    total_pages = len(pages)

    def add_line(line: str):
        key = line.strip()
        if not key:
            return
        line_counts[key] = line_counts.get(key, 0) + 1

    for page in pages:
        lines = [l for l in normalize_newlines(page).split('\n') if l is not None]
        top = lines[:HEADER_FOOTER_SAMPLE_LINES]
        bottom = lines[-HEADER_FOOTER_SAMPLE_LINES:] if len(lines) >= HEADER_FOOTER_SAMPLE_LINES else lines
        for l in top + bottom:
            add_line(l)

    repetitive = {line for line, cnt in line_counts.items() if cnt / max(total_pages, 1) > MAJORITY_THRESHOLD}
    return repetitive


def regex_clean(text: str) -> str:
    """Apply deterministic regex cleaning patterns as specified."""
    # Patterns in order of application
    patterns = [
        # Court headers (case-insensitive)
        (r"(?i)IN THE [A-Z \-]+COURT[ \w,]*", ""),
        (r"(?i)IN THE SUPREME COURT", ""),
        
        # Boilerplate markers
        (r"\bREPORTABLE\b", ""),
        (r"\bNOT FOR PUBLICATION\b", ""),
        (r"^\s*JUDGMENT\s*$", ""),  # Only if standalone line
        
        # URLs
        (r"Indian Kanoon - https?://\S+", ""),
        (r"https?://\S+", ""),
        
        # Page numbers
        (r"Page\s*\d+\s*of\s*\d+", ""),
        (r"^\s*\d+\s*$", ""),  # Isolated numeric lines
        
        # Digital signatures (multi-line with DOTALL)
        (r"Digitally signed by.*?(?=\n\n|\n[A-Z]|\Z)", "", re.DOTALL),
        (r"Signature Not Verified.*?(?=\n\n|\n[A-Z]|\Z)", "", re.DOTALL),
        
        # Timestamps
        (r"\b\d{1,2}:\d{2}:\d{2}\s*(IST|UTC)?\b", ""),
        
        # Docket/case number boilerplate (but preserve the actual numbers)
        (r"CIVIL APPEAL NO\.\s*", ""),
        (r"CRIMINAL PETITION NO\.\s*", ""),
        (r"WRIT PETITION NO\.\s*", ""),
        (r"CASE NO\.\s*", ""),
        
        # Reason lines
        (r"^\s*Reason:.*$", "", re.MULTILINE),
    ]
    
    cleaned = text
    for pattern_tuple in patterns:
        if len(pattern_tuple) == 3:
            pat, repl, flags = pattern_tuple
            cleaned = re.sub(pat, repl, cleaned, flags=flags)
        else:
            pat, repl = pattern_tuple
            cleaned = re.sub(pat, repl, cleaned, flags=re.MULTILINE)

    # Fix hyphenation across line breaks
    cleaned = re.sub(r"(\w)-\n(\w)", r"\1\2", cleaned)

    # Collapse multiple newlines to preserve paragraph breaks
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)  # First collapse 3+ to 2
    cleaned = re.sub(r"\n\n+", "\n\n", cleaned)  # Then normalize 2+ to exactly 2
    
    # Normalize inner whitespace (multiple spaces to single) but preserve \n\n
    lines = cleaned.split('\n\n')
    normalized_lines = []
    for para in lines:
        # Within paragraphs, normalize spaces
        para = re.sub(r'[ \t]+', ' ', para).strip()
        if para:
            normalized_lines.append(para)
    cleaned = '\n\n'.join(normalized_lines)

    # Remove very short lines (<4 chars) but preserve legal references
    final_lines = []
    for line in cleaned.split('\n'):
        line = line.strip()
        # Keep if >= 4 chars OR contains legal markers
        if len(line) >= 4 or re.search(r'(Section|Article|s\.|Sec\.|\(\d{4}\)|SCC)', line, re.IGNORECASE):
            final_lines.append(line)
    
    cleaned = '\n'.join(final_lines)
    
    return cleaned.strip()


def remove_headers_footers(pages: List[str]) -> str:
    """Remove repetitive header/footer lines detected across pages."""
    repetitive = detect_repetitive_headers_footers(pages)
    new_pages: List[str] = []
    for page in pages:
        lines = [l for l in normalize_newlines(page).split('\n')]
        filtered = [l for l in lines if l.strip() not in repetitive]
        new_pages.append('\n'.join(filtered))
    return '\n\n'.join(new_pages)


def clean_pages_to_file(filename: str, pages: List[str]) -> str:
    """Clean pages and write to processed_texts/<filename>.clean.txt"""
    joined = remove_headers_footers(pages)
    cleaned = regex_clean(joined)
    out_path = os.path.join(PROCESSED_DIR, f"{filename}.clean.txt")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    return out_path
