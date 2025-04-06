import re

# === Constants ===

DATE_PATTERN = re.compile(
    r"((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+[‘’']?\d{2,4})|"
    r"(\d{4}\s*[-–—]\s*(Present|\d{2,4}))",
    flags=re.IGNORECASE
)

STOP_KEYWORDS = ["summary", "projects", "education", "skills", "certifications"]

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

        if DATE_PATTERN.search(line):
            if current_chunk:
                # Only save if it has more than 1 line (skip floating company-only chunks)
                if len(current_chunk) > 1:
                    job_chunks.append("\n".join(current_chunk).strip())
                current_chunk = []

            # Grab 1-2 lines before date (title/company)
            if i >= 2:
                current_chunk.extend([lines[i-2].strip(), lines[i-1].strip()])
            elif i == 1:
                current_chunk.append(lines[i-1].strip())

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
    """
    lines = chunk.strip().split("\n")

    date_line_idx = None
    date_match = None

    for i, line in enumerate(lines):
        match = DATE_PATTERN.search(line)
        if match:
            date_line_idx = i
            date_match = match
            break

    if date_line_idx is None:
        return {
            "company": "",
            "title": "",
            "date_range": "",
            "bullets": lines
        }

    date_line = lines[date_line_idx].strip()
    date_range = date_line[date_match.start():].strip()
    title = date_line[:date_match.start()].strip()
    company = lines[date_line_idx - 1].strip() if date_line_idx >= 1 else ""

    bullets = []
    current_bullet = ""

    for line in lines[date_line_idx + 1:]:
        striped = line.strip()

        # === STOP if it's a likely new company name (e.g. 'FrontStream') ===
        if (
            striped and
            not striped.startswith(("•", "-", "·")) and
            len(striped.split()) <= 3 and
            striped[0].isupper() and
            not any(char in striped for char in ["@", "•", "-", "·"]) and
            striped.count(",") == 0
        ):
            break

        if striped.startswith(("•", "-", "·")):
            if current_bullet:
                bullets.append(current_bullet.strip())
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
