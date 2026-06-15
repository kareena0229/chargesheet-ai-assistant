from rag.embeddings import load_vector_store


def ask_question(question):

    try:

        db = load_vector_store()

        docs = db.similarity_search(question, k=3)

        if not docs:
            return "No relevant information found."

        context = "\n\n".join(
            [doc.page_content for doc in docs]
        )

        return f"""
Relevant information found from the chargesheet:

{context[:3000]}
"""

    except Exception as e:

        return f"CHATBOT ERROR: {str(e)}"