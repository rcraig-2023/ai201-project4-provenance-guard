# Project Planning: Provenance Guard

This document serves as the system architecture blueprint and AI assistance roadmap for Provenance Guard.

---

## 1. Detection Signals

Provenance Guard utilizes a multi-signal detection pipeline consisting of two independent analysis layers to determine content authenticity.

### Signal 1: LLM-Based Semantic Analysis (Groq API)
*   **What it measures:** Semantic cohesion, structural monotony, presence of predictable transition tokens (e.g., *furthermore*, *moreover*, *it is important to note*), and narrative pacing.
*   **Why it differs:** Standard LLMs optimize for helpfulness and risk-aversion, leading to a neutral tone, uniform sentence structures, and textbook transitions. Humans write with varied flow, emotional variance, and idiom usage.
*   **Blind Spots:** Highly polished, formal, or academic human writing (e.g., essay or legal briefs) matches the "perfect" grammar patterns of LLM training data, risking false positives.
*   **Output Format:** A float between `0.0` (confident human) and `1.0` (confident AI).

### Signal 2: Stylometric Heuristics (Pure Python)
*   **What it measures:** Sentence length variance (burstiness), type-token ratio (vocabulary diversity), and punctuation density.
*   **Why it differs:** Human writing is driven by intent and emotion, leading to high structural variation—short punchy sentences mixed with long clauses. AI text generation naturally converges on statistical averages, producing highly uniform structure.
*   **Blind Spots:** Bad actors can bypass these metrics using deliberate prompting strategies (e.g., "Write this with highly varied sentence lengths"). Conversely, highly regulated human writing structures naturally suppress structural variance.
*   **Output Format:** A float between `0.0` (high variance/human) and `1.0` (low variance/AI).

### Combining Signals
The two independent outputs are combined into a single unified `confidence_score` using a simple arithmetic mean:

$$\text{confidence\\_score} = \frac{\text{llm\\_score} + \text{heuristic\\_score}}{2}$$

---

## 2. Uncertainty Representation

To minimize damaging false positives on creative platforms, the scoring scale does not use a binary midpoint split at `0.5`. Instead, it expands the "Uncertain" category to serve as a safety buffer for human writers with formal or uniform styles.

*   **Score Range:** `0.0` represents absolute confidence in human origin; `1.0` represents absolute confidence in AI origin.
*   **Threshold Calibration:**
    *   **Score < 0.3:** Mapped to **Likely Human**.
    *   **0.3 <= Score <= 0.75:** Mapped to **Uncertain**.
    *   **Score > 0.75:** Mapped to **Likely AI**.

A score of `0.6` represents a borderline case where the signals indicate a mix of human-like creativity and AI-like structural uniformity. The system explicitly flags this as "Uncertain" rather than issuing a definitive attribution.

---

## 3. Transparency Label Design

The system maps the calibrated confidence score to one of three user-facing string messages displayed to readers on the platform.

| Variant | Condition | Verbatim Text Displayed |
| :--- | :--- | :--- |
| **High-Confidence Human** | Score < 0.3 | `"This writing was detected as human writing. There are no AI-generated writing elements detected."` |
| **Uncertain** | 0.3 <= Score <= 0.75 | `"Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated."` |
| **High-Confidence AI** | Score > 0.75 | `"This writing contains components typically found in AI-generated writing, and it doesn't show any components of human writing."` |

---

## 4. Appeals Workflow

When a creator believes their original work has been misclassified, they can file an appeal to ensure human review.

*   **Who can submit:** The original content author, verified by matching their `creator_id` to the submission record.
*   **Information provided:** The unique `content_id` and a text field containing the `creator_reasoning`.
*   **System Actions on Receipt:**
    1.  Validates that the `content_id` exists.
    2.  Updates the record state from `"classified"` to `"under_review"` in the database.
    3.  Appends the `creator_reasoning` and submission timestamp to the structured audit log.
    4.  Returns an acknowledgment JSON payload: `{"status": "appeal_received"}`.
*   **Human Reviewer Queue View:** A human reviewer opening the moderation dashboard will see a table containing:
    *   `content_id` & `creator_id`
    *   The original submitted text
    *   The raw component scores (`llm_score`, `heuristic_score`) and combined `confidence_score`
    *   The original transparency label applied
    *   The creator's written text explaining their reasoning

---

## 5. Anticipated Edge Cases

### Case 1: Formal/Academic Prose or Legal Documents
*   **Impact:** False Positive (Mislabeled as AI)
*   **Mechanism:** Academic papers and professional articles enforce rigid structural styling, formal vocabulary choices, and textbook transitions. The Groq signal may flag these as AI-generated due to semantic alignment with standard LLM output styles.

### Case 2: Recipe Books and Instructional Frameworks
*   **Impact:** False Positive (Mislabeled as AI)
*   **Mechanism:** Recipe instructions follow highly repetitive grammatical patterns ("Add 1 cup of X. Stir for 2 minutes. Bake at Y temperature."). This drops the sentence length variance (burstiness) to near zero, causing the stylometric heuristics component to return a high AI score.

