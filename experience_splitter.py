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
    current_chunk = []
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
        elif re.search(r"(Analyst|Engineer|Manager|Director|Accountant)", line) and DATE_RANGE_PATTERN.search(line):
            is_job_title = True
            
        # Method 3: Look for job titles that are short standalone lines
        elif any(title in line for title in ["Analyst", "Engineer", "Manager", "Accountant"]) and len(line) < 70:
            # Make sure it's not a bullet point
            if not line.startswith(('•', '-', '*')):
                is_job_title = True

        # Method 4: Look for Fund Accountant style job entries
        elif "Fund Accountant" in line or "Accounting Analyst" in line:
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
        
        # Check for department info as separate
        dept_match = re.search(r'\b(Department of [A-Za-z]+|Dept\.? of [A-Za-z]+)\b', title)
        if dept_match:
            dept_info = dept_match.group(0)
            # Don't remove it from title yet, just note it for company name
            if not company:
                company = dept_info
                
        # Special handling for "at SAMHSA" or similar organization formats
        at_match = re.search(r'\bat\s+([A-Z][A-Za-z0-9\s,]+)(?:\s+Department|\s*$)', title)
        if at_match:
            org_name = at_match.group(1).strip()
            company = org_name
            if dept_match:
                company += f", {dept_info}"
            # Remove the "at Org" portion from title
            title = title.replace(at_match.group(0), "").strip()
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
    
    # Third pass: Handle specific "at Company" format in title if no company found yet
    if not company:
        # Look for "at Company" directly in the title (more specific match)
        at_match = re.search(r'\bat\s+([A-Z][A-Za-z0-9\s&,\.-]+)(?:\s|$)', title)
        if at_match:
            company = at_match.group(1).strip()
            # Remove the "at Company" from title
            title = title.replace(f"at {company}", "").strip()
    
    # Final cleanup for title
    # Remove any trailing "at" that might be left
    title = re.sub(r'\s+at\s*$', '', title).strip()
    
    # Process bullet points (only start from bullets_start index)
    current_bullet = ""
    
    for line in lines[bullets_start:]:
        line_content = line.strip()
        
        # Skip empty lines
        if not line_content:
            continue
            
        # Skip if it's potentially a new job title
        if (re.match(r"^[□■◆♦📌]", line_content) or 
            (JOB_TITLE_PATTERN.search(line_content) and len(line_content) < 60)):
            break
            
        # Check if line starts with bullet character
        if re.match(r"^[•\-\*]", line_content):
            # If we have a previous bullet, save it before starting new one
            if current_bullet:
                bullets.append(current_bullet.strip())
            # Start new bullet with cleaned content (remove leading bullet)
            current_bullet = re.sub(r"^[•\-\*]\s*", "", line_content)
        else:
            # If no current bullet, start one; otherwise append to existing
            if not current_bullet:
                current_bullet = line_content
            else:
                current_bullet += " " + line_content

    # Add the last bullet if there is one
    if current_bullet:
        bullets.append(current_bullet.strip())

    # Final cleanup - ensure no duplicated company names in title
    if company and company in title:
        title = title.replace(company, "").strip()

    return {
        "company": company,
        "title": title,
        "date_range": date_range,
        "bullets": bullets
    }
