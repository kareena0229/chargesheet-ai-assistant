
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from langchain_core.documents import Document

from rag import embeddings
from rag.chatbot import ask_question


@pytest.fixture
def isolated_store(tmp_path, monkeypatch):
    """Use a temporary vectorstore directory for each test."""
    monkeypatch.setattr(
        embeddings,
        "VECTORSTORE_ROOT",
        tmp_path / "vectorstore"
    )
    return tmp_path / "vectorstore"


def test_document_ids_are_validated():
    valid_id = "f0b66ea3-dbe9-42ad-aac5-2e2bf3c4202d"

    assert embeddings.validate_document_id(valid_id) == valid_id

    with pytest.raises(ValueError):
        embeddings.validate_document_id("../db_faiss")

    with pytest.raises(ValueError):
        embeddings.validate_document_id("invalid-id")


def test_each_document_gets_separate_index(isolated_store, monkeypatch):
    document_a = "f0b66ea3-dbe9-42ad-aac5-2e2bf3c4202d"
    document_b = "428d0142-5789-41f0-b765-a9d872dbc7f8"

    def fake_create_and_save(chunks, path):
        Path(path, "index.faiss").write_text("fake index")
        Path(path, "index.pkl").write_text("fake metadata")

    monkeypatch.setattr(
        embeddings.FAISS,
        "from_documents",
        lambda chunks, model: MagicMock(
            save_local=lambda path: fake_create_and_save(chunks, path)
        )
    )

    embeddings.create_vector_store(
        [Document(page_content="Vehicle theft case")],
        document_a
    )

    embeddings.create_vector_store(
        [Document(page_content="Missing person case")],
        document_b
    )

    assert (isolated_store / document_a / "index.faiss").exists()
    assert (isolated_store / document_b / "index.faiss").exists()
    assert (isolated_store / document_a) != (isolated_store / document_b)


def test_empty_chunks_are_rejected(isolated_store):
    with pytest.raises(ValueError, match="No document chunks"):
        embeddings.create_vector_store(
            [],
            "f0b66ea3-dbe9-42ad-aac5-2e2bf3c4202d"
        )


def test_existing_index_is_not_overwritten(isolated_store):
    document_id = "f0b66ea3-dbe9-42ad-aac5-2e2bf3c4202d"
    index_path = isolated_store / document_id
    index_path.mkdir(parents=True)

    with pytest.raises(FileExistsError):
        embeddings.create_vector_store(
            [Document(page_content="Test")],
            document_id
        )


def test_unknown_document_index_raises_error(isolated_store):
    with pytest.raises(FileNotFoundError):
        embeddings.load_vector_store(
            "f0b66ea3-dbe9-42ad-aac5-2e2bf3c4202d"
        )


def test_missing_index_file_raises_error(isolated_store):
    document_id = "f0b66ea3-dbe9-42ad-aac5-2e2bf3c4202d"
    index_path = isolated_store / document_id
    index_path.mkdir(parents=True)

    (index_path / "index.faiss").write_text("fake index")

    with pytest.raises(FileNotFoundError):
        embeddings.load_vector_store(document_id)


def test_chat_rejects_empty_question():
    with pytest.raises(ValueError, match="Question cannot be empty"):
        ask_question(
            "",
            "f0b66ea3-dbe9-42ad-aac5-2e2bf3c4202d"
        )


def test_chat_searches_only_selected_document(monkeypatch):
    selected_id = "f0b66ea3-dbe9-42ad-aac5-2e2bf3c4202d"

    fake_db = MagicMock()
    fake_db.similarity_search.return_value = [
        Document(page_content="A red Honda motorcycle was stolen.")
    ]

    loaded_ids = []

    def fake_load(document_id):
        loaded_ids.append(document_id)
        return fake_db

    monkeypatch.setattr(
        "rag.chatbot.load_vector_store",
        fake_load
    )

    answer = ask_question(
        "What vehicle was stolen?",
        selected_id
    )

    assert loaded_ids == [selected_id]
    assert "Honda motorcycle" in answer
    fake_db.similarity_search.assert_called_once()


def test_chat_does_not_load_index_for_invalid_id(monkeypatch):
    def should_not_load(document_id):
        pytest.fail("Index should not load for an invalid ID")

    monkeypatch.setattr(
        "rag.chatbot.load_vector_store",
        should_not_load
    )

    with pytest.raises(ValueError):
        ask_question("Test question", "../db_faiss")
