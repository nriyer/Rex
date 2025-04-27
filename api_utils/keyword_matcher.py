import re
import openai
from dotenv import load_dotenv
import os
import json
from hashlib import md5
from pathlib import Path
from typing import List
from api_utils.keyword_classifier import normalize_keyword


# === STOPWORDS for filtering generic words ===
STOPWORDS = {
    "and", "or", "with", "a", "the", "in", "of", "for", "to", "on", "at", "by",
    "an", "as", "from", "is", "are", "using", "use"
}

# === Extended Stopwords for filtering weak or vague terms ===
EXTENDED_STOPWORDS = {
    "manage", "assist", "understand", "tailored", "trusting", "plans", "regularly", 
    "communicate", "individual", "circumstances", "overall", "needs", "situation",
    "client", "clients", "goals", "conditions", "objectives", "requirements"
}


# === Synonyms mapping (optional normalization layer) ===
KEYWORD_SYNONYMS = {
    "power bi": "powerbi",
    "microsoft excel": "excel",
    "ms excel": "excel",
    "scikit-learn": "sklearn",
    "machine learning": "ml",
    "artificial intelligence": "ai",
}

def normalize_token(token: str) -> str:
    token = token.lower().strip()

    # Always try naive plural to singular if ends in 's'
    if token.endswith("s") and len(token) > 3:
        token = token[:-1]

    return KEYWORD_SYNONYMS.get(token, token)



# === Extract clean keywords from job description text ===
def extract_keywords(job_text: str) -> set:
    job_text = job_text.lower()
    
    # Regex: match words with at least 3+ characters (exclude numbers/symbols)
    tokens = re.findall(r"\b[a-zA-Z][a-zA-Z0-9\-]{2,}\b", job_text)

    keywords = set(
        normalize_keyword(t) for t in tokens
        if t not in STOPWORDS
        and t not in EXTENDED_STOPWORDS
        and not t.isdigit()
        and len(t) > 3
    )

    return keywords

# === GPT filter to remove irrelevant keywords ===
FILTER_CACHE_PATH = Path("filtered_keywords_cache.json")
if FILTER_CACHE_PATH.exists():
    with open(FILTER_CACHE_PATH, "r") as f:
        filter_cache = json.load(f)
else:
    filter_cache = {}

def filter_relevant_keywords(all_keywords: List[str], model="gpt-4", job_id=None, debug: bool = False) -> List[str]:
    # === Normalize and dedupe ===
    filtered_input = sorted(set(normalize_keyword(k) for k in all_keywords if len(k) > 3))
    
    # === Use job hash if no ID provided ===
    if job_id is None:
        job_id = md5(" ".join(filtered_input).encode()).hexdigest()

    # === Cache hit ===
    if job_id in filter_cache:
        return filter_cache[job_id]

    prompt = (
        "You are helping clean a list of job posting keywords for a resume enhancement tool.\n"
        "The list below was extracted from a job description. It may apply to ANY kind of job: "
        "\"data analyst, warehouse worker, psychologist, etc.\"\n\n"
        f"List:\n{filtered_input}\n\n"
        "🎯 Your goal is to keep ONLY ~40 keywords that are:\n"
        "- hard skills (e.g., Python, Excel, SQL, CPR, logistics)\n"
        "- tools or platforms (e.g., Salesforce, Tableau)\n"
        "- certifications or licenses (e.g., PMP, CPA, RN, CDL)\n"
        "- acronyms or capitalized technical terms (e.g., GAAP, HRIS, HIPAA)\n"
        "- domain-specific phrases (e.g., inventory control, behavioral therapy)\n\n"
        "🚫 Strictly REMOVE anything that is:\n"
        "- a vague verb or adjective (e.g., tailored, proactive)\n"
        "- filler or connector language (e.g., regularly, effectively)\n\n"
        "✅ Always include terms that refer to credentials:\n"
        "- Degrees like 'bachelor', 'bachelor’s', 'masters', 'mba', 'phd', 'degree'\n"
        "- Certifications like 'pmp', 'cpa', 'cissp', etc.\n"
        "❗️These must be retained even if they appear only once in the list.\n\n"
        "✅ Return only the cleaned list as a valid Python list of lowercase strings.\n"
        "No explanations. Format as a Python list (e.g., ['python', 'sql', 'excel'])."
    )


    load_dotenv()
    

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )

    try:
        filtered = eval(response.choices[0].message.content.strip())
        filtered = [k.lower().strip() for k in filtered]

        if debug:
            print(f"\n🧠 Filtered Keywords:\n{filtered}\n")
            removed = set(filtered_input) - set(filtered)
            print(f"❌ Removed Keywords:\n{sorted(removed)}\n")

        # ✅ Cache the result
        filter_cache[job_id] = filtered
        with open(FILTER_CACHE_PATH, "w") as f:
            json.dump(filter_cache, f, indent=2)

        return filtered

    except Exception as e:
        print(f"[GPT keyword filter error] {e}")
        return all_keywords
    
# === Match GPT-filtered keywords against full resume text ===
def compute_keyword_match(resume_text: str, job_text: str, model="gpt-4") -> dict:
    raw_keywords = extract_keywords(job_text)
    job_keywords = filter_relevant_keywords(raw_keywords, model=model)
    resume_text_lower = resume_text.lower()

    matched = {kw for kw in job_keywords if kw in resume_text_lower}
    missing = set(job_keywords) - matched
    match_pct = round(len(matched) / len(job_keywords) * 100, 1) if job_keywords else 0.0

    return {
        "match_percent": match_pct,
        "matched_keywords": sorted(matched),
        "missing_keywords": sorted(missing),
        "all_keywords": sorted(job_keywords),
    }






