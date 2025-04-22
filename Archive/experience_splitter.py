import re
print("🔥 experience_splitter.py LOADED")


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
    STOP_KEYWORDS = ["summary", "projects", "Education", "skills", "education and certifications", "certifications"]

    lines = text.strip().split("\n")
    job_chunks = []
    current_chunk = []
    job_start_indices = []

    # First pass: identify all potential job start lines
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        if line.startswith(("•", "-", "–", "*", "·", "□", "■", "◆", "♦", "📌")):
            continue  # 🚫 never treat bullets as job header lines


        # Skip bad header lines (contact, email, phone, address)
        if re.search(r"@|http|\.com|\d{3}[-.\s]?\d{3}[-.\s]?\d{4}", line.lower()):
            continue
        
        # Skip false header matches
        if any(stop in line.lower() for stop in STOP_KEYWORDS):
            print(f"🚫 Skipping stopword line: {line}")
            continue  # ✅ just skip, NOT break


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

        # Method 5: Handle formats where job title + date is one line, company is next
        elif i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if (
                re.search(r"(Analyst|Engineer|Manager|Accountant)", line) and
                DATE_RANGE_PATTERN.search(line) and
                not any(skip in next_line.lower() for skip in STOP_KEYWORDS) and
                len(next_line) < 100 and
                not next_line.startswith(("•", "-", "*"))
            ):
                is_job_title = True

        # Method 6: Title line followed by company + date
        elif i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if (
                any(title in line for title in ["Analyst", "Engineer", "Manager", "Accountant"])
                and DATE_RANGE_PATTERN.search(next_line)
                and not next_line.startswith(("•", "-", "*"))
                and not any(stop in next_line.lower() for stop in STOP_KEYWORDS)
            ):
                print(f"📌 Detected job title on line {i}, company/date on line {i+1}")
                is_job_title = True



    # If no job starts found, return the entire text as one job
    if not job_start_indices:
        return [text]

    # Second pass: Process each job chunk
    for i in range(len(job_start_indices)):
        start_idx = job_start_indices[i]
        end_idx = job_start_indices[i + 1] if i < len(job_start_indices) - 1 else len(lines)

        # Slice out job lines
        # Include potential company name on the line before or after
        job_lines = []

        # 1. Include line above (company above header)
        if start_idx > 0:
            prev_line = lines[start_idx - 1].strip()
            if (
                prev_line
                and not prev_line.startswith(("•", "-", "*", "·", "□", "■", "◆", "♦", "📌"))
                and not DATE_RANGE_PATTERN.search(prev_line)
                and not any(title in prev_line for title in ["Analyst", "Engineer", "Manager", "Accountant", "Developer", "Scientist", "Consultant"])
                and not any(stop in prev_line.lower() for stop in STOP_KEYWORDS)
                and not any(char in prev_line for char in ["@", ".", "www", "http"])
                and not any(char.isdigit() for char in prev_line)
                and len(prev_line.split()) <= 10
                and prev_line[0].isupper()
            ):

                print(f"📌 Pulling company from line above: {prev_line}")
                job_lines.append(prev_line)

        # 2. Add header line and rest of chunk
        job_lines.extend(lines[start_idx:end_idx])


        # Truncate the job if a STOP keyword appears mid-chunk
        truncated_lines = []
        for line in job_lines:
            if any(stop in line.lower() for stop in STOP_KEYWORDS):
                print(f"🚫 Truncating job at STOP line: {line}")
                break
            truncated_lines.append(line)

        job_chunk = "\n".join(truncated_lines).strip()

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
