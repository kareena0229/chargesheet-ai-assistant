
import io
import uuid

import pytest
from fastapi.testclient import TestClient

import app as app_module


@pytest.fixture
def client():
    """Create a FastAPI test client."""
    return TestClient(app_module.app)


# --------------------------------------------------
# TEST 1: Missing document ID
# --------------------------------------------------

def test_chat_missing_document_id_returns_422(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Summarize this chargesheet"
        }
    )

    assert response.status_code == 422


# --------------------------------------------------
# TEST 2: Invalid document ID
# --------------------------------------------------

def test_chat_invalid_document_id_returns_400(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Summarize this chargesheet",
            "document_id": "../db_faiss"
        }
    )

    assert response.status_code == 400


# --------------------------------------------------
# TEST 3: Unknown document ID
# --------------------------------------------------

def test_chat_unknown_document_returns_404(client):
    unknown_id = str(uuid.uuid4())

    response = client.post(
        "/api/chat",
        json={
            "question": "Summarize this chargesheet",
            "document_id": unknown_id
        }
    )

    assert response.status_code == 404


# --------------------------------------------------
# TEST 4: Chat uses the selected document ID
# --------------------------------------------------

def test_chat_returns_selected_document_id(client, monkeypatch):
    document_id = str(uuid.uuid4())

    def fake_ask_question(question, selected_id):
        if selected_id == document_id:
            return "Vehicle theft information"

        return "Unexpected document"

    monkeypatch.setattr(
        app_module,
        "ask_question",
        fake_ask_question
    )

    response = client.post(
        "/api/chat",
        json={
            "question": "What happened?",
            "document_id": document_id
        }
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["document_id"] == document_id
    assert response_data["answer"] == "Vehicle theft information"


# --------------------------------------------------
# TEST 5: Upload generates unique document IDs
# --------------------------------------------------

def test_upload_rag_returns_unique_document_id(client, monkeypatch):
    created_ids = []

    # save_validated_pdf is asynchronous in app.py.
    async def fake_save(file):
        return "synthetic-test.pdf"

    def fake_load(path):
        return ["synthetic document chunk"]

    def fake_create(chunks, document_id):
        created_ids.append(document_id)

    def fake_cleanup(path):
        pass

    # Mock the PDF processing functions.
    monkeypatch.setattr(
        app_module,
        "save_validated_pdf",
        fake_save
    )

    monkeypatch.setattr(
        app_module,
        "load_and_split_pdf",
        fake_load
    )

    monkeypatch.setattr(
        app_module,
        "create_vector_store",
        fake_create
    )

    monkeypatch.setattr(
        app_module,
        "cleanup_temp_pdf",
        fake_cleanup
    )

    # Upload Document A.
    first_response = client.post(
        "/api/upload-rag",
        files={
            "file": (
                "document_A.pdf",
                io.BytesIO(b"synthetic PDF"),
                "application/pdf"
            )
        }
    )

    # Upload Document B.
    second_response = client.post(
        "/api/upload-rag",
        files={
            "file": (
                "document_B.pdf",
                io.BytesIO(b"synthetic PDF"),
                "application/pdf"
            )
        }
    )

    # Verify both uploads succeeded.
    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_id = first_response.json()["document_id"]
    second_id = second_response.json()["document_id"]

    # Verify both IDs are valid UUIDs.
    assert uuid.UUID(first_id)
    assert uuid.UUID(second_id)

    # Verify every upload gets a unique ID.
    assert first_id != second_id

    # Verify the vector-store creation received
    # the correct ID for each uploaded document.
    assert created_ids == [first_id, second_id]
