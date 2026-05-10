import fitz  

def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """
    Extract text from PDF page by page.
    Returns a list of pages with page number and text.
    """

    extracted_pages = []

    with fitz.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text()

            extracted_pages.append({
                "page": page_number,
                "text": text.strip()
            })

    return extracted_pages