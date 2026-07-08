import json
import os
import re
from typing import Dict, List, Set

from dotenv import load_dotenv

load_dotenv()

SKILLS = [
    "python", "java", "javascript", "typescript", "react", "next.js", "node.js",
    "express", "fastapi", "django", "flask", "mongodb", "mysql", "postgresql",
    "sql", "html", "css", "tailwind", "bootstrap", "git", "github", "docker",
    "kubernetes", "aws", "azure", "gcp", "linux", "rest api", "graphql",
    "machine learning", "deep learning", "nlp", "llm", "openai", "tensorflow",
    "pytorch", "pandas", "numpy", "scikit-learn", "data analysis", "power bi",
    "tableau", "excel", "testing", "jest", "pytest", "ci/cd", "authentication",
    "jwt", "microservices", "redis", "firebase", "stripe", "razorpay",
]

ACTION_VERBS = [
    "built", "developed", "created", "designed", "implemented", "optimized",
    "automated", "integrated", "deployed", "improved", "analyzed", "managed",
]


def analyze_resume(resume_text: str, job_description: str) -> Dict:
    if os.getenv("OPENAI_API_KEY"):
        try:
            return analyze_with_openai(resume_text, job_description)
        except Exception:
            return analyze_locally(resume_text, job_description)
    return analyze_locally(resume_text, job_description)


def analyze_locally(resume_text: str, job_description: str) -> Dict:
    resume_lower = normalize(resume_text)
    jd_lower = normalize(job_description)

    resume_skills = extract_skills(resume_lower)
    jd_skills = extract_skills(jd_lower)
    matched = sorted(resume_skills & jd_skills)
    missing = sorted(jd_skills - resume_skills)

    keyword_score = calculate_keyword_score(resume_lower, jd_lower)
    skill_score = int((len(matched) / max(len(jd_skills), 1)) * 100)
    formatting_score = calculate_formatting_score(resume_text)
    ats_score = round((keyword_score * 0.45) + (skill_score * 0.4) + (formatting_score * 0.15))
    job_match_score = round((keyword_score * 0.55) + (skill_score * 0.45))

    strengths = []
    if matched:
        strengths.append(f"Strong match in {', '.join(matched[:6])}.")
    if has_metrics(resume_text):
        strengths.append("Resume includes measurable achievements.")
    if has_action_verbs(resume_lower):
        strengths.append("Resume uses action-oriented wording.")
    if not strengths:
        strengths.append("Resume has a readable base structure.")

    improvements = []
    if missing:
        improvements.append(f"Add relevant experience or projects for: {', '.join(missing[:8])}.")
    if not has_metrics(resume_text):
        improvements.append("Add numbers such as percentage improvement, users, revenue, time saved, or accuracy.")
    if len(resume_text.split()) < 250:
        improvements.append("Add more project details, responsibilities, tools, and outcomes.")
    if "project" not in resume_lower:
        improvements.append("Add a dedicated Projects section with technical impact.")

    better_wording = build_wording_suggestions(resume_text, matched, missing)

    recommended = missing[:10]
    if "openai" in jd_skills and "llm" not in resume_skills:
        recommended.append("llm")
    recommended = sorted(set(recommended))

    return {
        "ats_score": clamp(ats_score),
        "job_match_score": clamp(job_match_score),
        "matched_skills": matched,
        "missing_skills": missing,
        "recommended_skills": recommended,
        "strengths": strengths,
        "improvements": improvements,
        "better_wording": better_wording,
        "summary": build_summary(ats_score, matched, missing),
    }


def analyze_with_openai(resume_text: str, job_description: str) -> Dict:
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    prompt = f"""
Return only valid JSON. Analyze this resume against the job description.
Use this exact schema:
{{
  "ats_score": 0,
  "job_match_score": 0,
  "matched_skills": [],
  "missing_skills": [],
  "recommended_skills": [],
  "strengths": [],
  "improvements": [],
  "better_wording": [],
  "summary": ""
}}

Resume:
{resume_text[:12000]}

Job description:
{job_description[:8000]}
"""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an ATS resume analysis expert."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    parsed = json.loads(content)
    return normalize_result(parsed)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def extract_skills(text: str) -> Set[str]:
    found = set()
    for skill in SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"
        if re.search(pattern, text):
            found.add(skill)
    return found


def calculate_keyword_score(resume_text: str, job_description: str) -> int:
    jd_words = [
        word for word in re.findall(r"[a-zA-Z][a-zA-Z+#.]{2,}", job_description)
        if word not in {"and", "the", "with", "for", "you", "are", "this", "that"}
    ]
    top_keywords = list(dict.fromkeys(jd_words))[:80]
    matches = sum(1 for word in top_keywords if word in resume_text)
    return int((matches / max(len(top_keywords), 1)) * 100)


def calculate_formatting_score(resume_text: str) -> int:
    score = 45
    sections = ["experience", "education", "skills", "project"]
    score += sum(10 for section in sections if section in resume_text.lower())
    if "@" in resume_text:
        score += 5
    if re.search(r"\b\d{10}\b|\+\d", resume_text):
        score += 5
    return clamp(score)


def has_metrics(text: str) -> bool:
    return bool(re.search(r"\d+%|\b\d+\+?\b", text))


def has_action_verbs(text: str) -> bool:
    return any(verb in text for verb in ACTION_VERBS)


def build_wording_suggestions(resume_text: str, matched: List[str], missing: List[str]) -> List[str]:
    primary_skill = matched[0] if matched else (missing[0] if missing else "relevant technologies")
    return [
        f"Built and optimized a {primary_skill} based solution, improving workflow efficiency and user experience.",
        "Implemented REST APIs, authentication, and database operations to support production-style full-stack features.",
        "Improved project impact by adding measurable results such as response time, accuracy, users served, or time saved.",
    ]


def build_summary(score: int, matched: List[str], missing: List[str]) -> str:
    if score >= 80:
        level = "strong"
    elif score >= 60:
        level = "moderate"
    else:
        level = "low"
    return (
        f"This resume has a {level} match for the job description. "
        f"It matches {len(matched)} important skills and is missing {len(missing)} target skills."
    )


def normalize_result(result: Dict) -> Dict:
    defaults = analyze_locally("", "")
    defaults.update(result)
    defaults["ats_score"] = clamp(int(defaults.get("ats_score", 0)))
    defaults["job_match_score"] = clamp(int(defaults.get("job_match_score", 0)))
    for key in [
        "matched_skills", "missing_skills", "recommended_skills",
        "strengths", "improvements", "better_wording",
    ]:
        value = defaults.get(key)
        defaults[key] = value if isinstance(value, list) else []
    defaults["summary"] = str(defaults.get("summary", "Resume analysis completed."))
    return defaults


def clamp(value: int) -> int:
    return max(0, min(100, value))

