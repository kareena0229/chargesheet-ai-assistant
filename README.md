# chargesheet-ai-assistant

An AI-powered system that analyzes Hindi police chargesheets and extracts structured legal insights.

The system automatically:
- Generates a structured case summary
- Classifies the crime type
- Detects missing procedural documents
- Extracts legal entities (NER)
- Uses semantic similarity to detect evidence references

This helps police officers and prosecutors quickly review large chargesheets and identify missing legal documents.

---

# Problem

Police chargesheets in India are often:

- 30–50 pages long
- Written in Hindi
- Contain OCR noise
- Hard to review quickly
- Missing critical procedural documents

Manual review wastes time and can weaken cases during trial.

---

# Solution

Chargesheet AI Assistant processes raw Hindi chargesheet text and produces:

### 1️⃣ Structured Case Summary
Extracts:

- FIR number
- FIR date
- Police station
- Accused names
- Victim names
- Incident description
- Legal sections (IPC / NDPS / IT Act)

Example output:

```json
{
 "fir_number": "123/2024",
 "police_station": "Civil Lines",
 "accused": ["Ram Kumar"],
 "victim": ["Shyam Lal"],
 "sections": ["IPC 379"]
}
