
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.ipc_classifier import classify_sections
from services.pdf_ingestion import (
    save_validated_pdf,
    cleanup_temp_pdf
)

from rag.loader import load_and_split_pdf
from rag.embeddings import create_vector_store
from rag.chatbot import ask_question

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

import fitz
import re
import logging


# ==========================================
# APPLICATION CONFIGURATION
# ==========================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ChargeSheet AI Assistant",
    description="AI-powered legal document analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# AI MODEL
# ==========================================

model = SentenceTransformer("all-MiniLM-L6-v2")


# ==========================================
# INVESTIGATION CHECKLIST
# ==========================================

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


# ==========================================
# HOME ROUTE
# ==========================================

@app.get("/")
def home():
    return {
        "status": "Backend Running",
        "application": "ChargeSheet AI Assistant"
    }


# ==========================================
# PDF CHARGESHEET ANALYSIS
# ==========================================

@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):

    # Validate PDF and create a safe temporary file
    temp_path = await save_validated_pdf(file)

    try:

        # ----------------------------------
        # Extract text from searchable PDF
        # ----------------------------------

        with fitz.open(temp_path) as doc:

            text = ""

            for page in doc:
                text += page.get_text()

        # ----------------------------------
        # OCR fallback for scanned PDFs
        # ----------------------------------

        if len(text.strip()) < 50:

            from services.ocr import extract_text_from_scanned_pdf

            text = extract_text_from_scanned_pdf(temp_path)

        if not text.strip():
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
            sentences = ["No readable text found"]

        # ----------------------------------
        # STAGE 1: INFORMATION EXTRACTION
        # ----------------------------------

        fir = re.findall(r"\d+/\d{4}", text)

        sections = re.findall(
            r"IPC\s?\d+",
            text
        )

        summary = {
            "fir_number": fir[0] if fir else "Not Found",
            "date": "Unknown",
            "police_station": "Unknown",
            "sections": sections if sections else [],
        }

        # ----------------------------------
        # IPC / BNS CLASSIFICATION
        # ----------------------------------

        classification = classify_sections(text)

        # ----------------------------------
        # SEMANTIC SIMILARITY CHECKLIST
        # ----------------------------------

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
                "similarity_score": round(
                    float(best_score), 2
                ),
                "matched_text": best_sentence[:150]
            })

        # ----------------------------------
        # SIMPLE NAMED ENTITY RECOGNITION
        # ----------------------------------

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

        # ----------------------------------
        # API RESPONSE
        # ----------------------------------

        return {
            "summary": summary,
            "classification": classification,
            "checklist": checklist,
            "entities": entities
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("Chargesheet analysis failed")

        raise HTTPException(
            status_code=500,
            detail="Unable to process the uploaded PDF."
        )

    finally:
        # Always remove temporary PDF
        cleanup_temp_pdf(temp_path)


# ==========================================
# RAG CHATBOT FEATURE
# ==========================================

class ChatRequest(BaseModel):
    question: str


# ==========================================
# SECURE RAG PDF UPLOAD
# ==========================================

@app.post("/api/upload-rag")
async def upload_rag(file: UploadFile = File(...)):

    # Apply the same PDF validation
    temp_path = await save_validated_pdf(file)

    try:

        # Load and split validated PDF
        chunks = load_and_split_pdf(temp_path)

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="No readable content found in the PDF."
            )

        # Create FAISS vector store
        create_vector_store(chunks)

        return {
            "message": "Document processed successfully",
            "chunks_created": len(chunks)
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("RAG PDF processing failed")

        raise HTTPException(
            status_code=500,
            detail="Unable to process the uploaded document."
        )

    finally:
        # Always remove temporary PDF
        cleanup_temp_pdf(temp_path)


# ==========================================
# CHAT WITH CHARGESHEET
# ==========================================

@app.post("/api/chat")
async def chat(req: ChatRequest):

    try:

        answer = ask_question(req.question)

        return {
            "answer": answer
        }

    except Exception:
        logger.exception("Chat request failed")

        raise HTTPException(
            status_code=500,
            detail="Unable to process your question."
        )
