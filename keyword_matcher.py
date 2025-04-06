import re
from openai import OpenAI
from dotenv import load_dotenv
import os

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
    return KEYWORD_SYNONYMS.get(token, token)

# === Extract clean keywords from job description text ===
def extract_keywords(job_text: str) -> set:
    job_text = job_text.lower()
    
    # Regex: match words with at least 3+ characters (exclude numbers/symbols)
    tokens = re.findall(r"\b[a-zA-Z][a-zA-Z0-9\-]{2,}\b", job_text)

    keywords = set(
        normalize_token(t) for t in tokens
        if t not in STOPWORDS
        and t not in EXTENDED_STOPWORDS
        and not t.isdigit()
        and len(t) > 3
    )

    return keywords

# === GPT filter to remove irrelevant keywords ===
def filter_relevant_keywords(all_keywords, model="gpt-4"):
    filtered_input = [k for k in all_keywords if len(k) > 3]

    prompt = (
        "You are helping clean a list of job posting keywords for a resume enhancement tool.\n"
        "The list below was extracted from a job description. It may apply to ANY kind of job: "
        "data analyst, warehouse worker, psychologist, etc.\n\n"
        f"List:\n{filtered_input}\n\n"
        "🎯 Your goal is to keep ONLY ~25 keywords that are:\n"
        "- hard skills (e.g., Python, Excel, SQL, CPR, logistics)\n"
        "- tools or platforms (e.g., Salesforce, Tableau)\n"
        "- certifications or licenses (e.g., PMP, CPA, RN, CDL)\n"
        "- acronyms or capitalized technical terms (e.g., GAAP, HRIS, HIPAA)\n"
        "- domain-specific phrases (e.g., inventory control, behavioral therapy)\n\n"
        "🚫 Strictly REMOVE anything that is:\n"
        "- a soft skill (e.g., communication, leadership)\n"
        "- a vague verb or adjective (e.g., tailored, understand, proactive, regular)\n"
        "- filler or connector language (e.g., regularly, continuously, effectively)\n\n"
        "✅ Return only the cleaned list as a valid Python list of lowercase strings.\n"
        "No explanations. Format as a Python list (e.g., ['python', 'sql', 'excel'])."
    )

    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    try:
        filtered = eval(response.choices[0].message.content.strip())
        return [k.lower().strip() for k in filtered]
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






