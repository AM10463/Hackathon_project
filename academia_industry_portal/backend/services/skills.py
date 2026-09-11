from sqlmodel import Session, select

from models.skill import InternshipSkill, Skill, StudentSkill


def split_skills(value: str) -> set[str]:
    return {part.strip().lower() for part in value.split(",") if part.strip()}


def get_or_create_skill(session: Session, name: str) -> Skill:
    skill = session.exec(select(Skill).where(Skill.name == name)).first()
    if skill is None:
        skill = Skill(name=name)
        session.add(skill)
        session.flush()
    return skill


def sync_student_skills(session: Session, student_id: int, skills: str) -> None:
    for name in split_skills(skills):
        skill = get_or_create_skill(session, name)
        link = session.get(StudentSkill, (student_id, skill.id))
        if link is None:
            session.add(StudentSkill(student_id=student_id, skill_id=skill.id))


def sync_internship_skills(session: Session, internship_id: int, skills: str) -> None:
    for name in split_skills(skills):
        skill = get_or_create_skill(session, name)
        link = session.get(InternshipSkill, (internship_id, skill.id))
        if link is None:
            session.add(InternshipSkill(internship_id=internship_id, skill_id=skill.id))


def student_skill_names(session: Session, student_id: int) -> set[str]:
    statement = (
        select(Skill.name)
        .join(StudentSkill, StudentSkill.skill_id == Skill.id)
        .where(StudentSkill.student_id == student_id)
    )
    return set(session.exec(statement).all())


def internship_skill_names(session: Session, internship_id: int) -> set[str]:
    statement = (
        select(Skill.name)
        .join(InternshipSkill, InternshipSkill.skill_id == Skill.id)
        .where(InternshipSkill.internship_id == internship_id)
    )
    return set(session.exec(statement).all())
