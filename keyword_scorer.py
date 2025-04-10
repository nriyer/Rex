from typing import List,Dict

#Define weights for each keyword category (importance in scoring)

CATEGORY_WEIGHTS = {

    "tool_platform" : 3,
    "certification_license" : 2,
    "domain_knowledge" : 2,
    "soft_skill" : 1
}

def compute_category_matches(
    classified_keywords: Dict[str, List[str]],
    matched_keywords: List[str]
) -> Dict[str,Dict[str,float]]:
    """
    Compute total and matched keyword counts per category.

    Args:
        classified_keywords: Dict of JD keywords grouped by category.
        matched_keywords: List of keywords found in resume.

    Returns:
        Dict of category → { matched, total, percent }
    """
    results = {}

    matched_set = set(k.lower().strip() for k in matched_keywords)

    for category, keywords in classified_keywords.items():
        keywords_set= set(k.lower().strip() for k in keywords)
        total = len(keywords_set)

        matched_in_category = keywords_set & matched_set
        matched = len(matched_in_category)

        percent = round((matched / total) * 100, 1) if total > 0 else 0.0

        unmatched_in_category = keywords_set - matched_in_category

        results[category] = {
            "matched": matched,
            "total": total,
            "percent": percent,
            "matched_words": sorted(matched_in_category),
            "unmatched_words": sorted(unmatched_in_category)
     }

     
    return results

def compute_weighted_score(category_stats: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """
    Apply weights to each category match and compute final overall score.

    Args:
        category_stats: Output from compute_category_matches()

    Returns:
        Dictionary with per-category weighted scores and final score.
    """
    total_weight = 0
    weighted_sum = 0
    category_scores = {}

    for category, stats in category_stats.items():
        weight = CATEGORY_WEIGHTS.get(category, 1)
        percent = stats.get("percent", 0)

        weighted_score = percent * weight
        category_scores[category] = round(weighted_score, 2)

        weighted_sum += weighted_score
        total_weight += weight

    final_score = round(weighted_sum / total_weight, 1) if total_weight > 0 else 0.0
    category_scores["final_score"] = final_score

    return category_scores

def score_keywords(
    classified_keywords: Dict[str, List[str]],
    matched_keywords: List[str]
) -> Dict[str, float]:
    """
    End-to-end scoring function that:
    1. Compares JD keywords with matched resume keywords.
    2. Applies category weights.
    3. Returns final and per-category weighted scores.
    """
    category_stats = compute_category_matches(classified_keywords, matched_keywords)
    weighted_scores = compute_weighted_score(category_stats)

     # ✅ Inserted block here:
    print("\n📊 Detailed Scoring Breakdown:")
    for category, score in weighted_scores.items():
        matched = category_stats.get(category, {}).get("matched", 0)
        total = category_stats.get(category, {}).get("total", 0)
        percent = category_stats.get(category, {}).get("percent", 0)
        weight = CATEGORY_WEIGHTS.get(category, 1.0)

        print(f"\n{category.upper()}")
        print(f"  Matched: {matched} / {total}")
        print(f"  Match %: {percent}%")
        print(f"  Weight : {weight}")
        print(f"  Score  : {score}")

        matched_words = category_stats.get(category, {}).get("matched_words", [])
        unmatched_words = category_stats.get(category, {}).get("unmatched_words", [])

        print(f"  ✅ Matched Terms   : {', '.join(matched_words) if matched_words else 'None'}")
        print(f"  ❌ Unmatched Terms : {', '.join(unmatched_words) if unmatched_words else 'None'}")

    return weighted_scores

def get_matched_keywords_by_category(
    classified_keywords: Dict[str, List[str]],
    matched_keywords: List[str]
) -> Dict[str, List[str]]:
    """
    Return which matched keywords belong to which category.
    """
    matched_set = set(k.lower().strip() for k in matched_keywords)
    categorized = {}

    for category, keywords in classified_keywords.items():
        category_keywords = set(k.lower().strip() for k in keywords)
        matches = category_keywords & matched_set
        categorized[category] = sorted(matches)

    return categorized
