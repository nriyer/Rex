import re

# === Constants ===

DATE_PATTERN = re.compile(
    r"((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+[''']?\d{2,4})|"
    r"(\d{4}\s*[-–—]\s*(Present|\d{2,4}))",
    flags=re.IGNORECASE
)

STOP_KEYWORDS = ["summary", "projects", "education", "skills", "certifications"]

# Modified to detect job titles like "Budget Analyst"
JOB_TITLE_PATTERN = re.compile(
    r"(□\s*)?(\b(Analyst|Engineer|Manager|Director|Specialist|Associate|Consultant|Developer|Accountant)\b)",
    flags=re.IGNORECASE
)

# === Split Experience Section ===

def split_experience_section(text):
    lines = text.strip().split("\n")
    job_chunks = []
    current_chunk = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Check for the specific format with square bullet and job title
        title_match = JOB_TITLE_PATTERN.search(line)
        date_match = DATE_PATTERN.search(line)

        # Detect start of job entry - either by date pattern or by job title
        is_new_job = False
        
        if title_match and line.startswith('□'):
            # Specific format with square bullet at start of line
            is_new_job = True
        elif title_match and len(line) < 60 and any(word in line for word in ['Analyst', 'Engineer', 'Manager', 'Accountant']):
            # Look for short lines with job titles
            is_new_job = True
        elif date_match and " - " in line and any(year in line for year in ['2020', '2021', '2022', '2023', '2024', '2025']):
            # Date range format like "December 2023 - March 2025"
            is_new_job = True

        if is_new_job:
            if current_chunk:
                # Only save if it has more than 1 line (skip floating company-only chunks)
                if len(current_chunk) > 1:
                    job_chunks.append("\n".join(current_chunk).strip())
                current_chunk = []

        current_chunk.append(line)
        i += 1

    if current_chunk:
        job_chunks.append("\n".join(current_chunk).strip())

    return job_chunks

# === Parse Individual Job Entry ===

def parse_job_entry(chunk):
    """
    Extracts structured fields from a job chunk using:
    - title + date line
    - company line above
    - multi-line bullets
    Handles both traditional formats and the format with job title on first line
    and company/date on second line.
    """
    lines = chunk.strip().split("\n")
    
    # Initialize default values
    company = ""
    title = ""
    date_range = ""
    bullets = []
    
    # If there are less than 2 lines, return what we have
    if len(lines) < 2:
        return {
            "company": "",
            "title": lines[0] if lines else "",
            "date_range": "",
            "bullets": []
        }
    
    # First, check if this is the □ format with job title on line 1
    # and company/date on line 2
    first_line = lines[0].strip()
    second_line = lines[1].strip()
    
    # Check for square bullet or job title on first line
    if first_line.startswith("□") or JOB_TITLE_PATTERN.search(first_line):
        # First line is the job title
        title = first_line.lstrip("□ ")
        
        # Second line may contain company and/or date
        date_match = DATE_PATTERN.search(second_line)
        if date_match:
            date_range = second_line[date_match.start():].strip()
            company = second_line[:date_match.start()].strip()
        else:
            # If no date on second line, the whole line is the company
            company = second_line
        
        # Bullets start from third line
        bullets_start = 2
    else:
        # Try traditional format with date on a line
        date_line_idx = None
        date_match = None

        for i, line in enumerate(lines):
            match = DATE_PATTERN.search(line)
            if match:
                date_line_idx = i
                date_match = match
                break

        if date_line_idx is None:
            # No date found, treat first line as title, second as company
            title = lines[0]
            company = lines[1] if len(lines) > 1 else ""
            bullets_start = 2
        else:
            # Found date, use traditional parsing
            date_line = lines[date_line_idx].strip()
            date_range = date_line[date_match.start():].strip()
            title = date_line[:date_match.start()].strip()
            company = lines[date_line_idx - 1].strip() if date_line_idx >= 1 else ""
            bullets_start = date_line_idx + 1
    
    # Process bullet points
    current_bullet = ""
    
    for line in lines[bullets_start:]:
        striped = line.strip()
        
        # Skip if it's potentially a new job title
        if (striped.startswith("□") or 
            (JOB_TITLE_PATTERN.search(striped) and len(striped) < 60)):
            break
            
        if striped.startswith(("•", "-", "·")):
            if current_bullet:
                bullets.append(current_bullet.strip())
            current_bullet = striped
        else:
            if not current_bullet:
                current_bullet = striped
            else:
                current_bullet += " " + striped

    if current_bullet:
        bullets.append(current_bullet.strip())

    return {
        "company": company,
        "title": title,
        "date_range": date_range,
        "bullets": bullets
    }
