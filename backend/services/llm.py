"""
LLM calls via the OpenAI-compatible HuggingFace Inference API.
Set HF_TOKEN and HF_MODEL in .env
"""
import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
from services.llm_config import provider_config
from schemas.analysis_schema import (ResumeAnalysisSchema)
from pydantic import ValidationError


load_dotenv(override=True, dotenv_path="backend/.env")

PROVIDER=os.getenv("PROVIDER", "OPENROUTER")

try:
    API_KEY = os.getenv(provider_config[PROVIDER]["API_KEY"])
    BASE_URL = os.getenv(provider_config[PROVIDER]["BASE_URL"])
    MODEL = os.getenv(provider_config[PROVIDER]["MODEL"])

    if not API_KEY or not BASE_URL or not MODEL:
        raise EnvironmentError(
            f"Missing environment variables for {PROVIDER}"
        )

    print(f"Using {PROVIDER} provider, Model: {MODEL}")

except KeyError as e:
    raise EnvironmentError(
        f"Invalid provider config: {e}"
    )

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=BASE_URL,
            api_key=API_KEY,
        )
        print("LLM client initialised!")
    return _client


def _chat(messages: list[dict[str, str]], max_tokens: int = 1024, temperature: float = 0.4) -> str:
    client = get_client()
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()


def _extract_json(text: str) -> dict | list:
    """Pull the first JSON object or array out of a model response."""
    match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
    if match:
        return json.loads(match.group(1))
    raise ValueError(f"No JSON found in model output:\n{text}")


def judge_and_revise(text: str,content_type: str = "general",max_retries: int = 2):

    current = text

    for _ in range(
        max_retries + 1
    ):

        judge_prompt = f"""
            You are an AI safety and professionalism judge.

            Evaluate this {content_type}.

            APPROVE only if it is:

            - professional
            - non-toxic
            - non-discriminatory
            - role relevant
            - safe for hiring workflows
            - not vulgar or offensive

            Reject if:

            - abusive
            - hateful
            - discriminatory
            - vulgar
            - sexually explicit
            - irrelevant
            - inferior question quality

            Return ONLY JSON:

            {{
            "approved": true|false,
            "feedback": "<short reason>"
            }}

            TEXT:
            {current}
            """

        raw = _chat(
            [{
                "role": "user",
                "content":
                    judge_prompt
            }],
            temperature=0
        )

        result = (
            _extract_json(
                raw
            )
        )

        approved = (result.get("approved",False)
                    
            if isinstance(result,dict) else False
        )

        if approved:
            return current

        feedback = (
            result.get(
                "feedback",
                "Did not meet review."
            )
            if isinstance(
                result,
                dict
            )
            else "Did not meet review."
        )

        revise_prompt = f"""
            You previously generated a {content_type}.

            It failed review.

            Feedback:
            {feedback}

            Rewrite it professionally and safely.

            Return ONLY revised text.

            TEXT:
            {current}
            """

        current = _chat(
            [
                {
                    "role":"system",
                    "content":"You rewrite content professionally and safely."
                },
                {
                    "role":"user",
                    "content":revise_prompt
                }
            ]
        )

    return None


ALLOWED_COMPETENCIES = {
    "technical_depth",
    "problem_solving",
    "communication",
    "leadership",
    "ownership",
    "system_design",
    "collaboration",
    "adaptability",
}


def _normalise_questions(questions: list[dict]) -> list[dict]:
    cleaned = []

    for q in questions:
        comps = q.get("competencies", [])

        comps = [
            c.lower().replace(" ", "_")
            for c in comps
            if c.lower().replace(" ", "_")
            in ALLOWED_COMPETENCIES
        ]

        if not comps:
            comps = ["technical_depth"]

        cleaned.append({
            "type": q.get("type", "Technical"),
            "category": q.get("category", "General"),
            "question": q.get("question", ""),
            "follow_up": q.get("follow_up", ""),
            "competencies": comps
        })

    return cleaned


# ---------------------------------------------------------------------------
# LLM Call 1 — Resume analysis & scoring data extraction
# ---------------------------------------------------------------------------
def analyse_resume(resume_text: str, role: dict) -> dict:
    
    required_skills = [s["name"] for s in role["scoring_config"]["skills"]]
    
    prompt = f"""You are an expert technical recruiter. Analyse the resume below for the role of "{role['title']}".

Required skills to look for: {", ".join(required_skills)}

Return ONLY a JSON object with this exact shape:
{{
  "skills_found": ["skill1", "skill2"],
  "years_experience": <integer>,
  "has_relevant_degree": <true|false>,
  "employment_gaps_over_12m": <integer count>,
  "job_count_last_2yr": <integer>,
  "candidate_name": "<full name or 'Unknown'>",
  "summary": "<2-sentence profile summary>"
}}

Resume:
{resume_text[:4000]}
"""
    raw = _chat([{"role": "user", "content": prompt}])
    result=_extract_json(raw)

    #validation part: pydantic guardrail
    try:

        validated = (
            ResumeAnalysisSchema
            .model_validate(
                result
            )
        )

        return validated.model_dump()

    except ValidationError as e:

        raise ValueError(
            f"LLM schema validation failed: {e}"
        )