---

## 6. Architecture

### Narrative Overview
When a client submits text via `POST /submit`, the application checks the request against a `Flask-Limiter` front door to prevent abuse. If allowed, the payload passes to the Multi-Signal Detection Pipeline, where it is analyzed in parallel by the Groq LLM API and a Python stylometric heuristics module. The individual scores are combined by the confidence scoring logic, mapped to a string-based transparency label, written as a permanent structured record into the SQLite audit log, and returned as a JSON response. The appeal flow exposes a `POST /appeal` endpoint that seamlessly flags existing audit records as `"under_review"` without re-running automated classification.

### System Diagram
```text
### 1. Submission Flow
+-------------+  {"text", "creator_id"}  +-------------------+       +-----------------------+
|   Writer    | -----------------------> | Flask API         | ----> | Signal 1: Groq LLM    |
|  (Client)   |                          | (POST /submit)    | ----> | Signal 2: Stylometric |
+-------------+                          +-------------------+       +-----------------------+
                                                 |                               |
                                                 |                      llm_score (0-1)
                                                 |                    heuristic_score (0-1)
                                                 |                               |
                                                 |                               v
                                                 |                   +-----------------------+
                                                 |                   | Confidence Scoring    |
                                                 |                   +-----------------------+
                                                 |                               |
                                                 |                     confidence_score (0-1)
                                                 |                               |
                                                 |                               v
+-------------+                                  |                   +-----------------------+
| Audit Log   | <--------------------------------+------------------ | Transparency Label    |
| (SQLite)    |       Writes complete record     |                   | Generator             |
+-------------+       (scores, label, IDs)       +-------------------+-----------------------+
                                                 |                               
+-------------+                                  |
|   Writer    | <--------------------------------+ 
|  (Client)   |  {"content_id", "confidence", "label"}
+-------------+


### 2. Appeal Flow
+-------------+  {"content_id", "reason"} +-------------------+      +-----------------------+
|   Writer    | ------------------------> | Flask API         | ---> | Audit Log (SQLite)    |
|  (Client)   |                           | (POST /appeal)    |      | (Updates status to    |
+-------------+                           +-------------------+      |  "under review" and   |
       ^                                            |                |   logs reasoning)     |
       |       {"status": "appeal_received"}        |                +-----------------------+
       +--------------------------------------------+

## 7. AI Tool Plan

### Milestone 3: Submission Endpoint & Groq Signal
*   **Context Provided:** Section 1 (Signal 1 properties), Section 6 (Architecture Narrative and Diagram).
*   **AI Generation Prompt:** Generate a complete boilerplate Flask application including a structured `POST /submit` route receiving `text` and `creator_id`. Implement a standalone Python function utilizing the `groq` SDK to prompt `llama-3.3-70b-versatile` to evaluate the text and return a confidence score between 0.0 and 1.0. Include a basic helper using Python's built-in `sqlite3` module to initialize a database table and log the entry with a unique UUID string (`content_id`).
*   **Verification Process:** Run the application locally and use a `curl` script to verify that a text submission returns a valid JSON response containing a unique `content_id` and that the row successfully populates the SQLite database.

### Milestone 4: Stylometric Heuristics & Unified Scoring
*   **Context Provided:** Section 1 (Signal 2 calculations and formula), Section 2 (Calibration ranges), Section 6 (Diagram).
*   **AI Generation Prompt:** Create a pure Python module that evaluates a text block and returns a normalized score between 0.0 and 1.0 based on sentence length variance and token distribution ratios. Write the unified scoring function that averages this heuristic score with the Groq score, and integrate it into the existing `POST /submit` code so that both metrics populate the SQLite database schema.
*   **Verification Process:** Pass 4 hardcoded string payloads into the pipeline (1 clear AI sample, 1 informal human text, 1 formal academic essay, 1 repetitive instructional block) to confirm that the combined scores shift predictably across the ranges.

### Milestone 5: Production Layer Completion
*   **Context Provided:** Section 3 (Transparency Label strings), Section 4 (Appeals parameters), Section 6 (Diagram).
*   **AI Generation Prompt:** Implement a function that processes the final score into the exact string labels specified in the design table. Add a `POST /appeal` endpoint that takes a `content_id` and `creator_reasoning`, updates the matching database row's status column to `"under_review"`, and records the reasoning. Configure `Flask-Limiter` with an in-memory storage URI to protect `/submit` from rapid floods. Add a simple `GET /log` endpoint that lists the database contents for audit inspection.
*   **Verification Process:** Verify label rendering by confirming all three string outputs change dynamically based on input properties. Run a localized bash loop firing 12 requests in under a second to confirm that the API successfully returns a `429 Too Many Requests` status block after the 10th request.

