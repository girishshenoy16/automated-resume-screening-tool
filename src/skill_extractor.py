"""
Automated Resume Screening Tool — Boundary-Safe Skill Extractor.

Extracts technical and soft skills from document text using token-safe regular
expressions with strict word boundaries and lookaround assertions.
Computes matched and missing skill sets and calculates technical skill coverage ratios.
"""

import re
import json
from pathlib import Path
try:
    from src import config
except ImportError:
    import config

def load_skills_taxonomy(taxonomy_path: Path | str | None = None) -> dict:
    """
    Load curated technical and soft skills taxonomy from JSON.

    Args:
        taxonomy_path: Optional path to skills JSON. Defaults to config.SKILLS_FILE.

    Returns:
        dict: {"technical_skills": [...], "soft_skills": [...]}
    """
    path = Path(taxonomy_path) if taxonomy_path else config.SKILLS_FILE
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_skill_pattern(skill: str) -> re.Pattern:
    """
    Compile an exact, boundary-safe regular expression pattern for a given skill.
    Guarantees non-word tokens (C++, C#, .NET) and subwords ("Java" vs "JavaScript")
    are parsed deterministically without false positives.

    Args:
        skill: Canonical skill name.

    Returns:
        re.Pattern: Compiled case-insensitive regex.
    """
    sk = skill.lower().strip()
    if sk == "c++":
        return re.compile(r"(?<![\w\+])c\+\+(?![\w\+])", re.IGNORECASE)
    elif sk == "c#":
        return re.compile(r"(?<![\w\#])c\#(?![\w\#])", re.IGNORECASE)
    elif sk == ".net":
        return re.compile(r"(?<![\w\.])\.net(?![\w\.])", re.IGNORECASE)
    elif sk == "ci/cd":
        return re.compile(r"\bci/cd\b", re.IGNORECASE)
    elif sk == "node.js":
        return re.compile(r"\bnode\.js\b", re.IGNORECASE)
    elif " " in sk or "/" in sk or "-" in sk:
        # Multi-word or compound terms: flexible whitespace matching
        parts = [re.escape(p) for p in re.split(r"[\s\/\-]+", sk) if p]
        return re.compile(r"\b" + r"[\s\/\-]+".join(parts) + r"\b", re.IGNORECASE)
    else:
        return re.compile(r"\b" + re.escape(sk) + r"\b", re.IGNORECASE)

def extract_skills(text: str, taxonomy: dict | None = None) -> dict:
    """
    Scan text against taxonomy and extract detected technical and soft skills.

    Args:
        text: Raw or normalized document text.
        taxonomy: Optional taxonomy dictionary with 'technical_skills' and 'soft_skills'.

    Returns:
        dict: {
            "technical_skills": list[str],  # Alphabetically sorted canonical names
            "soft_skills": list[str]        # Alphabetically sorted canonical names
        }
    """
    if not taxonomy:
        taxonomy = load_skills_taxonomy()

    found_tech = []
    found_soft = []

    # Match technical skills
    for skill in taxonomy.get("technical_skills", []):
        pattern = build_skill_pattern(skill)
        if pattern.search(text):
            found_tech.append(skill)

    # Match soft skills (informational only)
    for skill in taxonomy.get("soft_skills", []):
        pattern = build_skill_pattern(skill)
        if pattern.search(text):
            found_soft.append(skill)

    return {
        "technical_skills": sorted(list(set(found_tech))),
        "soft_skills": sorted(list(set(found_soft)))
    }

def compare_skills(candidate_tech_skills: list[str], jd_tech_skills: list[str]) -> dict:
    """
    Compare candidate technical skills against target Job Description requirements.

    Args:
        candidate_tech_skills: List of detected candidate technical skills.
        jd_tech_skills: List of required JD technical skills.

    Returns:
        dict: {
            "matched_skills": list[str],     # Candidate ∩ JD
            "missing_skills": list[str],     # JD \ Candidate
            "skill_match_ratio": float,      # |Matched| / |JD| (0.0 to 1.0)
            "skill_match_percentage": float  # Ratio * 100.0 (0.0 to 100.0)
        }
    """
    cand_set = set(candidate_tech_skills)
    jd_set = set(jd_tech_skills)

    matched = sorted(list(cand_set.intersection(jd_set)))
    missing = sorted(list(jd_set.difference(cand_set)))

    total_required = len(jd_set)
    if total_required > 0:
        ratio = len(matched) / total_required
    else:
        ratio = 0.0

    percentage = round(ratio * 100.0, 2)

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_match_ratio": ratio,
        "skill_match_percentage": percentage
    }
