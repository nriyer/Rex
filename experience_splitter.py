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
    Splits the experience section into job chunks in a stable, format-flexible way.
    It groups lines into chunks where each chunk starts with a non-bullet (header line),
    and all following bullet lines are grouped until the next header appears.
    """
    lines = text.strip().split("\n")
    job_chunks = []
    current_chunk = []

    def is_bullet(line):
        return line.strip().startswith(('•', '-', '*', '·', '–'))

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if not is_bullet(stripped):
            # If current_chunk already has content, this marks the start of a new job
            if current_chunk:
                job_chunks.append("\n".join(current_chunk).strip())
                current_chunk = []
        current_chunk.append(stripped)

    if current_chunk:
        job_chunks.append("\n".join(current_chunk).strip())

    return job_chunks



    # # First pass: identify all potential job start lines
    # for i, line in enumerate(lines):
    #     line = line.strip()
    #     if not line:
    #         continue

    #     # Various methods to detect job title lines
    #     is_job_title = False
        
    #     # Method 1: Look for lines starting with special bullets (□■◆♦📌)
    #     if re.match(r"^[□■◆♦📌]", line):
    #         is_job_title = True
            
    #     # Method 2: Look for job titles with dates (Budget Analyst Mar '21 - Dec '23)
    #     elif re.search(r"(Analyst|Engineer|Manager|Director|Accountant)", line) and DATE_RANGE_PATTERN.search(line):
    #         is_job_title = True
            
    #     # Method 3: Look for job titles that are short standalone lines
    #     elif any(title in line for title in ["Analyst", "Engineer", "Manager", "Accountant"]) and len(line) < 70:
    #         # Make sure it's not a bullet point
    #         if not line.startswith(('•', '-', '*')):
    #             is_job_title = True

    #     # Method 4: Look for Fund Accountant style job entries
    #     elif "Fund Accountant" in line or "Accounting Analyst" in line:
    #         is_job_title = True

    #     if is_job_title:
    #         job_start_indices.append(i)

    # # If no job starts found, return the entire text as one job
    # if not job_start_indices:
    #     return [text]

    # # Second pass: Process each job chunk
    # for i in range(len(job_start_indices)):
    #     start_idx = job_start_indices[i]
    #     # If this is the last job, include all remaining lines
    #     if i == len(job_start_indices) - 1:
    #         end_idx = len(lines)
    #     else:
    #         end_idx = job_start_indices[i + 1]
        
    #     # Get all lines for this job
    #     job_lines = lines[start_idx:end_idx]
    #     # Create a string from these lines
    #     job_chunk = "\n".join(job_lines).strip()
        
    #     # Add the job chunk if it's not empty
    #     if job_chunk:
    #         job_chunks.append(job_chunk)

    # return job_chunks

# === Parse Individual Job Entry ===

def parse_job_entry(chunk):
    """
    Extracts structured job data from a text chunk, handling various resume formats.
    
    Supported header formats:
    - Line 1: Company | Line 2: Role and Date
    - Line 1: Role | Line 2: Company and Date
    - Line 1: Role | Line 2: Company | Line 3: Date
    - Line 1: Company | Line 2: Role | Line 3: Date
    - Line 1: Date | Line 2: Role | Line 3: Company
    - Line 1: Date | Line 2: Company | Line 3: Role
    - Line 1: Role and Date | Line 2: Company
    - Line 1: Company and Date | Line 2: Role
    - Line 1: All-in-one line → "Budget Analyst at SAMHSA Jan 2023 – Mar 2025"
    
    Returns:
        dict: Structured job information with title, company, date_range, and bullets
    """
    lines = chunk.strip().split("\n")
    
    # Initialize with empty values
    job_data = {
        "title": "",
        "company": "",
        "date_range": "",
        "bullets": []
    }
    
    # Skip empty chunks
    if not lines:
        return job_data
    
    # PHASE 1: Extract the header components (first 1-3 lines)
    # We'll classify each line and then reconstruct the job metadata
    header_lines = []
    
    # Get the first 1-3 non-empty lines that don't look like bullets
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Skip if it's a bullet point
        if re.match(r'^[•\-\*◦◈◇➢➣➤►→⁃]', line):
            break
            
        header_lines.append(line)
        if len(header_lines) >= 3:
            break
    
    # Label each header line as title, company, or date
    line_types = []
    
    for line in header_lines:
        # Check for date pattern
        date_match = re.search(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+(?:\'|'|'|20)\d{2}\s*[-–—]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|Present|\d{4})', line, re.IGNORECASE)
        year_date_match = re.search(r'\b(?:19|20)\d{2}\s*[-–—]\s*(?:(?:19|20)\d{2}|Present)', line)
        
        # Check for job title indicators
        title_match = re.search(r'\b(?:Analyst|Engineer|Developer|Manager|Director|Specialist|Coordinator|Consultant|Administrator|Associate|Assistant|Accountant|Lead|Senior|Budget|Fund|Supervisor|Representative)\b', line, re.IGNORECASE)
        
        # Check for company indicators (organizations often in ALL CAPS or have Inc./LLC/etc.)
        company_indicators = re.search(r'(?:Inc\.|LLC|Ltd\.|\bCorp\.|\bCompany\b|Group|Associates|\bLLP\b)', line) or line.isupper() or (len(line.split()) <= 3 and line[0].isupper())
        
        # "at Company" pattern
        at_company_match = re.search(r'\bat\s+([A-Z][A-Za-z0-9\s&,\.-]+)', line)
        
        # Labeling logic - prioritized by confidence
        if date_match or year_date_match:
            if "at" in line and title_match and at_company_match:
                # This is an all-in-one line: "Budget Analyst at SAMHSA Jan 2023 – Mar 2025"
                line_types.append(("all", line))
            else:
                # Extract just the date part
                date_text = date_match.group(0) if date_match else year_date_match.group(0)
                line_types.append(("date", date_text))
                
                # If there's more to this line, it might contain title or company
                remaining = line.replace(date_text, "").strip()
                if remaining and title_match:
                    line_types.append(("title", remaining))
                elif remaining and (company_indicators or at_company_match):
                    line_types.append(("company", remaining))
        elif title_match:
            # Second highest confidence: job title
            line_types.append(("title", line))
        elif company_indicators or at_company_match or re.match(r'^[A-Z][A-Za-z\s]+$', line):
            # Company names are often capitalized or have company indicators
            line_types.append(("company", line))
        else:
            # Fallback: assign based on position
            if not any(t[0] == "title" for t in line_types):
                line_types.append(("title", line))
            elif not any(t[0] == "company" for t in line_types):
                line_types.append(("company", line))
            else:
                line_types.append(("unknown", line))
    
    # PHASE 2: Extract structured data from the classified lines
    # Process "all-in-one" entries first
    all_in_one = [item for item in line_types if item[0] == "all"]
    if all_in_one:
        line = all_in_one[0][1]
        
        # Extract date
        date_match = re.search(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+(?:\'|'|'|20)\d{2}\s*[-–—]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|Present|\d{4})', line, re.IGNORECASE)
        if date_match:
            job_data["date_range"] = date_match.group(0)
            line = line.replace(job_data["date_range"], "").strip()
        
        # Extract company if there's an "at Company" pattern
        at_company_match = re.search(r'\bat\s+([A-Z][A-Za-z0-9\s&,\.-]+)', line)
        if at_company_match:
            job_data["company"] = at_company_match.group(1).strip()
            line = line.replace(f"at {job_data['company']}", "").strip()
        
        # What remains is likely the title
        job_data["title"] = line
    else:
        # Process individual type-classified lines
        for line_type, text in line_types:
            if line_type == "title" and not job_data["title"]:
                job_data["title"] = text
            elif line_type == "company" and not job_data["company"]:
                # Clean up any "at" prefixes
                if text.startswith("at "):
                    text = text[3:]
                job_data["company"] = text
            elif line_type == "date" and not job_data["date_range"]:
                job_data["date_range"] = text
    
    # PHASE 3: Extract and clean bullet points with proper limits
    bullets_start_idx = len(header_lines)
    bullets = []
    
    # Define valid bullet point characters
    valid_bullet_chars = r'[•\-\*◦◈◇➢➣➤►→⁃]'
    
    # Define patterns that indicate a new job header
    new_job_pattern = re.compile(
        r'^[□■◆♦📌]|'                                                # Heading bullets
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}|'  # Date patterns
        r'\b\d{4}\s*[-–—]\s*(?:Present|\d{4})\b',                  # Year ranges
        re.IGNORECASE
    )
    
    job_title_pattern = re.compile(
        r'\b(?:Analyst|Engineer|Developer|Manager|Director|Specialist|Associate|Consultant)\b', 
        re.IGNORECASE
    )
    
    for i in range(bullets_start_idx, len(lines)):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Check if this might be the start of a new job entry
        if (new_job_pattern.search(line) or 
            (line.istitle() and not re.match(valid_bullet_chars, line)) or
            (line.isupper() and len(line) < 30) or
            (job_title_pattern.search(line) and len(line) < 60)):
            break
        
        # Only process lines that start with valid bullet characters
        if re.match(f'^{valid_bullet_chars}', line):
            # Remove the bullet character and add to list
            clean_bullet = re.sub(f'^{valid_bullet_chars}\s*', '', line).strip()
            
            # Only add bullet points that are meaningful (not too short or incomplete)
            if len(clean_bullet) > 10 and not clean_bullet.endswith(('by', 'for', 'to', 'of', 'the', 'and')):
                bullets.append(clean_bullet)
                
                # Cap bullets to maximum 6
                if len(bullets) >= 6:
                    break
    
    job_data["bullets"] = bullets
    
    # Final clean-up for title and company
    # Remove any trailing "at" from title
    job_data["title"] = re.sub(r'\s+at\s*$', '', job_data["title"]).strip()
    
    # Remove any date patterns from title and company
    date_pattern = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(?:\'|'|'|20)?\d{2}\s*[-–—]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Present|(?:\'|'|'|20)?\d{2})'
    job_data["title"] = re.sub(date_pattern, '', job_data["title"], flags=re.IGNORECASE).strip()
    job_data["company"] = re.sub(date_pattern, '', job_data["company"], flags=re.IGNORECASE).strip()
    
    # Remove company name from title if it appears there
    if job_data["company"] and job_data["company"] in job_data["title"]:
        job_data["title"] = job_data["title"].replace(job_data["company"], "").strip()
    
    # Special case handling: if no title was found but there are header lines
    if not job_data["title"] and header_lines:
        # Use first line as title if nothing better
        job_data["title"] = header_lines[0]
        
    return job_data