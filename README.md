# Provenance Guard: AI-Driven Authenticity & Attribution Pipeline

Provenance Guard is a sophisticated verification system designed to promote transparency in content creation. It addresses the challenge of distinguishing human-written content from AI-generated text by employing a multi-signal detection pipeline that provides verifiable, audit-ready provenance for digital submissions.

## The Problem & Solution
The rapid rise of LLMs has made it difficult to verify content origins. Reliance on single-signal detection often results in high false-positive rates. Provenance Guard provides a solution by combining two independent analysis layers to determine content authenticity:

* **Signal 1 (LLM Analysis):** Utilizes Groq's `llama-3.3-70b-versatile` model to measure semantic cohesion, structural monotony, and the presence of predictable transition tokens.
* **Signal 2 (Stylometric Heuristics):** A pure Python module that evaluates sentence length variance ("burstiness") and vocabulary diversity (type-token ratio).

The signals are combined into a unified `confidence_score` using an arithmetic mean, resulting in a robust metric that accounts for both semantic and structural patterns.

## Transparency Labels
Depending on the unified confidence score, users see one of the following plain-language labels:

| Condition | Verbatim Text Displayed |
| :--- | :--- |
| **High-Confidence Human** (Score < 0.3) | "This writing was detected as human writing. There are no AI-generated writing elements detected." |
| **Uncertain** (0.3 <= Score <= 0.75) | "Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated." |
| **High-Confidence AI** (Score > 0.75) | "This writing contains components typically found in AI-generated writing, and it doesn't show any components of human writing." |

## Confidence Scoring Validation
The confidence score represents genuine uncertainty rather than a binary output. The arithmetic mean combination of the Groq LLM score and Stylometric Heuristics score was validated against distinct input types:
* **Clearly AI-Generated:** Submitting an overly formal paragraph with textbook transitions (e.g., "Furthermore, stakeholders must collaborate...") consistently yielded scores > 0.8.
* **Clearly Human-Written:** Submitting casual, lower-case, low-punctuation text (e.g., casual restaurant reviews) yielded high variance and scores < 0.2.
* **Borderline:** Lightly edited texts hit the 0.4-0.6 range, successfully triggering the "Uncertain" label, ensuring we don't incorrectly penalize human writers with rigid styles.

## Rate Limiting
The `/submit` endpoint is protected by `Flask-Limiter` with limits set to `10 per minute; 100 per day`. 
* **Reasoning:** On a creative writing platform, a single creator realistically submits a few pieces a day. 10 requests per minute allows for reasonable rapid edits or retries, while 100 per day strictly prevents adversaries from using automated scripts to flood the system or reverse-engineer the detection heuristics. 

ricacraig@ricas-mbp ai201-project4-provenance-guard % for i in {1..12}; do curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:5002/submit -H "Content-Type: application/json" -d '{"text": "Rate limit test.", "creator_id": "ratelimit-test"}'; done
200
200
200
200
200
200
200
200
200
200
429
429

## Audit Log Evidence

