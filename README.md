# ⚖️ ChargeSheet AI Assistant

AI-powered legal-tech platform that analyzes police chargesheets, detects missing legal sections, and enables contextual interaction with documents using Retrieval-Augmented Generation (RAG).

The system assists investigators, legal officers, and researchers in reviewing chargesheets more efficiently.

---

# 🚀 Features

### 📄 Chargesheet Analysis

* Upload PDF chargesheets
* AI-powered legal document analysis
* Automatic investigation checklist verification
* Missing section detection
* Crime classification
* IPC section extraction
* Structured case summaries

### 🤖 RAG-Based AI Chat Assistant

* Chat with uploaded chargesheets
* Semantic document retrieval
* Context-aware legal question answering
* FAISS vector database integration
* Sentence Transformer embeddings
* Natural language interaction with legal documents

### 💡 Example Queries

* “Who is the accused?”
* “What IPC sections are mentioned?”
* “Summarize the witness statements.”
* “What evidence is available?”
* “What is the case timeline?”

---

# 🧠 How It Works 

1. User uploads a chargesheet PDF
2. Backend extracts document text
3. NLP pipeline processes legal sections
4. Document is chunked for semantic retrieval
5. Embeddings are generated using Sentence Transformers
6. FAISS vector database stores embeddings
7. User asks questions in natural language
8. Relevant legal context is retrieved and displayed

---

# 🏗 Project Architecture

```text
User Interface (Next.js)
        │
        ▼
Frontend Upload + Chat System
        │
        ▼
FastAPI Backend
        │
        ▼
PDF Processing & NLP
        │
        ▼
Sentence Transformer Embeddings
        │
        ▼
FAISS Vector Database
        │
        ▼
RAG-Based Retrieval Pipeline
        │
        ▼
AI Legal Responses
```

---

# 🛠 Tech Stack

## Frontend

* Next.js
* React
* Tailwind CSS

## Backend

* FastAPI
* Python

## AI / NLP

* LangChain
* FAISS
* Sentence Transformers
* PyMuPDF
* RAG Pipeline

---

# 📂 Project Structure

```text
chargesheet-ai-assistant
│
├── app.py
├── requirements.txt
├── rag
│   ├── loader.py
│   ├── embeddings.py
│   ├── chatbot.py
│   └── vectorstore
│
├── screenshots
│
└── chargesheet-frontend
    ├── app
    ├── public
    ├── package.json
    └── components
```

---

# ⚙️ Installation & Setup

## Clone Repository

```bash
git clone https://github.com/your-username/chargesheet-ai-assistant.git
cd chargesheet-ai-assistant
```

---

## Backend Setup

```bash
python -m venv venv
```

### Activate Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux/Mac

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Backend

```bash
python -m uvicorn app:app --reload --port 8001
```

---

## Frontend Setup

```bash
cd chargesheet-frontend
npm install
npm run dev
```

Frontend runs on:

```text
http://localhost:3000
```

Backend runs on:

```text
http://127.0.0.1:8001
```

---

## 🖥 Screenshots

### Upload & Analysis

<img width="1920" height="1020" alt="Screenshot 2026-06-16 005434" src="https://github.com/user-attachments/assets/6dc11c96-af69-4c2e-971a-857c7b28c6e5" />

<img width="1920" height="1020" alt="Screenshot 2026-06-16 011034" src="https://github.com/user-attachments/assets/640f7ea4-e309-4538-ac75-906a6e1b27e2" />



### RAG Chat Assistant

<img width="1920" height="1020" alt="Chargesheet RAG Analysis 2" src="https://github.com/user-attachments/assets/a185cf30-eefa-46c3-af69-00993de6727e" />
<img width="1920" height="1020" alt="RAG Chat Chargesheet UI 11" src="https://github.com/user-attachments/assets/1e4443b2-dd21-4c98-8ed6-ac6f5a62b2fd" />



Example:

* Upload Interface
* AI Analysis Results
* RAG Chat Assistant
* Investigation Checklist

---

# 🎯 Future Improvements

* OCR support for scanned PDFs
* Multi-document chat
* Legal timeline generation
* FIR cross-verification
* Multi-language support
* Chat history persistence
* AI-generated legal reports
* Authentication & dashboard
* Cloud vector database integration

---

# 🤝 Open for Contributions

Contributions are always welcome 🚀

You can contribute by:

* Fixing bugs
* Improving UI/UX
* Enhancing NLP accuracy
* Adding new AI capabilities
* Optimizing backend performance
* Improving documentation
* Adding OCR or multilingual support

## Contribution Steps

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Commit changes
5. Open a Pull Request

Please follow clean coding practices and proper documentation standards.

---

# ⭐ Support the Project

If you found this project useful, consider giving it a ⭐ on GitHub.

Your support motivates future development and improvements 💙

---

# 👩‍💻 Author

Kareena Kumari

---

# 📜 License


This project is licensed under the MIT License. 

You are free to use, modify, and distribute this software for educational and open-source purposes.

See the [LICENSE](LICENSE) file for more details.
