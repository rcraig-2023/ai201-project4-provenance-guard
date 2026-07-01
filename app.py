import uuid
from database import initialize_database, insert_submission, get_all_submissions, update_submission_status
from flask import Flask, jsonify, request
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from ai import evaluate_text_confidence
from heuristics import calculate_heuristic_score

app = Flask(__name__)

# Initialize Rate Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://"
)

initialize_database()

@app.route("/log", methods=["GET"])
def view_log():
    records = get_all_submissions()
    return jsonify({"audit_log": records})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

def get_transparency_label(score: float) -> str:
    if score < 0.3:
        return "This writing was detected as human writing. There are no AI-generated writing elements detected."
    elif 0.3 <= score <= 0.75:
        return "Due to this writing containing elements unique to human and AI writing, we were not able to confidently determine whether this writing is human or AI-generated."
    else:
        return "This writing contains components typically found in AI-generated writing, and it doesn't show any components of human writing."

@app.route("/submit", methods=["POST"])
@limiter.limit("10 per minute;100 per day")
def submit():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "JSON body required"}), 400
    
    text = data.get("text")
    creator_id = data.get("creator_id")
    
    if not text or not creator_id:
        return jsonify({"error": "Missing 'text' or 'creator_id'"}), 400

    # 1. Get both signals
    llm_score = evaluate_text_confidence(text)
    heuristic_score = calculate_heuristic_score(text)
    confidence = (llm_score + heuristic_score) / 2
    
    # 2. Calculate combined confidence score
    attribution = get_transparency_label(confidence)

    # 3. Prepare data
    content_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    status = "classified"

    # 4. Store in database
    insert_submission(
        content_id=content_id,
        creator_id=creator_id,
        timestamp=timestamp,
        attribution=attribution,
        llm_score=llm_score,
        heuristic_score=heuristic_score,
        text=text,
        confidence=confidence,
        status=status
    )
    
    return jsonify({
        "content_id": content_id, 
        "creator_id": creator_id,
        "confidence": confidence,
        "label": attribution
    })

@app.route("/appeal", methods=["POST"])
def appeal():
    data = request.get_json(silent=True)
    if not data or "content_id" not in data:
        return jsonify({"error": "content_id is required"}), 400
    
    content_id = data.get("content_id")
    reasoning = data.get("creator_reasoning", "No reason provided")
    
    # Update the submission status to "under_review" and log reasoning
    update_submission_status(content_id, "under_review", reasoning)
    
    return jsonify({
        "status": "appeal_received", 
        "content_id": content_id,
        "new_status": "under_review"
    })

if __name__ == "__main__":
    app.run(port=5002, debug=True)

