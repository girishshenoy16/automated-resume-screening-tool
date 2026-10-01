"""
Automated unit tests for extreme edge cases, anomalous inputs, and fault tolerance (TASK-21).
Validates empty documents, zero matching skills, 100% matching skills, zero JD skills,
Unicode/emoji content, large documents, and single-candidate workflows.
"""

from pathlib import Path
import pytest

from src.cleaner import clean_text
from src.skill_extractor import extract_skills, compare_skills, build_skill_pattern
from src.matcher import compute_tfidf_similarity
from src.reporter import compute_composite_score
from src import config

def test_zero_matching_skills_candidate():
    """Verify candidate with zero overlapping skills scores 0.0% on skill match."""
    jd_skills = ["Python", "SQL", "Docker", "FastAPI", "Pandas", "PostgreSQL", "Git", "Kubernetes"]
    candidate_skills = ["AutoCAD", "Thermodynamics", "HVAC", "SolidWorks"]

    comp = compare_skills(candidate_skills, jd_skills)
    assert comp["matched_skills"] == []
    assert len(comp["missing_skills"]) == 8
    assert comp["skill_match_ratio"] == 0.0
    assert comp["skill_match_percentage"] == 0.0

    # Composite score with 0% skill match and minimal TF-IDF (e.g. 3.0%)
    score = compute_composite_score(3.0, comp["skill_match_percentage"])
    assert score == round(0.40 * 3.0, 2)  # 1.20%
    signal, label = config.get_screening_signal(score)
    assert signal == config.SIGNAL_LOW_MATCH
    assert label == config.LABEL_LOW_MATCH == "Low Match"

def test_perfect_matching_skills_candidate():
    """Verify candidate with 100% skill coverage achieves top tier."""
    jd_skills = ["Python", "SQL", "Docker", "FastAPI", "Pandas", "PostgreSQL", "Git", "Kubernetes"]
    candidate_skills = ["Python", "SQL", "Docker", "FastAPI", "Pandas", "PostgreSQL", "Git", "Kubernetes", "Redis", "CI/CD"]

    comp = compare_skills(candidate_skills, jd_skills)
    assert len(comp["matched_skills"]) == 8
    assert comp["missing_skills"] == []
    assert comp["skill_match_percentage"] == 100.0

    # Composite score with 100% skill match and moderate TF-IDF (e.g. 35.0%)
    score = compute_composite_score(35.0, comp["skill_match_percentage"])
    assert score == round((0.40 * 35.0) + (0.60 * 100.0), 2)  # 14.0 + 60.0 = 74.0%
    signal, label = config.get_screening_signal(score)
    assert signal == config.SIGNAL_SHORTLIST
    assert label == "High Match"

def test_zero_jd_skills_guard():
    """Verify system safely guards against zero required skills in JD without dividing by zero."""
    candidate_skills = ["Python", "SQL"]
    comp = compare_skills(candidate_skills, [])
    assert comp["skill_match_ratio"] == 0.0
    assert comp["skill_match_percentage"] == 0.0
    assert comp["matched_skills"] == []
    assert comp["missing_skills"] == []

def test_unicode_emojis_and_non_ascii_resumes():
    """Verify resumes with international characters and emojis are cleaned without crashing."""
    raw = "Senior Software Ingénieur 🚀 | Python 🐍 | FastAPI & Docker 📦 | Développeur backend à Paris"
    cleaned = clean_text(raw)
    assert "python" in cleaned
    assert "fastapi" in cleaned
    assert "docker" in cleaned

    skills = extract_skills(cleaned)
    assert "Python" in skills["technical_skills"]
    assert "FastAPI" in skills["technical_skills"]
    assert "Docker" in skills["technical_skills"]

def test_extremely_large_document_handling():
    """Verify pipeline handles very large document text (stress test)."""
    # 20,000 words repetition
    paragraph = "Senior Python engineer building high performance backend microservices using FastAPI, Docker, and PostgreSQL. "
    large_text = paragraph * 1000

    cleaned = clean_text(large_text)
    assert len(cleaned) > 50_000

    skills = extract_skills(cleaned)
    assert "Python" in skills["technical_skills"]
    assert "FastAPI" in skills["technical_skills"]

    # TF-IDF should process without memory error
    tfidf_res = compute_tfidf_similarity(cleaned, paragraph)
    assert tfidf_res["tfidf_percentage"] > 80.0

def test_empty_document_end_to_end():
    """Verify empty document text flows through pipeline safely returning 0 scores."""
    cleaned = clean_text("")
    assert cleaned == ""

    skills = extract_skills(cleaned)
    assert skills["technical_skills"] == []
    assert skills["soft_skills"] == []

    comp = compare_skills(skills["technical_skills"], ["Python", "SQL"])
    assert comp["skill_match_percentage"] == 0.0

    tfidf_res = compute_tfidf_similarity(cleaned, "Python SQL Docker")
    assert tfidf_res["tfidf_percentage"] == 0.0

    score = compute_composite_score(tfidf_res["tfidf_percentage"], comp["skill_match_percentage"])
    assert score == 0.0
    signal, label = config.get_screening_signal(score)
    assert signal == "LOW MATCH"
    assert label == "Low Match"
