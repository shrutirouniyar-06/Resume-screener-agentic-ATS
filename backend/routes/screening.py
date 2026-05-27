from flask import Blueprint, request, jsonify
from models.store_sqlite import (
    get_role, save_candidate, get_all_candidates, get_candidate,
    save_voice_interview, get_voice_interviews
)
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
from services.speech import transcribe_audio, analyze_communication, calculate_communication_score
from services.safety import (
    detect_prompt_injection,
    run_comprehensive_safety_checks,
    filter_toxic_output,
    audit_log,
    security_log,
)
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
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

        # SAFETY: Detect prompt injection attempts
        is_injection, pattern = detect_prompt_injection(resume_text)
        malware_detected = False
        malware_feedback = None

        if is_injection:
            malware_detected = True
            # Log the security incident
            incident = security_log.log_injection_attempt(
                pattern_detected=pattern,
                filename=file.filename,
                resume_snippet=resume_text[:200]
            )

            # Educational feedback explaining the malware/attack
            malware_feedback = {
                "what_is_this": "Prompt Injection Attack (Malware Practice)",
                "why_malicious": [
                    "This resume contains hidden instructions attempting to bypass the hiring system's safety mechanisms",
                    "It tries to manipulate the AI screening process to artificially approve an unqualified candidate",
                    "This is a form of system manipulation and fraud in the recruitment process",
                    "Such attacks undermine fair hiring practices and compromise system integrity"
                ],
                "attack_method": f"Detected pattern: '{pattern}'",
                "how_it_works": "The resume includes embedded commands disguised within normal resume content to trick the AI into ignoring qualification requirements or artificially inflating scores",
                "consequences": [
                    "Hiring unqualified candidates due to system manipulation",
                    "Loss of trust in the recruitment process",
                    "Potential legal liability for fraudulent hiring practices",
                    "Compromise of fair and merit-based evaluation"
                ],
                "security_impact": "CRITICAL - This is a direct attempt to compromise the integrity of the hiring system"
            }

            # Continue processing but mark as malware - don't block
            logger.warning(f"Malware detected in resume {file.filename}: {pattern}")

        # PII scrubbing

        safe_resume_text = scrub_pii(resume_text)

        # print("\n--- ANONYMIZED RESUME ---\n")
        # print(safe_resume_text[:1000])

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
    # 3. Safety Validation
    # -------------------------

    # Run comprehensive safety checks
    safety_report = run_comprehensive_safety_checks(
        analysis, safe_resume_text, analysis
    )

    # If critical safety issues, flag for review
    if not safety_report["all_passed"]:
        logger.warning("Safety checks failed - candidate flagged for review")

    # -------------------------
    # 4. Score
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

                # SAFETY: Filter for toxicity and bias in rejection feedback
                filtered_reason = filter_toxic_output(reviewed_reason)
                filtered_improvements = [filter_toxic_output(s) for s in reviewed_improvements]

                rejection_feedback = {
                    "reason": filtered_reason,
                    "improvement_suggestions": filtered_improvements,
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

    # If malware detected, prepend warning to recruiter summary
    final_recruiter_summary = recruiter_summary
    if malware_detected:
        final_recruiter_summary = f"[MALWARE DETECTED] This resume contains prompt injection attack attempting to manipulate the screening system.\n\n{recruiter_summary}"

    candidate = save_candidate(
        {
            "name": display_name,
            "filename": file.filename,
            "role_id": role_id,
            "role_title": role["title"],
            "analysis": analysis,
            "score": score_breakdown,
            "status": ("Shortlisted" if shortlisted else "Rejected"),
            "recruiter_summary": final_recruiter_summary,
            "interview_questions": interview_questions,
            "interview_profile": {},
            "rejection_feedback": rejection_feedback,
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "malware_detected": malware_detected,
            "malware_feedback": malware_feedback,
        }
    )

    # SAFETY: Log decision for audit trail
    audit_log.log_decision(
        candidate_id=candidate.get("id"),
        role_id=role_id,
        decision="shortlisted" if shortlisted else "rejected",
        score=score_breakdown.get("overall", 0),
        reason=recruiter_summary if shortlisted else (rejection_feedback.get("reason") if rejection_feedback else "No feedback"),
        analysis=analysis,
        safety_checks=safety_report["checks"]
    )

    # Add safety report and malware feedback to response
    candidate["safety_checks"] = safety_report
    candidate["malware_detected"] = malware_detected
    if malware_feedback:
        candidate["malware_feedback"] = malware_feedback

    return jsonify(candidate), 201


@screen_bp.get("/api/candidates")
def list_candidates():
    role_id = request.args.get("role_id")
    candidates = get_all_candidates()
    if role_id:
        candidates = [c for c in candidates if c.get("role_id") == role_id]

    # Clean up response - remove verbose malware_feedback but keep malware_detected as boolean
    cleaned = []
    for c in candidates:
        c["malware_detected"] = bool(c.get("malware_detected"))  # Ensure it's boolean, not 0/1
        if "malware_feedback" in c:
            del c["malware_feedback"]  # Remove verbose feedback from list view
        cleaned.append(c)

    return jsonify(cleaned)


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


# ==================== VOICE INTERVIEW ENDPOINTS ====================

@screen_bp.post("/api/candidates/<cid>/voice-interview")
def save_voice_response(cid):
    """Record and process voice interview response"""

    candidate = get_candidate(cid)
    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404

    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    question_id = request.form.get("question_id")

    if not question_id:
        return jsonify({"error": "question_id required"}), 400

    try:
        question_id = int(question_id)
    except ValueError:
        return jsonify({"error": "Invalid question_id"}), 400

    # Get the question for context
    questions = candidate.get("interview_questions", [])
    if question_id >= len(questions):
        return jsonify({"error": "Question not found"}), 404

    question = questions[question_id]["question"]

    try:
        # 1. Transcribe audio
        audio_bytes = audio_file.read()
        transcript = transcribe_audio(audio_bytes, "wav")

        # 2. Analyze communication
        metrics = analyze_communication(transcript, question)

        # 3. Calculate overall score
        communication_score = calculate_communication_score(metrics)

        # 4. Save voice interview record
        voice_interview = {
            "candidate_id": cid,
            "question_id": question_id,
            "audio_path": f"voice_{cid}_{question_id}.wav",
            "transcript": transcript,
            "communication_score": communication_score,
            "clarity_score": metrics.get("clarity", 0),
            "confidence_score": metrics.get("confidence", 0),
            "relevance_score": metrics.get("relevance", 0),
            "speaking_pace_score": metrics.get("speaking_pace", 0),
        }

        result = save_voice_interview(voice_interview)

        return jsonify({
            "success": True,
            "voice_interview": result,
            "transcript": transcript,
            "metrics": metrics,
            "communication_score": communication_score,
        }), 201

    except Exception as e:
        print(f"[VOICE] Error processing audio: {str(e)}")
        return jsonify({"error": f"Voice processing failed: {str(e)}"}), 500


@screen_bp.get("/api/candidates/<cid>/voice-interviews")
def get_voice_profile(cid):
    """Get all voice interview responses for a candidate"""

    candidate = get_candidate(cid)
    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404

    voice_interviews = get_voice_interviews(cid)

    # Calculate voice profile metrics
    if voice_interviews:
        avg_communication = sum(v.get("communication_score", 0) for v in voice_interviews) / len(voice_interviews)
        avg_clarity = sum(v.get("clarity_score", 0) for v in voice_interviews) / len(voice_interviews)
        avg_confidence = sum(v.get("confidence_score", 0) for v in voice_interviews) / len(voice_interviews)
        avg_relevance = sum(v.get("relevance_score", 0) for v in voice_interviews) / len(voice_interviews)
        avg_pace = sum(v.get("speaking_pace_score", 0) for v in voice_interviews) / len(voice_interviews)
    else:
        avg_communication = avg_clarity = avg_confidence = avg_relevance = avg_pace = 0

    return jsonify({
        "voice_interviews": voice_interviews,
        "voice_profile": {
            "communication_score": int(avg_communication),
            "clarity": int(avg_clarity),
            "confidence": int(avg_confidence),
            "relevance": int(avg_relevance),
            "speaking_pace": int(avg_pace),
        }
    })


# ============================================================================
# AI SAFETY & AUDIT ENDPOINTS
# ============================================================================

@screen_bp.get("/api/audit-trail")
def get_audit_trail():
    """Get complete audit trail of all screening decisions for compliance."""
    return jsonify({
        "audit_entries": audit_log.get_audit_trail(),
        "total_entries": len(audit_log.logs)
    })


@screen_bp.get("/api/audit-report")
def get_audit_report():
    """Get audit report summary for compliance reporting."""
    role_id = request.args.get("role_id")
    report = audit_log.get_audit_report(role_id)
    return jsonify(report)


@screen_bp.post("/api/safety-check")
def run_safety_check():
    """Manually run safety checks on a candidate decision."""
    data = request.get_json()
    candidate_id = data.get("candidate_id")

    candidate = get_candidate(candidate_id)
    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404

    analysis = candidate.get("analysis", {})
    rejection_reason = ""
    if candidate.get("status") == "Rejected":
        feedback = candidate.get("rejection_feedback", {})
        rejection_reason = feedback.get("reason", "")

    safety_report = run_comprehensive_safety_checks(
        analysis,
        "",  # No resume text in this context
        analysis,
        rejection_reason
    )

    return jsonify(safety_report)


# ============================================================================
# SECURITY INCIDENT ENDPOINTS
# ============================================================================

@screen_bp.get("/api/security-incidents")
def get_security_incidents():
    """Get all security incidents (injection attempts, etc)."""
    return jsonify({
        "incidents": security_log.get_all_incidents(),
        "total_incidents": len(security_log.incidents)
    })


@screen_bp.get("/api/security-summary")
def get_security_summary():
    """Get security incident summary for dashboard."""
    return jsonify(security_log.get_incidents_summary())
