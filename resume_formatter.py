# === resume_formatter.py ===

from typing import List


def format_experience_section(jobs: List[dict]) -> str:
    """
    Formats a list of enhanced job dicts into a clean, copy-pasteable
    'Experience' section string with proper bullets and spacing.
    """
    lines = []

    for i, job in enumerate(jobs):
        # Extract job components
        title = job.get('title', '').strip()
        company = job.get('company', '').strip()
        date_range = job.get('date_range', '').strip()
        
        # Format job title and date (first line)
        # Use diamond bullet and ensure proper spacing
        if date_range:
            job_header = f"◆ {title} {date_range}"
        else:
            job_header = f"◆ {title}"
        
        lines.append(job_header)
        
        # Add company as separate line when available
        if company:
            lines.append(company)
        
        # Format bullet points with appropriate spacing
        bullet_lines = []
        for bullet in job.get("bullets", []):
            # Clean up bullet formatting to ensure consistent bullets
            # Remove any existing bullets (•-*◆) at the start
            clean_bullet = bullet.lstrip('•-*□■◆♦📌 \t').strip()
            
            # Skip empty bullets
            if not clean_bullet:
                continue
                
            # Add bullet with proper formatting
            bullet_lines.append(f"• {clean_bullet}")
        
        # Add bullets to main lines
        if bullet_lines:
            lines.extend(bullet_lines)
        
        # Add blank line between job entries if not the last job
        if i < len(jobs) - 1:
            lines.append("")

    result = "\n".join(lines).strip()
    return result


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
