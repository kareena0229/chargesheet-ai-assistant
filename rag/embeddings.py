
from pathlib import Path
from uuid import UUID

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


# Each document gets its own directory inside this folder.
VECTORSTORE_ROOT = Path(__file__).resolve().parent / "vectorstore"

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def validate_document_id(document_id: str) -> str:
    """Validate and normalize a UUID document identifier."""
    try:
        return str(UUID(document_id))
    except (ValueError, TypeError, AttributeError):
        raise ValueError("Invalid document ID.")


def get_document_index_path(document_id: str) -> Path:
    """Get the isolated FAISS directory for a document."""
    safe_id = validate_document_id(document_id)
    return VECTORSTORE_ROOT / safe_id


def create_vector_store(chunks, document_id: str) -> None:
    """Create and save a separate FAISS index for one document."""

    if not chunks:
        raise ValueError("No document chunks available.")

    index_path = get_document_index_path(document_id)

    # Do not overwrite an existing document index.
    if index_path.exists():
        raise FileExistsError("Document index already exists.")

    index_path.mkdir(parents=True, exist_ok=False)

    try:
        db = FAISS.from_documents(chunks, embedding_model)
        db.save_local(str(index_path))

    except Exception:
        # Remove an incomplete index if indexing fails.
        import shutil
        shutil.rmtree(index_path, ignore_errors=True)
        raise


def load_vector_store(document_id: str):
    """Load only the index belonging to the requested document."""

    index_path = get_document_index_path(document_id)

    required_files = [
        index_path / "index.faiss",
        index_path / "index.pkl"
    ]

    if not all(path.is_file() for path in required_files):
        raise FileNotFoundError("Document index not found.")

    return FAISS.load_local(
        str(index_path),
        embedding_model,
        allow_dangerous_deserialization=True
    )
