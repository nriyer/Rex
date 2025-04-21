import re

# === Constants ===

DATE_PATTERN = re.compile(
    r"((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+[''']?\d{2,4})|"
    r"(\d{4}\s*[-–—]\s*(Present|\d{2,4}))",
    flags=re.IGNORECASE
)

STOP_KEYWORDS = ["summary", "projects", "education", "skills", "certifications"]

# Modified to detect job titles with various bullet types including diamond (◆) and more job titles
JOB_TITLE_PATTERN = re.compile(
    r"^([□■◆♦📌]\s*)?([\w\s]+)?\b(Budget\s+)?(\w+\s+)?(Analyst|Engineer|Manager|Director|Specialist|Associate|Consultant|Developer|Accountant|Coordinator|Assistant|Accountant)\b",
    flags=re.IGNORECASE
)

# Pattern to recognize date ranges like "Dec '23 - Mar '25"
DATE_RANGE_PATTERN = re.compile(
    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[''`]?\s*\d{2}\s*[-–—]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Present)[''`]?\s*\d{0,2}",
    flags=re.IGNORECASE
)

# === Split Experience Section ===

def split_experience_section(text):
    """
    Split the experience section text into individual job chunks.
    Each job chunk starts with a job title line and continues until the next job title.
    """
    lines = text.strip().split("\n")
    job_chunks = []
    job_start_indices = []

    # First pass: identify all potential job start lines
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # Various methods to detect job title lines
        is_job_title = False

        # Method 1: Look for lines starting with special bullets (□■◆♦📌)
        if re.match(r"^[□■◆♦📌]", line):
            is_job_title = True

        # Method 2: Look for job titles with dates (Budget Analyst Mar '21 - Dec '23)
        elif re.search(JOB_TITLE_PATTERN, line) and DATE_RANGE_PATTERN.search(line):
            is_job_title = True

        # New Method: Use JOB_TITLE_PATTERN directly for title-only lines
        elif re.search(JOB_TITLE_PATTERN, line) and not line.startswith(('•', '-', '*')):
            # Look ahead and behind for job titles and dates
            if (i > 0 and (re.search(JOB_TITLE_PATTERN, lines[i-1]) or DATE_RANGE_PATTERN.search(lines[i-1]))) or \
               (i < len(lines) - 1 and (re.search(JOB_TITLE_PATTERN, lines[i+1]) or DATE_RANGE_PATTERN.search(lines[i+1]))):
                is_job_title = True

        if is_job_title:
            job_start_indices.append(i)

    # If no job starts found, return the entire text as one job
    if not job_start_indices:
        return [text]

    # Second pass: Process each job chunk
    for i in range(len(job_start_indices)):
        start_idx = job_start_indices[i]
        # If this is the last job, include all remaining lines
        if i == len(job_start_indices) - 1:
            end_idx = len(lines)
        else:
            end_idx = job_start_indices[i + 1]

        # Get all lines for this job
        job_lines = lines[start_idx:end_idx]
        # Create a string from these lines
        job_chunk = "\n".join(job_lines).strip()

        # Add the job chunk if it's not empty
        if job_chunk:
            job_chunks.append(job_chunk)

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
    
    # First pass: identify the job title line and date
    first_line = lines[0].strip()
    
    # Extract job title from first line with bullet
    if re.match(r"^[□■◆♦📌]", first_line):
        # Remove the bullet from the title
        title = re.sub(r"^[□■◆♦📌]\s*", "", first_line)
        
        # Extract date range if present in title
        date_match = DATE_RANGE_PATTERN.search(title)
        if date_match:
            date_range = date_match.group(0)
            title = title.replace(date_range, "").strip()
            
            # Check for "at Company" format
            if " at " in title:
                parts = title.split(" at ", 1)
                title = parts[0].strip()
                company = parts[1].strip()
    else:
        # Handle other formats
        title = first_line
        date_match = DATE_RANGE_PATTERN.search(title)
        if date_match:
            date_range = date_match.group(0)
            title = title.replace(date_range, "").strip()
    
    # Second pass: try to find company name if not already found
    if not company and len(lines) > 1:
        second_line = lines[1].strip()
        
        # If second line looks like a company name (not a bullet point and relatively short)
        if (not second_line.startswith(('•', '-', '*', '□', '■', '◆', '♦', '📌')) and 
            len(second_line) < 100 and 
            not DATE_PATTERN.search(second_line) and
            not JOB_TITLE_PATTERN.search(second_line)):
            
            # If it's likely to be a company name
            company = second_line
            bullets_start = 2
        else:
            bullets_start = 1
    else:
        bullets_start = 1
    
    # Third pass: Handle specific formats with "at" followed by company name
    if not company:
        # Look for "at Company" directly in the title
        at_match = re.search(r'\bat\s+(.+?)(?:\s+\d|$)', title)
        if at_match:
            company = at_match.group(1).strip()
            title = title.replace(f"at {company}", "").strip()
    
    # Final cleanup for title
    # Remove any trailing "at" that might be left
    title = re.sub(r'\s+at\s*$', '', title).strip()
    
    # Process bullet points
    current_bullet = ""
    
    for line in lines[bullets_start:]:
        striped = line.strip()
        
        # Skip if it's potentially a new job title
        if (re.match(r"^[□■◆♦📌]", striped) or 
            (JOB_TITLE_PATTERN.search(striped) and len(striped) < 60)):
            break
            
        if striped.startswith(("•", "-", "*", "·")):
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
