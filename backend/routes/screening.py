from flask import Blueprint, request, jsonify
from models.store_sqlite import get_role, save_candidate, get_all_candidates, get_candidate
from services.parser import extract_text
from services.scoring import calculate_score
from services.privacy import scrub_pii
from services.llm import (
    analyse_resume,
    generate_interview_questions,
    generate_rejection_feedback,
    generate_recruiter_summary,
    judge_and_revise,
)

screen_bp = Blueprint("screen", __name__)


# @screen_bp.post("/api/screen")
# def screen_resume():
#     if "resume" not in request.files:
#         return jsonify({"error": "No resume file provided"}), 400

#     file = request.files["resume"]
#     role_id = request.form.get("job_role_id")
#     if not role_id:
#         return jsonify({"error": "job_role_id required"}), 400

#     role = get_role(role_id)
#     if not role:
#         return jsonify({"error": "Role not found"}), 404


#     # 1. Parse resume
#     raw_bytes = file.read()
#     try:
#         resume_text = extract_text(raw_bytes, file.filename)

#         #PII scrubbing
#         safe_resume_text = scrub_pii(resume_text)
#         print("\n--- ANONYMIZED RESUME ---\n")
#         print(safe_resume_text[:1000])

#     except ValueError as e:
#         return jsonify({"error": str(e)}), 400


#     # 2. LLM Call 1 — structured analysis
#     try:
#         analysis = analyse_resume(safe_resume_text, role)
#     except Exception as e:
#         return jsonify({"error": f"LLM analysis failed: {e}"}), 500


#     # 3. Score
#     score_breakdown = calculate_score(analysis, role)
#     shortlisted = score_breakdown["shortlisted"]


#     # 4. LLM Call 4 — recruiter summary (always)
#     try:
#         recruiter_summary = generate_recruiter_summary(analysis, role, score_breakdown["overall"])

#         reviewed = (judge_and_revise(recruiter_summary,"recruiter summary"))

#         recruiter_summary = (
#             reviewed if reviewed else "Summary unavailable after AI review."
#         )

#     except Exception:
#         recruiter_summary = "Summary unavailable."


#     # 5. LLM Call 2 or 3 — interview questions or rejection feedback
#     interview_questions = []
#     rejection_feedback = None

#     if shortlisted:

#         try:

#             generated = (generate_interview_questions(analysis,role))

#             safe_questions = []

#             for q in generated:

#                 text = (q.get("question","")+ " "+ q.get("follow_up",""))

#                 reviewed = (judge_and_revise(text,"interview question"))

#                 if reviewed:

#                     q["question"] = (reviewed)

#                     safe_questions.append(q)

#             interview_questions = (safe_questions)

#         except Exception:
#             interview_questions = []

#     cfg = role["scoring_config"]
#     anonymise = cfg.get("bias_safeguards", {}).get("anonymise_names", False)
#     display_name = (
#         "Candidate " + analysis.get("candidate_name", "")[:1].upper() + "."
#         if anonymise
#         else analysis.get("candidate_name", file.filename)
#     )


#     candidate = save_candidate({
#         "name": display_name,
#         "filename": file.filename,
#         "role_id": role_id,
#         "role_title": role["title"],
#         "analysis": analysis,
#         "score": score_breakdown,
#         "status": "Shortlisted" if shortlisted else "Rejected",
#         "recruiter_summary": recruiter_summary,
#         "interview_questions": interview_questions,
#         "interview_profile": {},
#         "rejection_feedback": rejection_feedback,
#     })

#     return jsonify(candidate), 201


