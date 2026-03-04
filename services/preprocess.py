import re

def clean_text(text: str) -> str:
    # Normalize multiple spaces
    text = re.sub(r'\s+', ' ', text)

    # Normalize slashes in dates
    text = re.sub(r'\s*/\s*', '/', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text