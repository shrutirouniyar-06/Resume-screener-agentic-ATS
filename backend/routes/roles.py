from flask import Blueprint, request, jsonify
from models.store_sqlite import (
    create_role,
    get_all_roles,
    get_role,
    update_role,
    delete_role,
)
from services.scraper import suggest_skills, collect_market_text
from services.llm import generate_role_config

roles_bp = Blueprint("roles", __name__)


@roles_bp.get("/api/roles")
def list_roles():
    return jsonify(get_all_roles())


@roles_bp.post("/api/roles")
def add_role():
    data = request.get_json(force=True)
    role = create_role(
        title=data.get("title", "Untitled Role"),
        department=data.get("department", ""),
        description=data.get("description", ""),
    )
    return jsonify(role), 201


@roles_bp.get("/api/roles/<role_id>")
def fetch_role(role_id):
    role = get_role(role_id)
    if not role:
        return jsonify({"error": "Not found"}), 404
    return jsonify(role)


@roles_bp.put("/api/roles/<role_id>")
def edit_role(role_id):
    data = request.get_json(force=True)
    role = update_role(role_id, data)
    if not role:
        return jsonify({"error": "Not found"}), 404
    return jsonify(role)


@roles_bp.delete("/api/roles/<role_id>")
def remove_role(role_id):
    if delete_role(role_id):
        return jsonify({"ok": True})
    return jsonify({"error": "Not found"}), 404


@roles_bp.post("/api/roles/<role_id>/suggest-skills")
def skill_suggestions(role_id):
    data = request.get_json(force=True)
    job_title = data.get("job_title", "")
    if not job_title:
        return jsonify({"error": "job_title required"}), 400
    skills = suggest_skills(job_title)
    return jsonify({"suggested_skills": skills})


@roles_bp.post("/api/roles/auto-generate")
def auto_generate_role():
    data = request.get_json(force=True)

    job_title = data.get("job_title", "").strip()

    if not job_title:
        return jsonify({"error": "job_title required"}), 400

    try:
        market_text = collect_market_text(job_title)

        if not market_text.strip():
            return jsonify({"error": "No market data found"}), 400

        result = generate_role_config(job_title, market_text)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
