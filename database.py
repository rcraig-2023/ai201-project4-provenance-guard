import sqlite3

DATABASE = "content.db"

def get_connection():
    return sqlite3.connect(DATABASE)

def initialize_database():
    conn = get_connection()
    # Drop table to apply the new schema cleanly
    conn.execute("DROP TABLE IF EXISTS submissions")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS submissions (
            content_id TEXT PRIMARY KEY,
            creator_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            attribution TEXT NOT NULL,
            llm_score REAL NOT NULL,
            heuristic_score REAL NOT NULL,
            text TEXT NOT NULL,
            confidence REAL NOT NULL,
            status TEXT NOT NULL,
            appeal_reasoning TEXT
        )
        """
    )
    conn.commit()
    conn.close()

def insert_submission(
    content_id: str,
    creator_id: str,
    timestamp: str,
    attribution: str,
    llm_score: float,
    heuristic_score: float,
    text: str,
    confidence: float,
    status: str
):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO submissions
        (content_id, creator_id, timestamp, attribution, llm_score, heuristic_score, text, confidence, status, appeal_reasoning)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
        """,
        (content_id, creator_id, timestamp, attribution, llm_score, heuristic_score, text, confidence, status),
    )
    conn.commit()
    conn.close()

def get_all_submissions():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * FROM submissions")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_submission_status(content_id: str, status: str, reasoning: str = None):
    conn = get_connection()
    if reasoning:
        conn.execute(
            "UPDATE submissions SET status = ?, appeal_reasoning = ? WHERE content_id = ?",
            (status, reasoning, content_id),
        )
    else:
        conn.execute(
            "UPDATE submissions SET status = ? WHERE content_id = ?",
            (status, content_id),
        )
    conn.commit()
    conn.close()