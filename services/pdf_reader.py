import fitz  # PyMuPDF

def extract_text_from_pdf(file_path: str) -> str:
    text = ""

    try:
        doc = fitz.open(file_path)

        for page in doc:
            text += page.get_text()

        doc.close()

    except Exception as e:
        return f"Error reading PDF: {str(e)}"

    return text