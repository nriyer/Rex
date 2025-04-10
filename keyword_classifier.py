# keyword_classifier.py
import json
from pathlib import Path

from typing import List, Dict

# Persistent GPT classification cache
CACHE_PATH = Path("classified_keywords_cache.json")
if CACHE_PATH.exists():
    with open(CACHE_PATH, "r") as f:
        keyword_cache = json.load(f)
else:
    keyword_cache = {}


# === Normalize fuzzy keyword variants ===
def normalize_keyword(keyword: str) -> str:
    keyword = keyword.lower().strip()
    
    # Common synonyms or alternate forms
    synonyms = {
        "ms excel": "excel",
        "microsoft excel": "excel",
        "excel spreadsheet": "excel",
        "google sheets": "excel",
        "microsoft office": "ms office",
        "ms office": "ms office",
        "powerbi": "power bi",
        "scikit-learn": "sklearn",
        "machine learning": "ml",
        "artificial intelligence": "ai",
        "salesforce crm": "salesforce",
    }
    
    # Strip plural if base word ends in 's' and singular form is a real word
    if keyword.endswith("s") and len(keyword) > 4:
        keyword = keyword[:-1]

    return synonyms.get(keyword, keyword)


# === Keyword Classification Categories ===
CATEGORIES = {
    "tool_platform": [
        "sql", "excel", "power bi", "tableau", "python", "r", "sas", "vba",
        "jira", "snowflake", "oracle", "db2", "mysql", "postgresql", "github",
        "git", "airflow", "databricks", "spark", "tensorflow", "pytorch", "keras",
        "sklearn", "docker", "kubernetes", "linux", "windows", "macos", "bash",
        "shell scripting", "nosql", "mongodb", "hadoop", "aws", "azure", "gcp",
        "bigquery", "looker", "powerapps", "sharepoint", "ms office", "access",
        "netsuite", "sap", "crm", "salesforce", "programming", "tools",
        "dashboard", "dashboards", "hris"
    ],

    "certification_license": [
        "cpa", "pmp", "cfa", "mba", "phd", "bachelor", "bachelor’s", "master",
        "msc", "series 7", "series 63", "series 66", "scrum master", "csme",
        "six sigma", "green belt", "black belt", "certification", "certifications",
        "license", "licenses", "licensed", "rn", "lcsw", "pe", "ccna", "ccnp",
        "aws certified", "gcp certified", "azure certified",
        "google analytics certified", "data analyst associate", "security+",
        "cissp", "cisa", "degree"
    ],

    "domain_knowledge": [
        "gaap", "hipaa", "sox", "fiduciary", "estate", "retirement", "401k",
        "insurance", "finance", "financial", "accounting", "budgeting",
        "forecasting", "marketing", "ecommerce", "supply chain", "logistics",
        "warehouse", "distribution", "inventory", "hr", "recruiting",
        "behavioral therapy", "counseling", "mental health", "compliance",
        "legal", "tax", "audit", "audits", "regulatory", "grants", "clinical",
        "healthcare", "education", "k12", "higher ed", "real estate", "mortgage",
        "data privacy", "gdpr", "cybersecurity", "operations", "investment",
        "investments", "planning", "management", "business", "strategies",
        "risk", "development", "regulations", "reporting", "statistics",
        "analyst", "metrics", "data", "visualization", "data-driven",
        "resources", "analysis", "analytics"
    ],

    "soft_skill": [
        "communication", "teamwork", "leadership", "collaboration", "adaptability",
        "analytical", "organizational", "problem-solving", "attention to detail",
        "time management", "conflict resolution", "presentation",
        "critical thinking", "creativity", "interpersonal", "decision making",
        "multitasking", "work ethic", "initiative", "proactive", "dependability",
        "flexibility"
    ]
}


import os
from openai import OpenAI
from dotenv import load_dotenv

# Load key for fallback GPT use
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def fallback_classify_with_gpt(keyword: str, model="gpt-4") -> str:
    norm_kw = keyword.lower().strip()
    
    if norm_kw in keyword_cache:
        return keyword_cache[norm_kw]
    
    prompt = (
        f"Classify the term '{keyword}' into one of the following categories:\n"
        "1. tool_platform\n"
        "2. certification_license\n"
        "3. domain_knowledge\n"
        "4. soft_skill\n\n"
        "Respond with only the category name (e.g., 'tool_platform')."
        "Use expert professional judgement to best categorize keyword if in 'other'"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,

        )
        label = response.choices[0].message.content.strip().lower()
        label = label.replace(".", "").replace("\"", "").replace("'", "").strip()

        # Force fallback to 'other' if it doesn't match any known category
        if label not in CATEGORIES:
            print(f"[Fallback Warning] Unexpected GPT label: '{label}' → defaulting to 'other'")
            label = "other"
        
        keyword_cache[norm_kw] = label
        with open(CACHE_PATH, "w") as f:
            json.dump(keyword_cache, f, indent=2)

        return label
    
    except Exception as e:
        print(f"[GPT fallback error] {e}")
        return "other"

def classify_keywords(keywords: List[str]) -> Dict[str, List[str]]:
    result = {
        "tool_platform": [],
        "certification_license": [],
        "domain_knowledge": [],
        "soft_skill": [],
        "other": []
    }

    for kw in keywords:
        norm_kw = normalize_keyword(kw)

        matched = False
        for category, terms in CATEGORIES.items():
            if norm_kw in terms:
                result[category].append(kw)
                matched = True
                break

        if not matched:
            gpt_category = fallback_classify_with_gpt(norm_kw)
            print(f"[GPT fallback] '{kw}' → {gpt_category}")  # 🔍 Optional debug log
            if gpt_category in result:
                result[gpt_category].append(kw)
            else:
                result["other"].append(kw)

    return result