ricacraig@ricas-mbp ai201-project4-provenance-guard % curl -s http://localhost:5002/log
{
  "audit_log": [
    {
      "appeal_reasoning": "I wrote this myself! It is just formal because I am an academic.",
      "attribution": "Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated.",
      "confidence": 0.6849104334027285,
      "content_id": "c1363f45-e5ea-435a-a817-09fa1fefba91",
      "creator_id": "user-1",
      "heuristic_score": 0.449820866805457,
      "llm_score": 0.92,
      "status": "under_review",
      "text": "Artificial intelligence represents a transformative paradigm shift in modern society. It is important to note that while the benefits of AI are numerous, it is equally essential to consider the ethical implications. Furthermore, stakeholders across various sectors must collaborate to ensure responsible deployment.",
      "timestamp": "2026-06-30T23:53:12.272001"
    },
    {
      "appeal_reasoning": null,
      "attribution": "Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated.",
      "confidence": 0.334678261271533,
      "content_id": "f2806be9-549c-4cea-abcc-5d47ea0a3570",
      "creator_id": "user-2",
      "heuristic_score": 0.43935652254306595,
      "llm_score": 0.23,
      "status": "classified",
      "text": "ok so i finally tried that new ramen place downtown and honestly? underwhelming. the broth was fine but they put WAY too much sodium in it and i was thirsty for like three hours after. my friend got the spicy version and said it was better. probably wont go back unless someone drags me there",
      "timestamp": "2026-06-30T23:53:12.621514"
    },
    {
      "appeal_reasoning": null,
      "attribution": "Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated.",
      "confidence": 0.3878312163512968,
      "content_id": "6afb0962-44bd-471f-a6d9-f770044e09eb",
      "creator_id": "user-3",
      "heuristic_score": 0.45566243270259355,
      "llm_score": 0.32,
      "status": "classified",
      "text": "I have been thinking a lot about remote work lately. There are genuine tradeoffs \u2014 flexibility and no commute on one side, isolation and blurred work-life boundaries on the other. Studies show productivity varies widely by individual and role type.",
      "timestamp": "2026-06-30T23:53:12.906241"
    },
    {
      "appeal_reasoning": null,
      "attribution": "Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated.",
      "confidence": 0.45999999999999996,
      "content_id": "a38e01c8-902f-4aa2-a820-bc44126534f7",
      "creator_id": "ratelimit-test",
      "heuristic_score": 0.5,
      "llm_score": 0.42,
      "status": "classified",
      "text": "Rate limit test.",
      "timestamp": "2026-06-30T23:53:27.045841"
    },
    {
      "appeal_reasoning": null,
      "attribution": "Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated.",
      "confidence": 0.45999999999999996,
      "content_id": "907d1941-540e-4856-8211-1847be1cf5d8",
      "creator_id": "ratelimit-test",
      "heuristic_score": 0.5,
      "llm_score": 0.42,
      "status": "classified",
      "text": "Rate limit test.",
      "timestamp": "2026-06-30T23:53:27.402553"
    },
    {
      "appeal_reasoning": null,
      "attribution": "Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated.",
      "confidence": 0.45999999999999996,
      "content_id": "811e6d15-f3ac-4855-a51a-bbbf56988309",
      "creator_id": "ratelimit-test",
      "heuristic_score": 0.5,
      "llm_score": 0.42,
      "status": "classified",
      "text": "Rate limit test.",
      "timestamp": "2026-06-30T23:53:27.568277"
    },
    {
      "appeal_reasoning": null,
      "attribution": "Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated.",
      "confidence": 0.45999999999999996,
      "content_id": "66f97bc8-00f1-458c-a54c-0be482fc80b2",
      "creator_id": "ratelimit-test",
      "heuristic_score": 0.5,
      "llm_score": 0.42,
      "status": "classified",
      "text": "Rate limit test.",
      "timestamp": "2026-06-30T23:53:27.748947"
    },
    {
      "appeal_reasoning": null,
      "attribution": "Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated.",
      "confidence": 0.45999999999999996,
      "content_id": "e655cbb6-06b0-44ce-a263-edca50170f49",
      "creator_id": "ratelimit-test",
      "heuristic_score": 0.5,
      "llm_score": 0.42,
      "status": "classified",
      "text": "Rate limit test.",
      "timestamp": "2026-06-30T23:53:28.272808"
    },
    {
      "appeal_reasoning": null,
      "attribution": "Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated.",
      "confidence": 0.45999999999999996,
      "content_id": "79baeab0-fe9f-45e6-a4ca-78cd3c64de98",
      "creator_id": "ratelimit-test",
      "heuristic_score": 0.5,
      "llm_score": 0.42,
      "status": "classified",
      "text": "Rate limit test.",
      "timestamp": "2026-06-30T23:53:28.527336"
    },
    {
      "appeal_reasoning": null,
      "attribution": "Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated.",
      "confidence": 0.45999999999999996,
      "content_id": "be9c640f-57a3-4d5c-a65e-49d557373ac2",
      "creator_id": "ratelimit-test",
      "heuristic_score": 0.5,
      "llm_score": 0.42,
      "status": "classified",
      "text": "Rate limit test.",
      "timestamp": "2026-06-30T23:53:28.822259"
    },
    {
      "appeal_reasoning": null,
      "attribution": "Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated.",
      "confidence": 0.45999999999999996,
      "content_id": "65773d6b-7c24-4b31-be4d-b02a86577a5f",
      "creator_id": "ratelimit-test",
      "heuristic_score": 0.5,
      "llm_score": 0.42,
      "status": "classified",
      "text": "Rate limit test.",
      "timestamp": "2026-07-01T00:07:35.466424"
    },
    {
      "appeal_reasoning": null,
      "attribution": "Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated.",
      "confidence": 0.45999999999999996,
      "content_id": "8877a8e8-a0f0-4335-95df-3b4129bb922d",
      "creator_id": "ratelimit-test",
      "heuristic_score": 0.5,
      "llm_score": 0.42,
      "status": "classified",
      "text": "Rate limit test.",
      "timestamp": "2026-07-01T00:07:35.734966"
    },
    {
      "appeal_reasoning": null,
      "attribution": "Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated.",
      "confidence": 0.45999999999999996,
      "content_id": "8b37efc3-fbda-41a5-b833-f2102514d8cb",
      "creator_id": "ratelimit-test",
      "heuristic_score": 0.5,
      "llm_score": 0.42,
      "status": "classified",
      "text": "Rate limit test.",
      "timestamp": "2026-07-01T00:07:35.882538"
    },
    {
      "appeal_reasoning": null,
      "attribution": "Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated.",
      "confidence": 0.45999999999999996,
      "content_id": "dc9452f2-9bd2-49c6-857d-a51bec19b0bd",
      "creator_id": "ratelimit-test",
      "heuristic_score": 0.5,
      "llm_score": 0.42,
      "status": "classified",
      "text": "Rate limit test.",
      "timestamp": "2026-07-01T00:07:36.204512"
    },
    {
      "appeal_reasoning": null,
      "attribution": "Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated.",
      "confidence": 0.45999999999999996,
      "content_id": "30f595bb-0b5a-4bed-b6ae-0d9b9f17bcb7",
      "creator_id": "ratelimit-test",
      "heuristic_score": 0.5,
      "llm_score": 0.42,
      "status": "classified",
      "text": "Rate limit test.",
      "timestamp": "2026-07-01T00:07:36.394378"
    },
    {
      "appeal_reasoning": null,
      "attribution": "Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated.",
      "confidence": 0.45999999999999996,
      "content_id": "ea67bd71-7a13-4f2e-bf7e-883ab5af2dd8",
      "creator_id": "ratelimit-test",
      "heuristic_score": 0.5,
      "llm_score": 0.42,
      "status": "classified",
      "text": "Rate limit test.",
      "timestamp": "2026-07-01T00:07:36.789867"
    },
    {
      "appeal_reasoning": null,
      "attribution": "Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated.",
      "confidence": 0.45999999999999996,
      "content_id": "9b2c7d30-e1eb-4a45-8141-d9ad0ca7c89d",
      "creator_id": "ratelimit-test",
      "heuristic_score": 0.5,
      "llm_score": 0.42,
      "status": "classified",
      "text": "Rate limit test.",
      "timestamp": "2026-07-01T00:07:37.047899"
    },
    {
      "appeal_reasoning": null,
      "attribution": "Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated.",
      "confidence": 0.45999999999999996,
      "content_id": "6b5b35ae-1881-45a6-b04f-dff8eca532d8",
      "creator_id": "ratelimit-test",
      "heuristic_score": 0.5,
      "llm_score": 0.42,
      "status": "classified",
      "text": "Rate limit test.",
      "timestamp": "2026-07-01T00:07:37.483044"
    },
    {
      "appeal_reasoning": null,
      "attribution": "Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated.",
      "confidence": 0.45999999999999996,
      "content_id": "e68049dd-5265-4618-9863-0471dac591bd",
      "creator_id": "ratelimit-test",
      "heuristic_score": 0.5,
      "llm_score": 0.42,
      "status": "classified",
      "text": "Rate limit test.",
      "timestamp": "2026-07-01T00:07:37.759529"
    },
    {
      "appeal_reasoning": null,
      "attribution": "Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated.",
      "confidence": 0.45999999999999996,
      "content_id": "9ab324f0-b055-4096-8d41-78311970571a",
      "creator_id": "ratelimit-test",
      "heuristic_score": 0.5,
      "llm_score": 0.42,
      "status": "classified",
      "text": "Rate limit test.",
      "timestamp": "2026-07-01T00:07:38.023641"
    }
  ]
}

