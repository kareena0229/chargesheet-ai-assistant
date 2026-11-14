# Checklist Matching – Evaluation and Mismatch Analysis

## 1. Evaluation Context

This evaluation uses 30 synthetic examples covering all 10 checklist requirements in the existing ChargeSheet AI Assistant.

The existing SentenceTransformer model (`all-MiniLM-L6-v2`) and production similarity thresholds were preserved. No threshold tuning or manual alteration of predictions was performed.

Thresholds:
- PRESENT: similarity > 0.75
- PARTIAL: similarity > 0.55 and <= 0.75
- MISSING: similarity <= 0.55

Each example contains a checklist requirement and a corresponding synthetic evidence excerpt. The existing similarity-based classification logic was applied to each pair.

## 2. Overall Results

- Total examples: 30
- PRESENT reference examples: 10
- PARTIAL reference examples: 10
- MISSING reference examples: 10
- Correct predictions: 13
- Incorrect predictions: 17
- Accuracy: 43.33%

### Classification Metrics

| Class | Precision | Recall | F1-score | Support |
|---|---:|---:|---:|---:|
| PRESENT | 0.00 | 0.00 | 0.00 | 10 |
| PARTIAL | 0.375 | 0.30 | 0.333 | 10 |
| MISSING | 0.455 | 1.00 | 0.625 | 10 |
| Macro average | 0.277 | 0.433 | 0.319 | 30 |
| Weighted average | 0.277 | 0.433 | 0.319 | 30 |

### Confusion Matrix

Rows represent expected labels and columns represent predicted labels.

| Expected / Predicted | PRESENT | PARTIAL | MISSING |
|---|---:|---:|---:|
| PRESENT | 0 | 5 | 5 |
| PARTIAL | 0 | 3 | 7 |
| MISSING | 0 | 0 | 10 |

The matcher did not predict PRESENT for any example. It correctly classified all 10 MISSING examples, but failed to recognize all 10 PRESENT examples.

The confusion matrix is also provided as `confusion_matrix.png`.

## 3. Mismatch Analysis

### Case 1 – False Negative (E004)

**Checklist item:** Police station name

**Text excerpt:** The complaint was registered at Kotwali Police Station, Patna.

- Expected: PRESENT
- Predicted: MISSING
- Similarity score: 0.3353

The excerpt explicitly identifies a police station. However, the similarity score is below the MISSING threshold of 0.55.

This is a false negative: relevant information is present in the excerpt, but the matcher classifies it as missing.

**Observation:** A low semantic similarity score does not necessarily mean that the required information is absent.

### Case 2 – Under-classification (E010)

**Checklist item:** Details of complainant and accused

**Text excerpt:** The complaint was filed by Rajesh Kumar against accused Mohan Singh, whose address is recorded in the case diary.

- Expected: PRESENT
- Predicted: PARTIAL
- Similarity score: 0.5607

The excerpt identifies both the complainant and accused. The score falls just above the PARTIAL threshold and below the PRESENT threshold.

The matcher therefore under-classifies this example.

**Observation:** Similarity thresholds may not adequately distinguish complete information from partially available information.

### Case 3 – Threshold-sensitive Classification (E017)

**Checklist item:** Recovery/seizure memo of property

**Text excerpt:** The motorcycle was recovered from the accused, but the case diary does not mention preparation of a seizure memo.

- Expected: PARTIAL
- Predicted: MISSING
- Similarity score: 0.5455

The excerpt documents recovery but indicates that the seizure memo is not mentioned. The human-assigned label is PARTIAL.

The score is only 0.0045 below the PARTIAL threshold of 0.55, resulting in a MISSING prediction.

**Observation:** Small score differences around a fixed threshold can change the classification.

## 4. Overall Findings

1. No reference PRESENT examples were correctly classified as PRESENT.
2. Five PRESENT examples were predicted as PARTIAL and five as MISSING.
3. Three PARTIAL examples were correctly classified; seven were predicted as MISSING.
4. All ten MISSING examples were correctly classified.
5. The matcher demonstrates a conservative classification pattern on this dataset.

The results indicate that semantic similarity alone may not adequately determine whether a checklist requirement is fully or partially documented.

## 5. Threshold Review

The original production thresholds were retained:

- PRESENT: > 0.75
- PARTIAL: > 0.55 and <= 0.75
- MISSING: <= 0.55

No threshold changes were made. The results suggest that the current thresholds may be too conservative for some paraphrased or contextually relevant excerpts.

Threshold tuning is not claimed as part of this evaluation. Any future tuning should use a separate validation set and an independent test set.

## 6. Limitations

1. The dataset contains only 30 synthetic examples.
2. Each of the 10 checklist requirements has three examples.
3. Human reference labels are based on the supplied excerpts and their stated reasons.
4. This evaluation compares each checklist item with its corresponding excerpt. Production matching searches across sentences in a complete extracted document and selects the best match. Therefore, this is a controlled single-excerpt evaluation, not a full end-to-end PDF evaluation.
5. Results may vary with wording, sentence structure, context, and model behavior.
6. The small dataset does not establish generalization to real chargesheets.
7. The dataset is not an independent legal validation dataset.

The results must not be interpreted as evidence of legal accuracy, legal completeness, correctness of allegations, or production readiness.

## 7. Reproducibility

Run from the project root with the project virtual environment activated:

```bash
python evaluation/evaluate_checklist.py


q





