"""
Scrape job boards for skill suggestions given a job title.
Returns a deduplicated list of frequently-mentioned skills.
"""
import re
import requests
from collections import Counter
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

# Common tech skills to detect in scraped text
SKILL_PATTERNS = [
    "python","java","javascript","typescript","go","rust","c\\+\\+","c#","ruby","scala",
    "react","angular","vue","node\\.js","django","flask","fastapi","spring",
    "sql","postgresql","mysql","mongodb","redis","elasticsearch","cassandra",
    "aws","gcp","azure","docker","kubernetes","terraform","ansible","jenkins","ci/cd",
    "machine learning","deep learning","nlp","pytorch","tensorflow","scikit-learn",
    "spark","hadoop","kafka","airflow","dbt","mlops","llm","rag",
    "git","linux","bash","rest api","graphql","microservices","system design",
    "data structures","algorithms","agile","scrum",
]

_COMPILED = [re.compile(r'\b' + p + r'\b', re.IGNORECASE) for p in SKILL_PATTERNS]
_SKILL_NAMES = [
    "Python","Java","JavaScript","TypeScript","Go","Rust","C++","C#","Ruby","Scala",
    "React","Angular","Vue","Node.js","Django","Flask","FastAPI","Spring",
    "SQL","PostgreSQL","MySQL","MongoDB","Redis","Elasticsearch","Cassandra",
    "AWS","GCP","Azure","Docker","Kubernetes","Terraform","Ansible","Jenkins","CI/CD",
    "Machine Learning","Deep Learning","NLP","PyTorch","TensorFlow","Scikit-learn",
    "Spark","Hadoop","Kafka","Airflow","dbt","MLOps","LLM","RAG",
    "Git","Linux","Bash","REST API","GraphQL","Microservices","System Design",
    "Data Structures","Algorithms","Agile","Scrum",
]


def _extract_skills_from_text(text: str) -> list[str]:
    found = []
    for i, pat in enumerate(_COMPILED):
        if pat.search(text):
            found.append(_SKILL_NAMES[i])
    return found


def _scrape_indeed(job_title: str) -> str:
    query = job_title.replace(" ", "+")
    url = f"https://www.indeed.com/jobs?q={query}&l=Remote"
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.find_all("div", class_=re.compile("job_seen_beacon|jobsearch-SerpJobCard"))
        return " ".join(c.get_text(" ") for c in cards[:10])
    except Exception:
        return ""


def _scrape_remotive(job_title: str) -> str:
    """Remotive has a public API — no scraping needed."""
    try:
        r = requests.get(
            "https://remotive.com/api/remote-jobs",
            params={"search": job_title, "limit": 20},
            timeout=8,
        )
        jobs = r.json().get("jobs", [])
        return " ".join(j.get("description", "") for j in jobs[:10])
    except Exception:
        return ""


def suggest_skills(job_title: str) -> list[str]:
    """
    Return job-specific skills based on job title.
    Uses role-based mapping for accuracy, falls back to scraping/generic.
    """
    role_skills = {
        "ux/ui designer": ["Figma", "Adobe XD", "Sketch", "User Research", "Interaction Design", "Wireframing", "Prototyping", "User Testing", "Design Systems", "Usability Testing"],
        "ui designer": ["Figma", "Adobe XD", "Sketch", "Visual Design", "Typography", "Color Theory", "Design Systems", "CSS", "HTML", "Responsive Design"],
        "ux designer": ["User Research", "Interaction Design", "Wireframing", "Usability Testing", "Information Architecture", "User Testing", "Prototyping", "Journey Mapping"],
        "product manager": ["Product Strategy", "User Research", "A/B Testing", "Analytics", "Roadmapping", "Agile", "Jira", "Data Analysis", "Communication", "Stakeholder Management"],
        "backend engineer": ["Python", "SQL", "REST API", "Microservices", "System Design", "Database Design", "Docker", "Kubernetes", "AWS", "Git"],
        "frontend engineer": ["React", "JavaScript", "CSS", "HTML", "TypeScript", "Web Performance", "Redux", "Git", "REST API", "Responsive Design"],
        "full stack engineer": ["React", "Node.js", "JavaScript", "SQL", "MongoDB", "AWS", "Docker", "Git", "REST API", "System Design"],
        "data scientist": ["Python", "SQL", "Statistics", "Machine Learning", "TensorFlow", "Pandas", "Data Visualization", "Jupyter", "Linear Algebra", "SQL"],
        "devops engineer": ["AWS", "Kubernetes", "Docker", "CI/CD", "Infrastructure as Code", "Terraform", "Jenkins", "Linux", "Git", "Monitoring"],
        "data engineer": ["Python", "SQL", "Apache Spark", "Data Warehousing", "ETL", "AWS", "Kafka", "Git", "Data Modeling", "Airflow"],
        "ml engineer": ["Python", "Machine Learning", "TensorFlow", "PyTorch", "SQL", "Statistics", "Deep Learning", "Model Deployment", "Docker", "AWS"],
        "qa engineer": ["Test Automation", "Selenium", "Test Design", "SQL", "API Testing", "Performance Testing", "Jira", "Git", "Python", "Documentation"],
        "software engineer": ["Python", "Java", "JavaScript", "System Design", "SQL", "Docker", "AWS", "Git", "REST API", "Algorithms"],
    }

    job_title_lower = job_title.lower().strip()

    # Try exact match first
    for role_key, skills in role_skills.items():
        if role_key in job_title_lower or job_title_lower in role_key:
            return skills

    # Try partial match (substring matching)
    for role_key, skills in role_skills.items():
        words = role_key.split()
        if any(word in job_title_lower for word in words):
            return skills

    # Fallback: Try scraping
    text = _scrape_remotive(job_title) + " " + _scrape_indeed(job_title)
    if text.strip():
        found = _extract_skills_from_text(text)
        counts = Counter(found)
        top_skills = [skill for skill, _ in counts.most_common(15)]
        if top_skills:
            return top_skills

    # Final fallback: return generic skills
    return ["Python", "System Design", "SQL", "Docker", "Git", "REST API", "Agile"]


def collect_market_text(job_title: str) -> str:
    """
    Aggregate market job descriptions for LLM synthesis.
    """
    return (
        _scrape_remotive(job_title)
        + " "
        + _scrape_indeed(job_title)
    )