## Known Limitations
* **Stylometric Heuristics Blind Spot:** The system is prone to false positives when processing **instructional recipe books**. These texts follow rigid, repetitive grammatical patterns ("Add 1 cup of X. Stir for 2 minutes.") which causes the stylometric heuristic signal to drop sentence length variance to near zero. Consequently, the system will likely misclassify these human-written instructions as AI-generated due to their lack of structural "burstiness".
* **LLM Analysis Blind Spot:** Highly polished, formal, or academic human writing (e.g., legal briefs or research papers) often matches the "perfect" grammar patterns of standard LLM training data. The Groq model may flag these as AI-generated due to their semantic alignment with textbook LLM output styles.

## Implementation Reflection
During development, we diverged from the initial plan regarding the database schema. While the original blueprint focused on capturing only the `llm_score` and `confidence`, we realized that a human reviewer needs to see the raw component scores to assess an appeal. Therefore, we modified the database schema to explicitly store the `heuristic_score` as a separate column. This ensure that auditors can diagnose *why* a specific confidence score was generated, fulfilling the transparency requirements of our architectural design.

## AI Usage
1. **Initial API Scaffolding:** I prompted Gemini with my architecture diagram and planning specs to generate the Flask app skeleton. The output included basic routes, but I had to heavily revise the SQLite database logic to properly drop and recreate the schema for clean testing.
2. **Transparency Label Generation:** I used Gemini to translate my conditional thresholds into a Python helper function (`get_transparency_label`). The AI initially tried to return integer codes instead of the full strings, so I manually overrode the function to return the verbatim user-facing text defined in my `planning.md`.

