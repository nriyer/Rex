# === resume_formatter.py ===

from typing import List


def format_experience_section(jobs: List[dict]) -> str:
    """
    Formats a list of enhanced job dicts into a clean, copy-pasteable
    'Experience' section string with proper bullets and spacing.
    """
    lines = []

    for job in jobs:
        header = f"📌 {job['title']} at {job['company']} {job['date_range']}"
        lines.append(header)

        for bullet in job["bullets"]:
            lines.append(f"• {bullet.lstrip('•- ').strip()}")


        lines.append("")  # Blank line between jobs

    return "\n".join(lines).strip()


def assemble_resume(summary: str, skills: str, experience: str, education: str = "") -> str:
    """
    Combines all enhanced resume sections into one clean final string.
    Adds section headers and spacing.
    """
    lines = []

    if summary.strip():
        lines.append("SUMMARY")
        lines.append("-------")
        lines.append(summary.strip())
        lines.append("")

    if skills.strip():
        lines.append("SKILLS")
        lines.append("------")
        lines.append(skills.strip())
        lines.append("")

    if experience.strip():
        lines.append("EXPERIENCE")
        lines.append("----------")
        lines.append(experience.strip())
        lines.append("")

    if education.strip():
        lines.append("EDUCATION")
        lines.append("---------")
        lines.append(education.strip())

    return "\n".join(lines).strip()
