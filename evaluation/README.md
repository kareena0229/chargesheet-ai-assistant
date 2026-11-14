# Ticket 03 – Checklist Matching Evaluation

## Project
ChargeSheet AI Assistant

## Objective
Evaluate the existing similarity-based checklist matcher using a human-reviewed synthetic dataset. The matcher classifies checklist evidence as PRESENT, PARTIAL, or MISSING.

## Dataset
File: checklist_eval.csv

- 30 synthetic examples.
- 10 checklist requirements.
- 10 PRESENT, 10 PARTIAL, and 10 MISSING reference labels.
- Each example includes an ID, checklist item, evidence excerpt, expected status, and label reason.

## Existing Matching Logic

Model: all-MiniLM-L6-v2

Original production thresholds were preserved:

| Status | Similarity threshold |
|---|---|
| PRESENT | > 0.75 |
| PARTIAL | > 0.55 and <= 0.75 |
| MISSING | <= 0.55 |

No threshold tuning or manual modification of predictions was performed.

## How to Run

Activate the virtual environment:

    .\venv\Scripts\Activate.ps1

Install dependencies:

    pip install -r requirements.txt

Run the evaluation from the project root:

    python evaluation\evaluate_checklist.py

The script imports the existing model and checklist definitions from app.py. The sentence-transformer model must be available locally or downloadable from Hugging Face.

## Evaluation Results

- Total examples: 30
- Correct predictions: 13
- Accuracy: 43.33%
- Review candidates: 19

### Confusion Matrix

Rows represent expected labels; columns represent predicted labels.

| Expected / Predicted | PRESENT | PARTIAL | MISSING |
|---|---:|---:|---:|
| PRESENT | 0 | 5 | 5 |
| PARTIAL | 0 | 3 | 7 |
| MISSING | 0 | 0 | 10 |

The matcher did not predict PRESENT for any example. It correctly classified all 10 MISSING examples but struggled to identify PRESENT and PARTIAL evidence.

See evaluation_metrics.json for detailed precision, recall, and F1 scores.

## Mismatch Analysis

See mismatch_analysis.md for three analyzed examples:

- E004: Police station information classified as MISSING.
- E010: Complainant and accused information classified as PARTIAL instead of PRESENT.
- E017: Partial recovery information classified as MISSING near the 0.55 threshold.

## Output Files

| File | Purpose |
|---|---|
| checklist_eval.csv | Human-labeled synthetic dataset |
| evaluate_checklist.py | Evaluation script |
| evaluation_results.csv | Predictions and similarity scores |
| evaluation_metrics.json | Classification metrics and confusion matrix |
| confusion_matrix.png | Visual confusion matrix |
| review_candidates.csv | Mismatches and borderline examples |
| mismatch_analysis.md | Detailed mismatch analysis |

The baseline_18 directory preserves the earlier 18-example evaluation artifacts.

## Limitations and Responsible Use

- The dataset contains only 30 synthetic examples.
- Each checklist requirement has three examples.
- Evaluation compares each checklist item with its paired excerpt. Production matching searches across sentences in a complete extracted document, so this is not a full end-to-end PDF evaluation.
- Results may vary with wording, context, and model behavior.
- The dataset is not an independent legal validation dataset.
- No threshold tuning was performed.
- These results do not establish legal accuracy, legal completeness, or production readiness.

Only synthetic or properly anonymized excerpts should be used.