# ---------------------------------------------------------------------------
# LLM Call 2 — Interview question generation
# ---------------------------------------------------------------------------
def generate_interview_questions(candidate_analysis: dict, role: dict) -> list[dict]:
    """
    Returns interview intelligence question objects.
    """

    skills = ", ".join(candidate_analysis.get("skills_found", []))
    role_skills = ", ".join(
        s["name"]
        for s in role["scoring_config"]["skills"]
    )

    prompt = f"""
You are a senior technical interviewer.

Generate 10 HIGH-QUALITY interview questions for a candidate applying for:

Role: {role['title']}

Candidate skills:
{skills}

Role skills:
{role_skills}

Experience:
{candidate_analysis.get('years_experience', '?')} years

Generate:

- 4 technical validation
- 2 project deep-dive
- 2 behavioural
- 1 situational
- 1 risk / weakness probe

Questions should be:

- role-specific
- resume-grounded
- not generic
- include follow-up

Return ONLY JSON array:

[
  {{
    "type":"Technical",
    "category":"Backend",
    "question":"...",
    "follow_up":"...",
    "competencies":[
      "technical_depth",
      "problem_solving"
    ]
  }}
]

Allowed competencies:

technical_depth
problem_solving
communication
leadership
ownership
system_design
collaboration
adaptability
"""
    raw = _chat(
        [{"role":"user","content":prompt}],
        max_tokens=1600,
        temperature=0.4
    )

    result = _extract_json(raw)

    if not isinstance(result, list):
        return []

    return _normalise_questions(result)



# ---------------------------------------------------------------------------
# LLM Call 3 — Rejection feedback
# ---------------------------------------------------------------------------
def generate_rejection_feedback(candidate_analysis: dict, role: dict, score: int) -> dict:
    """
    Returns {reason, improvement_suggestions: [str]}
    Feedback is grounded in actual resume gaps, not hallucinated skills.
    """
    candidate_skills = [s.lower() for s in candidate_analysis.get('skills_found', [])]
    required_skills = [s['name'].lower() for s in role['scoring_config']['skills']]

    # Find skills that are MISSING (not in candidate's resume)
    missing_skills = [s for s in required_skills if s.lower() not in candidate_skills]

    # If all skills are present, find other gaps
    gap_analysis = ""
    if missing_skills:
        gap_analysis = f"\n\nMissing skills compared to job requirements: {', '.join(missing_skills[:3])}"
    else:
        gap_analysis = "\n\nAll listed skills are present. Focus on experience gaps or other factors."

    prompt = f"""You are a compassionate HR professional. A candidate scored {score}% for the role "{role['title']}" and did not meet the threshold.

CRITICAL INSTRUCTION: Only suggest improvements for skills they DON'T have. Never suggest they learn skills they already list.

Candidate skills found: {', '.join(candidate_analysis.get('skills_found', []))}
Years of experience: {candidate_analysis.get('years_experience', '?')}
Required skills for role: {', '.join(required_skills)}
{gap_analysis}

Write a polite, constructive response focusing ONLY on genuine gaps. Return ONLY JSON:
{{
  "reason": "<2-sentence polite explanation that is truthful>",
  "improvement_suggestions": ["Only suggest skills/experience they actually lack, grounded in the role requirements"]
}}

IMPORTANT: Do NOT suggest they learn Figma, Adobe XD, or Sketch if those tools appear in their skills list. Do NOT suggest they develop user research skills if they already mention conducting interviews or usability testing.
"""
    raw = _chat([{"role": "user", "content": prompt}], max_tokens=512)
    return _extract_json(raw)


# ---------------------------------------------------------------------------
# LLM Call 4 — Recruiter summary
# ---------------------------------------------------------------------------
def generate_recruiter_summary(candidate_analysis: dict, role: dict, score: int) -> str:
    prompt = f"""You are a recruitment assistant. Write a concise 3-sentence summary for a busy recruiter about this candidate for "{role['title']}".

Score: {score}%
Skills: {', '.join(candidate_analysis.get('skills_found', []))}
Experience: {candidate_analysis.get('years_experience', '?')} years
Degree: {'Yes' if candidate_analysis.get('has_relevant_degree') else 'No'}

Focus on: top strengths, key gaps, and overall recommendation. Be direct.
Return plain text only, no JSON.
"""
    return _chat([{"role": "user", "content": prompt}], max_tokens=256)


# ---------------------------------------------------------------------------
# LLM Call 5 — Role auto-generation
# ---------------------------------------------------------------------------

def generate_role_config(job_title: str, market_text: str) -> dict:
    """
    Generate role description + scoring config from market job postings.
    """

    prompt = f"""
You are a senior technical recruiter and hiring manager.

Based on these job postings for "{job_title}", generate an ATS-ready role configuration.

Return ONLY valid JSON:

{{
  "description": "<2-4 sentence job description>",
  "skills": [
    {{
      "name": "Python",
      "weight": 90,
      "required": true
    }}
  ],
  "experience_band": <0-3>,
  "threshold": <50-95>
}}

Rules:

- 6-10 skills
- weights 20-100
- 2-4 skills required=true
- experience_band:
  0 = 0-2 yrs
  1 = 3-4 yrs
  2 = 5-7 yrs
  3 = 8+ yrs
- threshold realistic for market

Job postings:
{market_text[:6000]}
"""

    raw = _chat(
        [{"role": "user", "content": prompt}],
        max_tokens=1200,
        temperature=0.3,
    )

    return _extract_json(raw)