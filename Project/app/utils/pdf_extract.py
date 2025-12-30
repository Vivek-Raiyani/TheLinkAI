import fitz  # pymupdf

def extract_text_from_pdf(path: str) -> str:
    doc = fitz.open(path)
    text = []

    for page in doc:
        page_text = page.get_text()
        if page_text:
            text.append(page_text)

    return "\n".join(text).strip()