def normalize_skills(skills: str) -> set[str]:
    return {
        skill.strip().lower()
        for skill in skills.split(",")
        if skill.strip()
    }


def calculate_match(student_skills: str, required_skills: str):
    student = normalize_skills(student_skills)
    required = normalize_skills(required_skills)
    if not required:
        return {"score": 0, "matched_skills": [], "missing_skills": []}
    matched = student & required
    missing = required - student
    score = (len(matched) / len(required)) * 100
    return {
        "score": round(score),
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
    }
