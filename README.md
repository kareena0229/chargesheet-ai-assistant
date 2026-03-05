# ⚖️ AI Chargesheet Analyzer

AI Chargesheet Analyzer is an intelligent system that analyzes legal charge sheets and identifies missing information, inconsistencies, and important legal checkpoints.

The system uses Natural Language Processing (NLP) and semantic similarity models to assist investigators, legal professionals, and students in reviewing case documents efficiently.

---

# 🚀 Features

• Upload and analyze a chargesheet document
• AI-based document understanding
• Automatic checklist generation
• Detect missing legal elements
• Highlight important sections
• Fast and user-friendly interface

---

# 🧠 Technology Stack

Frontend

* Next.js
* React
* Tailwind CSS

Backend

* FastAPI
* Python

AI / NLP

* Sentence Transformers
* HuggingFace Models

---

# 🏗 System Architecture

User → Frontend (Next.js) → FastAPI Backend → AI Model → Analysis Results

Steps:

1. User uploads a chargesheet
2. Frontend sends file to FastAPI server
3. Backend extracts text from PDF
4. NLP model analyzes legal sections
5. AI generates checklist and insights
6. Results displayed in UI

---

# 📷 Screenshots

Add screenshots of:

• Upload Interface
• Analysis Results
• Checklist Output

Example:

![Upload Screen](screenshots/upload.png)

![Analysis Result](screenshots/result.png)

---

# ⚙️ Installation Guide

Clone repository

git clone https://github.com/kareena0229/chargesheet-ai-assistant.git

Go to project folder

cd chargesheet-ai-assistant

---

## Backend Setup

Create virtual environment

python -m venv .venv

Activate environment

.venv\Scripts\activate

Install dependencies

pip install -r requirements.txt

Run backend

uvicorn app:app --reload

---

## Frontend Setup

Open frontend folder

cd chargesheet-frontend

Install packages

npm install

Run frontend

npm run dev

Open browser

http://localhost:3000

---

# 🎯 Future Improvements

• Case law recommendation system
• Evidence validation using AI
• Multi-language legal support
• Court document summarization

---

# 👩‍💻 Author

Kareena Kumari

AI / Software Engineering Project
