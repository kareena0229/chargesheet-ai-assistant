from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import re

from services.pdf_reader import extract_text_from_pdf
from services.preprocess import clean_text

app = FastAPI(title="Chargesheet AI API")

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load checklist config
with open("config/checklists.json", "r", encoding="utf-8") as f:
    checklist_data = json.load(f)


# -----------------------------
# Extract Basic Fields
# -----------------------------
def extract_basic_fields(text):

    fir_match = re.search(r"(?:FIR\s*No\.?\s*[:\-]?\s*(\S+))", text, re.IGNORECASE)
    hindi_fir_match = re.search(r"(?:सं\s*[:\-]?\s*(\d+/\d+))", text)

    fir_number = "Not Found"
    if fir_match:
        fir_number = fir_match.group(1)
    elif hindi_fir_match:
        fir_number = hindi_fir_match.group(1)

    date_match = re.search(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", text)
    fir_date = date_match.group(0) if date_match else "Not Found"

    ps_match = re.search(r"(थाना\s*[^\n|]+)", text)
    police_station = ps_match.group(0) if ps_match else "Not Found"

    sections = []

    grouped = re.findall(r"([\d/]+)\s*IPC", text, re.IGNORECASE)
    for group in grouped:
        numbers = group.split("/")
        for num in numbers:
            if num.strip().isdigit():
                sections.append(f"IPC {num.strip()}")

    direct = re.findall(r"IPC\s*(\d+)", text, re.IGNORECASE)
    for num in direct:
        sections.append(f"IPC {num.strip()}")

    sections = list(set(sections))

    return {
        "fir_number": fir_number,
        "fir_date": fir_date,
        "police_station": police_station,
        "legal_sections": sections
    }


# -----------------------------
# Classification
# -----------------------------
def classify_crime(legal_sections):
    for crime_key, crime_data in checklist_data.items():
        for section in crime_data["typical_sections"]:
            if section in legal_sections:
                return crime_key
    return "UNKNOWN"


# -----------------------------
# Checklist Validation
# -----------------------------
def validate_checklist(text, crime_type):

    if crime_type == "UNKNOWN":
        return []

    required = checklist_data[crime_type]["required_items"]
    results = []

    for item in required:
        if item.lower() in text.lower():
            status = "PRESENT"
        else:
            status = "MISSING"

        results.append({
            "item": item,
            "status": status
        })

    return results


# -----------------------------
# Routes
# -----------------------------
@app.get("/")
def root():
    return {"status": "Backend Running Successfully 🚀"}


@app.post("/api/analyze")
async def analyze_pdf(file: UploadFile = File(...)):

    temp_path = f"temp_{file.filename}"

    with open(temp_path, "wb") as f:
        f.write(await file.read())

    raw_text = extract_text_from_pdf(temp_path)
    cleaned_text = clean_text(raw_text)
    os.remove(temp_path)

    basic_info = extract_basic_fields(cleaned_text)
    crime_type = classify_crime(basic_info["legal_sections"])
    checklist = validate_checklist(cleaned_text, crime_type)

    if crime_type == "UNKNOWN":
        classification = {
            "crime_type": "UNKNOWN",
            "reason": "No matching sections found"
        }
    else:
        classification = {
            "crime_type": crime_type,
            "display_name": checklist_data[crime_type]["display_name"]
        }

    return {
        "structured_summary": basic_info,
        "crime_classification": classification,
        "checklist_validation": checklist
    }