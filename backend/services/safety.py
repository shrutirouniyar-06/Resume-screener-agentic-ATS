"""
AI Safety & Validation Module
Implements: Prompt injection detection, output validation, hallucination detection,
toxicity filtering, bias detection, audit logging, and explainability
"""

import re
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Tuple
from better_profanity import profanity

logger = logging.getLogger(__name__)

# ============================================================================
# 1. PROMPT INJECTION DETECTION
# ============================================================================

INJECTION_PATTERNS = [
    r"ignore\s+(?:all\s+)?instructions?",
    r"forget\s+(?:all\s+)?instructions?",
    r"bypass\s+(?:safety|filter|restriction)",
    r"override\s+(?:rules|restrictions|guidelines)",
    r"execute\s+(?:command|code|prompt)",
    r"print\s+(?:system|secret|api|key)",
    r"show\s+(?:system|hidden|secret|prompt)",
    r"what\s+are\s+your\s+instructions",
    r"who\s+(?:are\s+)?you\s+(?:really)?",
    r"you\s+are\s+(?:actually|really)\s+(?:a|an|the)",
    r"(?:^|[\s])(?:act|behave|pretend)\s+(?:as|like|that|you're)\s+(?:a\s+)?(?:attacker|hacker|jailbreak)",
    r"</?system>",
    r"</?admin>",
    r"<!-- .{1,100} -->",
    r"\[SYSTEM\]",
    r"\[ADMIN\]",
]

INJECTION_COMPILED = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]

def detect_prompt_injection(text: str) -> Tuple[bool, str]:
    """
    Detect potential prompt injection attempts in input text.
    Returns: (is_injection, detected_pattern)
    """
    if not text:
        return False, ""

    for compiled_pattern in INJECTION_COMPILED:
        match = compiled_pattern.search(text)
        if match:
            return True, match.group(0)

    return False, ""


# ============================================================================
# 2. LLM OUTPUT VALIDATION
# ============================================================================

def validate_score(value: Any, field_name: str = "score") -> Tuple[bool, str]:
    """Validate that score is within 0-100 range."""
    try:
        score = float(value)
        if not (0 <= score <= 100):
            return False, f"{field_name} out of range (0-100): {score}"
        return True, ""
    except (TypeError, ValueError):
        return False, f"{field_name} is not a valid number: {value}"


def validate_output_structure(output: Dict[str, Any], expected_fields: List[str]) -> Tuple[bool, str]:
    """Validate output has required fields."""
    if not isinstance(output, dict):
        return False, "Output is not a dictionary"

    missing = [f for f in expected_fields if f not in output]
    if missing:
        return False, f"Missing required fields: {missing}"

    return True, ""


def validate_text_length(text: str, min_len: int = 1, max_len: int = 2000, field: str = "text") -> Tuple[bool, str]:
    """Validate text length is reasonable."""
    if not isinstance(text, str):
        return False, f"{field} is not a string"

    length = len(text)
    if length < min_len:
        return False, f"{field} too short ({length} < {min_len})"
    if length > max_len:
        return False, f"{field} too long ({length} > {max_len})"

    return True, ""


