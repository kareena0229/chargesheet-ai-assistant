# Ticket 1: Make PDF Ingestion Safe and Reliable

## Overview

Implemented secure PDF ingestion for the ChargeSheet AI Assistant. The implementation validates uploaded PDF files, enforces upload limits, uses server-generated temporary filenames, handles processing errors safely, and removes temporary files after processing.

## Implementation Details

### 1. File Validation
- Accepts PDF files only.
- Checks the uploaded filename extension.
- Validates the declared MIME type.
- Checks for the PDF signature (`%PDF-`) within the first 1024 bytes.
- Uses PyMuPDF to verify that the document can be opened.
- Rejects encrypted and empty PDFs.

### 2. Upload Size Limit
- Maximum upload size: 10 MB.
- Reads uploaded content in 1 MB chunks.
- Returns HTTP 413 when the limit is exceeded.

### 3. Secure Temporary File Handling
- Uses Python's `tempfile.mkstemp()` to generate server-controlled temporary filenames.
- Never uses the original uploaded filename to construct a filesystem path.
- Removes partially uploaded files after validation failures.
- Removes temporary PDFs after successful and failed processing.

### 4. Error Handling
- HTTP 415: Unsupported or invalid file type.
- HTTP 413: Upload exceeds 10 MB.
- HTTP 400: Empty, encrypted, or corrupted PDF.
- HTTP 422: No readable content or chunks found.
- HTTP 500: Unexpected processing failure, with a generic client-facing error.

### 5. Endpoint Integration
- `/api/analyze`: Uses shared PDF validation, text extraction, OCR fallback, and guaranteed temporary-file cleanup.
- `/api/upload-rag`: Uses the same validation and cleanup mechanism before document processing.

## Dependencies

- FastAPI 0.104.1
- PyMuPDF 1.23.8
- python-multipart 0.0.6
- pytesseract 0.3.13
- pdf2image 1.17.0

OCR execution additionally requires the external Tesseract OCR executable and Poppler utilities.

## Acceptance Test Evidence

| Test | Result |
|---|---|
| Valid PDF upload | Passed |
| Fake PDF / renamed text file | Passed |
| Oversized PDF (11 MB) | Passed |
| Corrupted PDF | Passed |
| Successful processing cleanup | Passed |
| Failed validation cleanup | Passed |
| Path-like filename protection | Passed |
| Simulated OCR failure cleanup | Passed |
| Actual `/api/analyze` OCR failure cleanup | Passed |

## Scope

This implementation focuses on PDF upload validation, safe temporary-file management, and error handling. Authentication, cloud storage, and AI/RAG logic changes are outside the scope of this ticket.

## Configuration

The maximum upload size is configured in `services/pdf_ingestion.py`:

`MAX_PDF_SIZE = 10 * 1024 * 1024`
