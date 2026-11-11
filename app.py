
import logging
import re

import fitz
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from rag.loader import load_and_split_pdf
from rag.embeddings import create_vector_store
from rag.chatbot import ask_question

from services.pdf_ingestion import (
    save_validated_pdf,
    cleanup_temp_pdf,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    return {"status": "Backend Running Successfully"}


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    temp_path = None

    try:
        # Validate the PDF and save it using a server-generated filename.
        temp_path = await save_validated_pdf(file)

        # Extract text from the PDF.
        text = ""

        with fitz.open(temp_path) as doc:
            for page in doc:
                text += page.get_text()

        # OCR fallback for scanned PDFs.
        if len(text.strip()) < 50:
            from services.ocr import extract_text_from_scanned_pdf
            text = extract_text_from_scanned_pdf(temp_path)

        if not text or not text.strip():
            raise HTTPException(
                status_code=422,
                detail="No readable text could be extracted from the PDF."
            )

        sentences = [
            sentence.strip()
            for sentence in text.split("\n")
            if sentence.strip()
        ]

        if not sentences:
            raise HTTPException(
                status_code=422,
                detail="No readable text could be extracted from the PDF."
            )

        # Stage 1: Information extraction.
        fir = re.findall(r"\d+/\d{4}", text)
        sections = re.findall(r"IPC\s?\d+", text)

        summary = {
            "fir_number": fir[0] if fir else "Not Found",
            "date": "Unknown",
            "police_station": "Unknown",
            "sections": sections if sections else [],
        }

        # Crime classification.
        crime_type = "UNKNOWN"

        if "379" in text or "380" in text or "392" in text:
            crime_type = "Theft / Robbery"

        elif "323" in text or "324" in text:
            crime_type = "Assault / Hurt"

        elif "66C" in text or "66D" in text:
            crime_type = "Cyber Fraud"

        elif "NDPS" in text:
            crime_type = "NDPS"

        # Semantic similarity checklist.
        checklist = []

        item_embeddings = model.encode(checklist_items)
        sentence_embeddings = model.encode(sentences)

        for i, item in enumerate(checklist_items):
            sims = cosine_similarity(
                [item_embeddings[i]],
                sentence_embeddings
            )[0]

            best_score = float(max(sims))
            best_sentence = sentences[int(sims.argmax())]

            status = "MISSING"

            if best_score > 0.75:
                status = "PRESENT"
            elif best_score > 0.55:
                status = "PARTIAL"

            checklist.append({
                "item": item,
                "status": status,
                "similarity_score": round(best_score, 2),
                "matched_text": best_sentence[:150]
            })

        # Simple named entity extraction.
        entities = []

        names = re.findall(
            r"[A-Z][a-z]+\s[A-Z][a-z]+",
            text
        )

        for name in names[:5]:
            entities.append({
                "text": name,
                "type": "PERSON"
            })

        return {
            "summary": summary,
            "crime_type": crime_type,
            "checklist": checklist,
            "entities": entities
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("PDF analysis failed.")
        raise HTTPException(
            status_code=500,
            detail="Unable to process the uploaded PDF."
        )

    finally:
        if temp_path:
            cleanup_temp_pdf(temp_path)


# RAG chatbot feature.

class ChatRequest(BaseModel):
    question: str


@app.post("/api/upload-rag")
async def upload_rag(file: UploadFile = File(...)):
    temp_path = None

    try:
        # Apply the same validation and secure temporary-file handling.
        temp_path = await save_validated_pdf(file)

        chunks = load_and_split_pdf(temp_path)

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="No readable content could be extracted from the PDF."
            )

        create_vector_store(chunks)

        return {
            "message": "Document processed successfully"
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("RAG PDF processing failed.")
        raise HTTPException(
            status_code=500,
            detail="Unable to process the uploaded PDF."
        )

    finally:
        if temp_path:
            cleanup_temp_pdf(temp_path)


@app.post("/api/chat")
async def chat(req: ChatRequest):
    answer = ask_question(req.question)

    return {
        "answer": answer
    }