def validate_json_fields(obj: Dict, field_specs: Dict[str, Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validate JSON object fields against specifications.
    field_specs: {field_name: {type, min, max, required}}
    """
    errors = []

    for field_name, spec in field_specs.items():
        if spec.get("required", True) and field_name not in obj:
            errors.append(f"Missing required field: {field_name}")
            continue

        if field_name not in obj:
            continue

        value = obj[field_name]

        # Type validation
        expected_type = spec.get("type")
        if expected_type and not isinstance(value, expected_type):
            errors.append(f"{field_name}: expected {expected_type.__name__}, got {type(value).__name__}")

        # String length validation
        if isinstance(value, str):
            min_len = spec.get("min_len", 0)
            max_len = spec.get("max_len", 10000)
            if len(value) < min_len:
                errors.append(f"{field_name}: too short ({len(value)} < {min_len})")
            if len(value) > max_len:
                errors.append(f"{field_name}: too long ({len(value)} > {max_len})")

        # Numeric range validation
        if isinstance(value, (int, float)):
            if "min" in spec and value < spec["min"]:
                errors.append(f"{field_name}: below minimum ({value} < {spec['min']})")
            if "max" in spec and value > spec["max"]:
                errors.append(f"{field_name}: above maximum ({value} > {spec['max']})")

    return len(errors) == 0, errors


# ============================================================================
# 3. HALLUCINATION DETECTION
# ============================================================================

def detect_hallucination(claim: str, source_text: str, min_overlap: float = 0.3) -> Tuple[bool, str]:
    """
    Detect if a claim appears to be hallucinated (not grounded in source).
    Uses keyword overlap analysis.
    """
    if not source_text:
        return True, "No source text to verify against"

    # Extract keywords from claim
    claim_words = set(re.findall(r'\b\w{4,}\b', claim.lower()))
    source_words = set(re.findall(r'\b\w{4,}\b', source_text.lower()))

    if not claim_words:
        return True, "Claim has no significant keywords"

    overlap = len(claim_words & source_words) / len(claim_words)

    if overlap < min_overlap:
        return True, f"Low keyword overlap ({overlap:.1%}) - possible hallucination"

    return False, ""


def check_grounding(analysis_text: str, resume_text: str, min_phrases: int = 2) -> Tuple[bool, List[str]]:
    """
    Check if analysis findings are grounded in resume.
    Returns (is_grounded, missing_grounds)
    """
    suspicious_claims = []

    # Look for strong skill claims
    skill_pattern = r"(?:expert|master|proficient|advanced)\s+(?:in|with|at)\s+(\w+)"
    for match in re.finditer(skill_pattern, analysis_text, re.IGNORECASE):
        skill = match.group(1).lower()
        if skill not in resume_text.lower():
            suspicious_claims.append(f"Ungrounded skill claim: {skill}")

    # Look for experience claims
    exp_pattern = r"(\d+)\+?\s+years?\s+(?:of\s+)?(?:experience|expertise)"
    for match in re.finditer(exp_pattern, analysis_text):
        years_str = match.group(1)
        if years_str not in resume_text:
            suspicious_claims.append(f"Ungrounded experience claim: {years_str}+ years")

    return len(suspicious_claims) == 0, suspicious_claims


# ============================================================================
# 4. TOXICITY & PROFANITY FILTERING
# ============================================================================

# Initialize profanity filter
profanity.load_censor_words()

BIASED_PHRASES = {
    # Age bias
    r"overqualified": "candidate has excess qualifications",
    r"too (?:experienced|senior)": "candidate has significant experience",
    r"outdated(?:\s+skills)?": "candidate's skills need refresh",
    r"set in (?:their|his|her) ways?": "candidate has strong experience",
    r"old\s+school": "candidate uses traditional approaches",

    # Gender bias
    r"\b(?:aggressive|bossy)\b": "assertive",
    r"(?:emotional|dramatic|hysterical)": "expressive",
    r"(?:motherhood|paternity) gap": "career break",
    r"too (?:pretty|attractive)": "[remove - appearance irrelevant]",

    # Disability bias
    r"(?:crazy|insane|lame|dumb)": "[remove - ableist language]",
    r"(?:suffers from|afflicted with|handicapped)": "has",
    r"(?:special needs|differently abled)": "[avoid jargon]",

    # Ethnicity/culture bias
    r"(?:articulate|well-spoken)\s+(?:for|because)": "[remove - coded language]",
    r"(?:exotic|unique) (?:background|culture)": "diverse background",
    r"(?:foreigner|alien)": "person from another country",

    # General toxicity patterns
    r"(?:lazy|incompetent|useless)": "not suitable",
    r"(?:stupid|idiotic|moronic)": "not qualified",
}

BIASED_COMPILED = {re.compile(k, re.IGNORECASE): v for k, v in BIASED_PHRASES.items()}

def check_toxicity(text: str) -> Tuple[bool, List[str]]:
    """
    Check text for toxic/profane language.
    Returns (is_clean, issues_found)
    """
    issues = []

    # Check for profanity
    if profanity.contains_profanity(text):
        censored = profanity.censor(text)
        issues.append(f"Profanity detected: {censored}")

    # Check for biased language
    for pattern, suggestion in BIASED_COMPILED.items():
        matches = pattern.finditer(text)
        for match in matches:
            issues.append(f"Biased language '{match.group(0)}' detected - suggest '{suggestion}'")

    return len(issues) == 0, issues


def filter_toxic_output(text: str, replacement: str = "[filtered]") -> str:
    """Remove or censor toxic content from output."""
    # Censor profanity
    text = profanity.censor(text)

    # Replace biased phrases
    for pattern, suggestion in BIASED_COMPILED.items():
        text = pattern.sub(lambda m: f"{suggestion}", text)

    return text


# ============================================================================
# 5. FAIRNESS & BIAS DETECTION
# ============================================================================

def check_fairness_in_decision(
    rejection_reason: str,
    score: float,
    analysis: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """
    Check if decision and reasoning are fair/unbiased.
    Returns (is_fair, concerns)
    """
    concerns = []

    # Check for score-reason mismatch
    reason_lower = rejection_reason.lower()
    if score > 70 and any(word in reason_lower for word in ["poor", "bad", "weak", "lacking"]):
        concerns.append("Score contradicts rejection reason (high score but negative language)")

    # Check for biased language in reason
    is_clean, toxic_issues = check_toxicity(rejection_reason)
    if not is_clean:
        concerns.extend(toxic_issues)

    # Check for vague/unsupported reasons
    if len(rejection_reason) < 20:
        concerns.append("Rejection reason too brief - lacks specific justification")

    # Check for protected characteristic references
    protected_attrs = ["age", "gender", "race", "ethnicity", "religion", "disability",
                       "marital", "parental", "sexual", "orientation"]
    for attr in protected_attrs:
        if attr in reason_lower:
            concerns.append(f"Possible reference to protected characteristic: {attr}")

    return len(concerns) == 0, concerns


# ============================================================================
# 6. AUDIT LOGGING & EXPLAINABILITY
# ============================================================================

class DecisionAuditLog:
    """Log all screening decisions for audit trail and compliance."""

    def __init__(self):
        self.logs = []

    def log_decision(
        self,
        candidate_id: str,
        role_id: str,
        decision: str,  # "shortlisted" or "rejected"
        score: float,
        reason: str,
        analysis: Dict[str, Any],
        safety_checks: Dict[str, Any],
        timestamp: str = None
    ) -> Dict[str, Any]:
        """Log a screening decision with full context."""

        log_entry = {
            "timestamp": timestamp or datetime.now().isoformat(),
            "candidate_id": candidate_id,
            "role_id": role_id,
            "decision": decision,
            "score": score,
            "reason": reason,
            "analysis_summary": {
                "skills_found": analysis.get("skills_found", [])[:5],  # Top 5
                "years_experience": analysis.get("years_experience"),
                "education": analysis.get("has_relevant_degree"),
            },
            "safety_checks": safety_checks,
            "explanation": self._generate_explanation(decision, score, reason, analysis),
        }

        self.logs.append(log_entry)
        logger.info(f"Decision logged: {candidate_id} -> {decision} (score: {score})")

        return log_entry

    def _generate_explanation(
        self,
        decision: str,
        score: float,
        reason: str,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate human-readable explanation for decision."""

        skills = analysis.get("skills_found", [])[:3]
        experience = analysis.get("years_experience", 0)
        education = analysis.get("has_relevant_degree", False)

        explanation = {
            "decision_summary": f"Candidate {decision.upper()}",
            "score_justification": f"Overall match: {score}%",
            "key_factors": {
                "skills": f"Found {len(skills)} matching skills: {', '.join(skills)}",
                "experience": f"{experience} years of experience",
                "education": "Relevant degree present" if education else "No relevant degree found",
            },
            "decision_reason": reason,
            "support_from_resume": [
                f"- {skill} mentioned in resume" for skill in skills[:3]
            ]
        }

        return explanation

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Return full audit trail."""
        return self.logs

    def get_audit_report(self, role_id: str = None) -> Dict[str, Any]:
        """Generate audit report (for compliance)."""

        filtered = self.logs if not role_id else [l for l in self.logs if l["role_id"] == role_id]

        shortlisted = len([l for l in filtered if l["decision"] == "shortlisted"])
        rejected = len([l for l in filtered if l["decision"] == "rejected"])
        avg_score = sum(l["score"] for l in filtered) / len(filtered) if filtered else 0

        return {
            "total_candidates": len(filtered),
            "shortlisted_count": shortlisted,
            "rejected_count": rejected,
            "shortlist_rate": f"{(shortlisted / len(filtered) * 100):.1f}%" if filtered else "N/A",
            "average_score": round(avg_score, 1),
            "audit_entries": len(filtered),
            "generated_at": datetime.now().isoformat(),
        }

# Global audit log instance
audit_log = DecisionAuditLog()


# ============================================================================
# 7. SAFETY CHECK AGGREGATOR
# ============================================================================

def run_comprehensive_safety_checks(
    candidate_data: Dict[str, Any],
    resume_text: str,
    llm_output: Dict[str, Any],
    rejection_reason: str = None,
) -> Dict[str, Any]:
    """
    Run all safety checks on candidate screening process.
    Returns detailed safety report.
    """

    report = {
        "timestamp": datetime.now().isoformat(),
        "all_passed": True,
        "checks": {}
    }

    # 1. Check for injection in input
    is_injection, pattern = detect_prompt_injection(resume_text)
    report["checks"]["prompt_injection"] = {
        "passed": not is_injection,
        "detected": is_injection,
        "pattern": pattern if is_injection else None,
    }
    if is_injection:
        report["all_passed"] = False

    # 2. Validate LLM output structure
    required_fields = ["overall", "skills", "experience", "profile"]
    valid_struct, struct_errors = validate_output_structure(llm_output, required_fields)
    report["checks"]["output_structure"] = {
        "passed": valid_struct,
        "errors": struct_errors,
    }
    if not valid_struct:
        report["all_passed"] = False

    # 3. Validate score ranges
    score_errors = []
    for field in ["overall", "skills", "experience", "profile"]:
        valid, error = validate_score(llm_output.get(field), field)
        if not valid:
            score_errors.append(error)

    report["checks"]["score_validation"] = {
        "passed": len(score_errors) == 0,
        "errors": score_errors,
    }
    if score_errors:
        report["all_passed"] = False

    # 4. Check for hallucination
    skills_list = llm_output.get('skills_found', []) if isinstance(llm_output.get('skills_found'), list) else []
    skills_claim = f"Found skills: {', '.join(str(s) for s in skills_list)}" if skills_list else "No skills found"
    is_hallucinated, hallucin_reason = detect_hallucination(skills_claim, resume_text)
    grounded, ungrounded = check_grounding(str(llm_output), resume_text)

    report["checks"]["hallucination_detection"] = {
        "passed": not is_hallucinated and grounded,
        "hallucinated": is_hallucinated,
        "reason": hallucin_reason,
        "ungrounded_claims": ungrounded,
    }
    if is_hallucinated or not grounded:
        report["all_passed"] = False

    # 5. Check for toxicity in output
    if rejection_reason:
        is_clean, toxic_issues = check_toxicity(rejection_reason)
        report["checks"]["toxicity_filtering"] = {
            "passed": is_clean,
            "issues": toxic_issues,
            "filtered_version": filter_toxic_output(rejection_reason) if not is_clean else None,
        }
        if not is_clean:
            report["all_passed"] = False

    # 6. Check fairness in decision
    if rejection_reason:
        is_fair, fairness_concerns = check_fairness_in_decision(
            rejection_reason,
            llm_output.get("overall", 50),
            candidate_data
        )
        report["checks"]["fairness_check"] = {
            "passed": is_fair,
            "concerns": fairness_concerns,
        }
        if not is_fair:
            report["all_passed"] = False

    # 7. Summary
    report["summary"] = {
        "total_checks": len(report["checks"]),
        "passed_checks": sum(1 for c in report["checks"].values() if c.get("passed", True)),
        "safety_score": f"{(sum(1 for c in report['checks'].values() if c.get('passed', True)) / len(report['checks']) * 100):.0f}%",
        "requires_review": not report["all_passed"],
    }

    return report
