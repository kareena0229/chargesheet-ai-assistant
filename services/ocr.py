import pytesseract
from pdf2image import convert_from_path

# Uncomment and edit if Tesseract isn't in PATH:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_scanned_pdf(pdf_path):

    pages = convert_from_path(pdf_path)

    text = ""

    for page in pages:
        text += pytesseract.image_to_string(page)

    return text