from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import fitz
import re
from rag.loader import load_and_split_pdf
from rag.embeddings import create_vector_store
from rag.chatbot import ask_question
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pydantic import BaseModel
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = SentenceTransformer("all-MiniLM-L6-v2")

checklist_items = [
"FIR number and date",
"Police station name",
"Place and time of occurrence",
"Details of complainant and accused",
"Description of stolen property and value",
"Recovery/seizure memo of property",
"Witness statements",
"Site plan / spot inspection memo",
"Arrest memo",
"Chain of custody of recovered items"
]


@app.get("/")
def home():
    return {"status": "Backend Running 🚀"}


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):

    pdf_bytes = await file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    text = ""

    # -----------------------------
    # Extract text from searchable PDF
    # -----------------------------
    for page in doc:
        text += page.get_text()

    # -----------------------------
    # OCR fallback for scanned PDFs
    # -----------------------------
    if len(text.strip()) < 50:

        from services.ocr import extract_text_from_scanned_pdf

        temp_path = f"temp_{file.filename}"

        with open(temp_path, "wb") as f:
            f.write(pdf_bytes)

        text = extract_text_from_scanned_pdf(temp_path)

    sentences = text.split("\n")

    # -----------------------------
    # Stage 1 Extraction
    # -----------------------------
    fir = re.findall(r"\d+/\d{4}", text)
    sections = re.findall(r"IPC\s?\d+", text)

    summary = {
        "fir_number": fir[0] if fir else "Not Found",
        "date": "Unknown",
        "police_station": "Unknown",
        "sections": sections if sections else [],
    }

    # -----------------------------
    # Crime Classification
    # -----------------------------
    crime_type = "UNKNOWN"

    if "379" in text or "380" in text or "392" in text:
        crime_type = "Theft / Robbery"

    elif "323" in text or "324" in text:
        crime_type = "Assault / Hurt"

    elif "66C" in text or "66D" in text:
        crime_type = "Cyber Fraud"

    elif "NDPS" in text:
        crime_type = "NDPS"

    # -----------------------------
    # Semantic Similarity Checklist
    # -----------------------------
    checklist = []

    item_embeddings = model.encode(checklist_items)
    sentence_embeddings = model.encode(sentences)

    for i, item in enumerate(checklist_items):

        sims = cosine_similarity(
            [item_embeddings[i]],
            sentence_embeddings
        )[0]

        best_score = max(sims)
        best_sentence = sentences[sims.argmax()]

        status = "MISSING"

        if best_score > 0.75:
            status = "PRESENT"

        elif best_score > 0.55:
            status = "PARTIAL"

        checklist.append({
            "item": item,
            "status": status,
            "similarity_score": round(float(best_score), 2),
            "matched_text": best_sentence[:150]
        })

    # -----------------------------
    # Simple NER
    # -----------------------------
    entities = []

    names = re.findall(
        r"[A-Z][a-z]+\s[A-Z][a-z]+",
        text
    )

    for n in names[:5]:

        entities.append({
            "text": n,
            "type": "PERSON"
        })

    return {
        "summary": summary,
        "crime_type": crime_type,
        "checklist": checklist,
        "entities": entities
    }
# ==============================
# RAG CHATBOT FEATURE
# ==============================

class ChatRequest(BaseModel):
    question: str


@app.post("/api/upload-rag")
async def upload_rag(file: UploadFile = File(...)):

    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    chunks = load_and_split_pdf(file_path)

    create_vector_store(chunks)

    return {
        "message": "Document processed successfully"
    }


@app.post("/api/chat")
async def chat(req: ChatRequest):

    answer = ask_question(req.question)

    return {
        "answer": answer
    }