@screen_bp.post("/api/screen")
def screen_resume():

    if "resume" not in request.files:
        return jsonify({"error": "No resume file provided"}), 400

    file = request.files["resume"]

    role_id = request.form.get("job_role_id")

    if not role_id:
        return jsonify({"error": "job_role_id required"}), 400

    role = get_role(role_id)

    if not role:
        return jsonify({"error": "Role not found"}), 404

    # -------------------------
    # 1. Parse + Privacy Layer
    # -------------------------

    raw_bytes = file.read()

    try:

        resume_text = extract_text(raw_bytes, file.filename)

        # PII scrubbing

        safe_resume_text = scrub_pii(resume_text)

        print("\n--- ANONYMIZED RESUME ---\n")

        print(safe_resume_text[:1000])

    except ValueError as e:

        return jsonify({"error": str(e)}), 400

    # -------------------------
    # 2. LLM Analysis
    # -------------------------

    try:

        analysis = analyse_resume(safe_resume_text, role)

    except Exception as e:

        return jsonify({"error": f"LLM analysis failed: {e}"}), 500

    # -------------------------
    # 3. Score
    # -------------------------

    score_breakdown = calculate_score(analysis, role)

    shortlisted = score_breakdown["shortlisted"]

    # -------------------------
    # 4. Recruiter Summary
    # -------------------------

    try:

        recruiter_summary = generate_recruiter_summary(
            analysis, role, score_breakdown["overall"]
        )

        reviewed = judge_and_revise(recruiter_summary, "recruiter summary")

        recruiter_summary = (
            reviewed if reviewed else "Summary unavailable after AI review."
        )

    except Exception:

        recruiter_summary = "Summary unavailable."

    # -------------------------
    # 5. Questions / Feedback
    # -------------------------

    interview_questions = []
    rejection_feedback = None

    if shortlisted:

        try:

            generated = generate_interview_questions(analysis, role)

            safe_questions = []

            for q in generated:

                # judge question

                reviewed_question = judge_and_revise(
                    q.get("question", ""), "interview question"
                )

                # judge followup

                reviewed_followup = (
                    judge_and_revise(q.get("follow_up", ""), "interview follow up")
                    if q.get("follow_up")
                    else None
                )

                if reviewed_question:

                    q["question"] = reviewed_question

                    if reviewed_followup:
                        q["follow_up"] = reviewed_followup

                    safe_questions.append(q)

            interview_questions = safe_questions

        except Exception:

            interview_questions = []

    else:

        try:

            generated_feedback = generate_rejection_feedback(
                analysis, role, score_breakdown["overall"]
            )

            reviewed_reason = judge_and_revise(
                generated_feedback.get("reason", ""), "candidate feedback"
            )

            reviewed_improvements = []

            for item in generated_feedback.get("improvement_suggestions", []):

                revised = judge_and_revise(item, "candidate improvement suggestion")

                if revised:
                    reviewed_improvements.append(revised)

            if reviewed_reason:

                rejection_feedback = {
                    "reason": reviewed_reason,
                    "improvement_suggestions": reviewed_improvements,
                }

            else:

                rejection_feedback = {
                    "reason": "Feedback unavailable after AI review.",
                    "improvement_suggestions": [],
                }

        except Exception:

            rejection_feedback = None

    # -------------------------
    # 6. Display Name
    # -------------------------

    cfg = role["scoring_config"]

    anonymise = cfg.get("bias_safeguards", {}).get("anonymise_names", False)

    display_name = (
        "Candidate " + analysis.get("candidate_name", "")[:1].upper() + "."
        if anonymise
        else analysis.get("candidate_name", file.filename)
    )

    # -------------------------
    # 7. Save Candidate
    # -------------------------

    candidate = save_candidate(
        {
            "name": display_name,
            "filename": file.filename,
            "role_id": role_id,
            "role_title": role["title"],
            "analysis": analysis,
            "score": score_breakdown,
            "status": ("Shortlisted" if shortlisted else "Rejected"),
            "recruiter_summary": recruiter_summary,
            "interview_questions": interview_questions,
            "interview_profile": {},
            "rejection_feedback": rejection_feedback,
        }
    )

    return jsonify(candidate), 201


@screen_bp.get("/api/candidates")
def list_candidates():
    role_id = request.args.get("role_id")
    candidates = get_all_candidates()
    if role_id:
        candidates = [c for c in candidates if c.get("role_id") == role_id]
    return jsonify(candidates)


@screen_bp.get("/api/candidates/<cid>")
def fetch_candidate(cid):
    c = get_candidate(cid)
    if not c:
        return jsonify({"error": "Not found"}), 404
    return jsonify(c)


@screen_bp.post("/api/candidates/<cid>/interview-rating")
def save_interview_rating(cid):

    candidate = get_candidate(cid)

    if not candidate:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json(force=True)

    question_id = data.get("question_id")
    competency = data.get("competency")
    score = data.get("score")

    if competency is None or score is None:
        return jsonify({"error": "Invalid payload"}), 400

    profile = candidate.setdefault("interview_profile", {})

    profile.setdefault(competency, {})

    profile[competency][str(question_id)] = score

    return jsonify({"success": True, "profile": profile})


@screen_bp.get("/api/stats")
def stats():
    candidates = get_all_candidates()
    shortlisted = [c for c in candidates if c.get("status") == "Shortlisted"]
    avg_score = (
        round(sum(c["score"]["overall"] for c in candidates) / len(candidates))
        if candidates
        else 0
    )
    interviews_generated = sum(1 for c in candidates if c.get("interview_questions"))
    return jsonify(
        {
            "total_resumes": len(candidates),
            "shortlisted": len(shortlisted),
            "interviews_generated": interviews_generated,
            "avg_match_score": avg_score,
        }
    )
