"""
SQLite store for roles and candidates
Replaces in-memory store.py
"""
import uuid
import json
from datetime import datetime
from database import get_connection, dict_from_row, list_from_rows, init_db

def new_id() -> str:
    return str(uuid.uuid4())[:8]

def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

def default_scoring_config() -> dict:
    return {
        "skills": [],
        "experience_band": 2,
        "threshold": 75,
        "penalties": {
            "gap_over_12m": 8,
            "no_degree": 5,
            "job_hopping": 6,
            "missing_required_skills_pct": 12,
        },
        "bias_safeguards": {
            "anonymise_names": True,
            "suppress_university_prestige": True,
            "remove_graduation_year": False,
        },
    }

# ==================== ROLE CRUD ====================

def create_role(title: str, department: str, description: str) -> dict:
    conn = get_connection()
    cursor = conn.cursor()

    role_id = new_id()
    scoring_config = default_scoring_config()
    now = now_iso()

    cursor.execute("""
        INSERT INTO roles (id, title, department, description, scoring_config, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (role_id, title, department, description, json.dumps(scoring_config), now, now))

    conn.commit()
    conn.close()

    return {
        "id": role_id,
        "title": title,
        "department": department,
        "description": description,
        "scoring_config": scoring_config,
        "created_at": now,
        "updated_at": now,
    }

def get_all_roles() -> list:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM roles ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    conn.close()

    roles = []
    for row in rows:
        role = dict_from_row(row)
        role["scoring_config"] = json.loads(role["scoring_config"])
        roles.append(role)

    return roles

def get_role(role_id: str) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM roles WHERE id = ?", (role_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        role = dict_from_row(row)
        role["scoring_config"] = json.loads(role["scoring_config"])
        return role
    return None

def update_role(role_id: str, data: dict) -> dict | None:
    role = get_role(role_id)
    if not role:
        return None

    conn = get_connection()
    cursor = conn.cursor()

    title = data.get("title", role["title"])
    department = data.get("department", role["department"])
    description = data.get("description", role["description"])
    scoring_config = data.get("scoring_config", role["scoring_config"])

    now = now_iso()

    cursor.execute("""
        UPDATE roles
        SET title = ?, department = ?, description = ?, scoring_config = ?, updated_at = ?
        WHERE id = ?
    """, (title, department, description, json.dumps(scoring_config), now, role_id))

    conn.commit()
    conn.close()

    return get_role(role_id)

def delete_role(role_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM roles WHERE id = ?", (role_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()

    return deleted

# ==================== CANDIDATE CRUD ====================

def save_candidate(candidate: dict) -> dict:
    conn = get_connection()
    cursor = conn.cursor()

    candidate_id = candidate.get("id") or new_id()
    now = now_iso()
    uploaded_at = candidate.get("uploaded_at", now)

    cursor.execute("""
        INSERT OR REPLACE INTO candidates
        (id, name, filename, role_id, role_title, analysis, score, status,
         recruiter_summary, interview_questions, rejection_feedback, interview_profile,
         created_at, uploaded_at, malware_detected, malware_feedback)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        candidate_id,
        candidate["name"],
        candidate["filename"],
        candidate["role_id"],
        candidate["role_title"],
        json.dumps(candidate["analysis"]),
        json.dumps(candidate["score"]),
        candidate["status"],
        candidate.get("recruiter_summary"),
        json.dumps(candidate.get("interview_questions", [])),
        json.dumps(candidate.get("rejection_feedback")),
        json.dumps(candidate.get("interview_profile", {})),
        now,
        uploaded_at,
        candidate.get("malware_detected", False),
        json.dumps(candidate.get("malware_feedback")) if candidate.get("malware_feedback") else None
    ))

    conn.commit()
    conn.close()

    candidate["id"] = candidate_id
    candidate["created_at"] = now
    candidate["uploaded_at"] = uploaded_at
    return candidate

def get_all_candidates() -> list:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM candidates ORDER BY uploaded_at DESC")
    rows = cursor.fetchall()
    conn.close()

    candidates = []
    for row in rows:
        candidate = dict_from_row(row)
        candidate["analysis"] = json.loads(candidate["analysis"])
        candidate["score"] = json.loads(candidate["score"])
        candidate["interview_questions"] = json.loads(candidate["interview_questions"])
        candidate["rejection_feedback"] = json.loads(candidate["rejection_feedback"])
        candidate["interview_profile"] = json.loads(candidate["interview_profile"])
        if candidate.get("malware_feedback"):
            candidate["malware_feedback"] = json.loads(candidate["malware_feedback"])
        candidates.append(candidate)

    return candidates

def get_candidate(cid: str) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM candidates WHERE id = ?", (cid,))
    row = cursor.fetchone()
    conn.close()

    if row:
        candidate = dict_from_row(row)
        candidate["analysis"] = json.loads(candidate["analysis"])
        candidate["score"] = json.loads(candidate["score"])
        candidate["interview_questions"] = json.loads(candidate["interview_questions"])
        candidate["rejection_feedback"] = json.loads(candidate["rejection_feedback"])
        candidate["interview_profile"] = json.loads(candidate["interview_profile"])
        if candidate.get("malware_feedback"):
            candidate["malware_feedback"] = json.loads(candidate["malware_feedback"])
        return candidate
    return None

# ==================== VOICE INTERVIEW CRUD ====================

def save_voice_interview(voice_data: dict) -> dict:
    conn = get_connection()
    cursor = conn.cursor()

    voice_id = voice_data.get("id") or new_id()
    now = now_iso()

    cursor.execute("""
        INSERT OR REPLACE INTO voice_interviews
        (id, candidate_id, question_id, audio_path, transcript, communication_score,
         clarity_score, confidence_score, relevance_score, speaking_pace_score, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        voice_id,
        voice_data["candidate_id"],
        voice_data["question_id"],
        voice_data.get("audio_path"),
        voice_data.get("transcript"),
        voice_data.get("communication_score"),
        voice_data.get("clarity_score"),
        voice_data.get("confidence_score"),
        voice_data.get("relevance_score"),
        voice_data.get("speaking_pace_score"),
        now
    ))

    conn.commit()
    conn.close()

    voice_data["id"] = voice_id
    voice_data["created_at"] = now
    return voice_data

def get_voice_interviews(candidate_id: str) -> list:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM voice_interviews
        WHERE candidate_id = ?
        ORDER BY created_at DESC
    """, (candidate_id,))
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows] if rows else []

def get_voice_interview(voice_id: str) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM voice_interviews WHERE id = ?", (voice_id,))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None

# ==================== SEEDING ====================

def seed_demo():
    """Seed demo role if database is empty"""
    roles = get_all_roles()
    if roles:
        return

    role = create_role(
        title="Senior ML Engineer",
        department="Engineering",
        description="Build and deploy production ML systems at scale.",
    )

    role["scoring_config"]["skills"] = [
        {"name": "Python", "weight": 90, "required": True},
        {"name": "PyTorch", "weight": 75, "required": True},
        {"name": "MLOps", "weight": 65, "required": False},
        {"name": "Kubernetes", "weight": 50, "required": False},
        {"name": "System Design", "weight": 70, "required": True},
        {"name": "AWS / GCP", "weight": 55, "required": False},
    ]
    role["scoring_config"]["threshold"] = 75

    update_role(role["id"], role)
