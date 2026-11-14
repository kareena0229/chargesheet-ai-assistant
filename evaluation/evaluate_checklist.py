import csv
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.metrics.pairwise import cosine_similarity

# Make the project root importable when this script is run directly.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app import model, checklist_items

EVALUATION_DIR = Path(__file__).resolve().parent
DATASET_PATH = EVALUATION_DIR / "checklist_eval.csv"
RESULTS_PATH = EVALUATION_DIR / "evaluation_results.csv"
METRICS_PATH = EVALUATION_DIR / "evaluation_metrics.json"
MATRIX_PATH = EVALUATION_DIR / "confusion_matrix.png"
REVIEW_PATH = EVALUATION_DIR / "review_candidates.csv"

LABELS = ["PRESENT", "PARTIAL", "MISSING"]

# Preserve the production thresholds from app.py.
PRESENT_THRESHOLD = 0.75
PARTIAL_THRESHOLD = 0.55


def predict_status(similarity_score):
    if similarity_score > PRESENT_THRESHOLD:
        return "PRESENT"
    elif similarity_score > PARTIAL_THRESHOLD:
        return "PARTIAL"
    return "MISSING"


def load_dataset():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    with DATASET_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    required_columns = {
        "example_id",
        "checklist_item",
        "text_excerpt",
        "expected_status",
        "label_reason",
    }

    if not rows:
        raise ValueError("The evaluation dataset is empty.")

    missing_columns = required_columns - set(rows[0].keys())
    if missing_columns:
        raise ValueError(f"Missing CSV columns: {sorted(missing_columns)}")

    for row in rows:
        row["expected_status"] = row["expected_status"].strip().upper()

        if row["expected_status"] not in LABELS:
            raise ValueError(
                f"Invalid expected status for {row['example_id']}: "
                f"{row['expected_status']}"
            )

        if row["checklist_item"] not in checklist_items:
            raise ValueError(
                f"Unknown checklist item in {row['example_id']}: "
                f"{row['checklist_item']}"
            )

        if not row["text_excerpt"].strip():
            raise ValueError(f"Empty text excerpt: {row['example_id']}")

    return rows


def evaluate(rows):
    checklist_texts = [row["checklist_item"] for row in rows]
    excerpts = [row["text_excerpt"] for row in rows]

    print(f"Encoding {len(rows)} checklist items and text excerpts...")

    item_embeddings = model.encode(
        checklist_texts,
        convert_to_numpy=True,
        show_progress_bar=True,
    )
    excerpt_embeddings = model.encode(
        excerpts,
        convert_to_numpy=True,
        show_progress_bar=True,
    )

    # Each dataset row compares its checklist item with its own excerpt.
    # This is the one-excerpt equivalent of the production best-sentence match.
    pairwise_scores = cosine_similarity(
        item_embeddings, excerpt_embeddings
    )
    similarity_scores = pairwise_scores.diagonal()

    results = []
    for row, score in zip(rows, similarity_scores):
        score = float(score)
        predicted = predict_status(score)

        results.append({
            **row,
            "predicted_status": predicted,
            "similarity_score": round(score, 4),
            "prediction_correct": predicted == row["expected_status"],
        })

    return results


def save_results(results):
    fieldnames = [
        "example_id",
        "checklist_item",
        "text_excerpt",
        "expected_status",
        "label_reason",
        "predicted_status",
        "similarity_score",
        "prediction_correct",
    ]

    with RESULTS_PATH.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def save_metrics(results):
    y_true = [row["expected_status"] for row in results]
    y_pred = [row["predicted_status"] for row in results]

    matrix = confusion_matrix(y_true, y_pred, labels=LABELS)

    report = classification_report(
        y_true,
        y_pred,
        labels=LABELS,
        output_dict=True,
        zero_division=0,
    )

    metrics = {
        "sample_count": len(results),
        "class_labels": LABELS,
        "thresholds": {
            "present": "> 0.75",
            "partial": "> 0.55 and <= 0.75",
            "missing": "<= 0.55",
        },
        "accuracy": accuracy_score(y_true, y_pred),
        "classification_report": report,
        "confusion_matrix": matrix.tolist(),
        "evaluation_scope": (
            "Synthetic dataset; results apply only to the supplied examples. "
            "The current dataset covers ten distinct checklist requirements."
        ),
    }

    with METRICS_PATH.open("w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=4)

    fig, ax = plt.subplots(figsize=(7, 6))
    image = ax.imshow(matrix, interpolation="nearest")
    fig.colorbar(image, ax=ax, label="Number of examples")

    ax.set(
        xticks=range(len(LABELS)),
        yticks=range(len(LABELS)),
        xticklabels=LABELS,
        yticklabels=LABELS,
        xlabel="Predicted status",
        ylabel="Expected status",
        title="Checklist Matching Confusion Matrix",
    )

    threshold = matrix.max() / 2 if matrix.size else 0
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(
                j, i, str(matrix[i, j]),
                ha="center",
                va="center",
                color="white" if matrix[i, j] > threshold else "black",
            )

    fig.tight_layout()
    fig.savefig(MATRIX_PATH, dpi=200)
    plt.close(fig)

    return metrics


def save_review_candidates(results):
    candidates = []

    for row in results:
        score = row["similarity_score"]
        distance_to_threshold = min(
            abs(score - PRESENT_THRESHOLD),
            abs(score - PARTIAL_THRESHOLD),
        )

        if (
            not row["prediction_correct"]
            or distance_to_threshold <= 0.05
        ):
            candidates.append({
                "example_id": row["example_id"],
                "checklist_item": row["checklist_item"],
                "text_excerpt": row["text_excerpt"],
                "expected_status": row["expected_status"],
                "predicted_status": row["predicted_status"],
                "similarity_score": row["similarity_score"],
                "prediction_correct": row["prediction_correct"],
                "label_reason": row["label_reason"],
                "review_note": (
                    "Mismatch: investigate prediction and human label."
                    if not row["prediction_correct"]
                    else "Borderline: score is within 0.05 of a threshold."
                ),
            })

    fields = [
        "example_id",
        "checklist_item",
        "text_excerpt",
        "expected_status",
        "predicted_status",
        "similarity_score",
        "prediction_correct",
        "label_reason",
        "review_note",
    ]

    with REVIEW_PATH.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(candidates)

    return candidates


def main():
    rows = load_dataset()
    results = evaluate(rows)

    save_results(results)
    metrics = save_metrics(results)
    candidates = save_review_candidates(results)

    print("\n========== EVALUATION SUMMARY ==========")
    print(f"Samples evaluated: {metrics['sample_count']}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print("\nClassification report:")

    y_true = [row["expected_status"] for row in results]
    y_pred = [row["predicted_status"] for row in results]

    print(classification_report(
        y_true,
        y_pred,
        labels=LABELS,
        zero_division=0,
    ))

    print("Confusion matrix (rows=expected, columns=predicted):")
    print(metrics["confusion_matrix"])

    print(f"\nReview candidates: {len(candidates)}")
    print("\nGenerated files:")
    print(f"- {RESULTS_PATH}")
    print(f"- {METRICS_PATH}")
    print(f"- {MATRIX_PATH}")
    print(f"- {REVIEW_PATH}")


if __name__ == "__main__":
    main()
