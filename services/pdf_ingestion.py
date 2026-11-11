
import logging
import os
import tempfile

import fitz
from fastapi import HTTPException, UploadFile

logger = logging.getLogger(__name__)

# Maximum upload size: 10 MB
MAX_PDF_SIZE = 10 * 1024 * 1024

# Read uploads in 1 MB chunks
CHUNK_SIZE = 1024 * 1024

PDF_SIGNATURE = b"%PDF-"
PDF_HEADER_CHECK_SIZE = 1024


async def save_validated_pdf(file: UploadFile) -> str:
    """
    Validate an uploaded PDF and save it to a server-generated
    temporary file. The caller is responsible for deleting the
    returned file after processing.
    """
    temp_path = None

    try:
        # 1. Validate the filename extension.
        # The original filename is never used to create a filesystem path.
        filename = file.filename or ""

        if not filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=415,
                detail="Only PDF files are allowed."
            )

        # 2. Validate the declared MIME type.
        allowed_mime_types = {
            "application/pdf",
            "application/octet-stream"
        }

        if file.content_type not in allowed_mime_types:
            raise HTTPException(
                status_code=415,
                detail="Unsupported file type."
            )

        # 3. Create a server-controlled temporary file.
        fd, temp_path = tempfile.mkstemp(
            prefix="chargesheet_",
            suffix=".pdf"
        )

        total_size = 0
        header = bytearray()

        with os.fdopen(fd, "wb") as temp_file:
            while True:
                chunk = await file.read(CHUNK_SIZE)

                if not chunk:
                    break

                total_size += len(chunk)

                # 4. Enforce the maximum upload size.
                if total_size > MAX_PDF_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="PDF exceeds the maximum allowed size of 10 MB."
                    )

                # 5. Capture the first 1024 bytes for signature validation.
                if len(header) < PDF_HEADER_CHECK_SIZE:
                    remaining = PDF_HEADER_CHECK_SIZE - len(header)
                    header.extend(chunk[:remaining])

                temp_file.write(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded PDF is empty."
            )

        if PDF_SIGNATURE not in header:
            raise HTTPException(
                status_code=415,
                detail="Invalid PDF file."
            )

        # 6. Verify that the file can actually be opened as a PDF.
        try:
            with fitz.open(temp_path) as document:
                if document.is_encrypted:
                    raise HTTPException(
                        status_code=400,
                        detail="Password-protected PDFs are not supported."
                    )

                if len(document) == 0:
                    raise HTTPException(
                        status_code=400,
                        detail="PDF contains no pages."
                    )

        except HTTPException:
            raise

        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid or corrupted PDF document."
            )

        return temp_path

    except Exception:
        # Delete partially uploaded or invalid files.
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                logger.exception("Failed to remove temporary PDF after validation failure.")

        raise

    finally:
        await file.close()


def cleanup_temp_pdf(temp_path: str) -> None:
    """Remove a temporary PDF after processing."""

    if not temp_path:
        return

    try:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    except OSError:
        logger.exception("Failed to remove temporary PDF after processing.")
