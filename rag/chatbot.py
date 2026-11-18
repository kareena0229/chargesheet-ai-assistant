
from rag.embeddings import (
    load_vector_store,
    validate_document_id,
)


def ask_question(question: str, document_id: str) -> str:
    """
    Retrieve information exclusively from the selected
    document's isolated FAISS vector index.
    """

    # Step 1: Validate the question.
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    # Step 2: Validate and normalize document ID BEFORE
    # attempting to load any vector index.
    safe_document_id = validate_document_id(document_id)

    # Step 3: Load only the selected document's index.
    db = load_vector_store(safe_document_id)

    # Step 4: Search only inside the selected document.
    docs = db.similarity_search(
        question.strip(),
        k=3
    )

    # Step 5: Handle empty retrieval results.
    if not docs:
        return "No relevant information found in this document."

    # Step 6: Prepare the retrieved context.
    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    return (
        "Relevant information found from the selected chargesheet:\n\n"
        + context[:3000]
    )
