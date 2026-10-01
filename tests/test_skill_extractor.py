"""
Automated unit tests for boundary-safe skill extraction engine (TASK-19).
Validates regex boundary lookaround assertions, multi-word skills, special tokens,
technical vs soft-skill partitioning, dynamic denominators, and gap analysis.
"""

import pytest
from src.skill_extractor import (
    build_skill_pattern,
    extract_skills,
    compare_skills,
    load_skills_taxonomy,
)

@pytest.fixture
def custom_taxonomy():
    return {
        "technical_skills": [
            "Python", "SQL", "Docker", "FastAPI", "Pandas", "PostgreSQL",
            "Git", "Kubernetes", "C++", "C#", ".NET", "Node.js", "CI/CD",
            "Java", "JavaScript", "Machine Learning", "Power BI", "Data Science"
        ],
        "soft_skills": [
            "Communication", "Leadership", "Teamwork", "Problem Solving"
        ]
    }

def test_boundary_safety_java_vs_javascript(custom_taxonomy):
    """Verify that 'JavaScript' does NOT trigger a false positive match for 'Java'."""
    text = "Front-end developer proficient in JavaScript, React, and CSS."
    skills = extract_skills(text, taxonomy=custom_taxonomy)
    assert "JavaScript" in skills["technical_skills"]
    assert "Java" not in skills["technical_skills"]

def test_boundary_safety_c_vs_cpp(custom_taxonomy):
    """Verify that 'C++' does not trigger false positive matching for standalone 'C'."""
    pattern_cpp = build_skill_pattern("C++")
    assert pattern_cpp.search("Expert in C++ systems programming.")
    assert not pattern_cpp.search("Programming in C language.")

def test_special_programming_tokens(custom_taxonomy):
    """Verify C++, C#, .NET, Node.js, and CI/CD match deterministically."""
    text = "Fullstack engineer with C#, .NET Core, Node.js, and CI/CD experience."
    skills = extract_skills(text, taxonomy=custom_taxonomy)
    tech = skills["technical_skills"]
    assert "C#" in tech
    assert ".NET" in tech
    assert "Node.js" in tech
    assert "CI/CD" in tech

def test_multi_word_skills(custom_taxonomy):
    """Verify multi-word skills match across spacing and formatting variations."""
    text = "Specialist in Machine Learning, Power BI dashboards, and Data Science models."
    skills = extract_skills(text, taxonomy=custom_taxonomy)
    tech = skills["technical_skills"]
    assert "Machine Learning" in tech
    assert "Power BI" in tech
    assert "Data Science" in tech

def test_case_insensitivity(custom_taxonomy):
    """Verify matching is case-insensitive and canonical names are preserved."""
    text = "daily use of PYTHON, sql, and DoCkEr."
    skills = extract_skills(text, taxonomy=custom_taxonomy)
    tech = skills["technical_skills"]
    assert "Python" in tech
    assert "SQL" in tech
    assert "Docker" in tech

def test_technical_vs_soft_skills_separation(custom_taxonomy):
    """Verify that technical and soft skills are strictly partitioned."""
    text = "Python engineer with strong Communication, Teamwork, and Problem Solving."
    skills = extract_skills(text, taxonomy=custom_taxonomy)
    assert skills["technical_skills"] == ["Python"]
    assert sorted(skills["soft_skills"]) == ["Communication", "Problem Solving", "Teamwork"]

    # Verify soft skills do not leak into technical skills
    for soft in skills["soft_skills"]:
        assert soft not in skills["technical_skills"]

def test_compare_skills_matched_and_missing():
    """Verify compare_skills accurately computes intersection and difference."""
    candidate_skills = ["Python", "SQL", "Docker", "Git", "Redis"]
    jd_skills = ["Python", "SQL", "Docker", "FastAPI", "Pandas", "PostgreSQL", "Git", "Kubernetes"]

    comparison = compare_skills(candidate_skills, jd_skills)
    assert comparison["matched_skills"] == ["Docker", "Git", "Python", "SQL"]
    assert comparison["missing_skills"] == ["FastAPI", "Kubernetes", "Pandas", "PostgreSQL"]
    assert comparison["skill_match_ratio"] == 4 / 8  # 0.5
    assert comparison["skill_match_percentage"] == 50.0

def test_dynamic_denominator():
    """Verify the skill match denominator dynamically adapts to target JD, not the full taxonomy."""
    candidate_skills = ["Python", "SQL"]

    # JD with 2 skills
    jd_2 = ["Python", "SQL"]
    comp_2 = compare_skills(candidate_skills, jd_2)
    assert comp_2["skill_match_percentage"] == 100.0

    # JD with 4 skills
    jd_4 = ["Python", "SQL", "Docker", "FastAPI"]
    comp_4 = compare_skills(candidate_skills, jd_4)
    assert comp_4["skill_match_percentage"] == 50.0

    # JD with 8 skills
    jd_8 = ["Python", "SQL", "Docker", "FastAPI", "Pandas", "PostgreSQL", "Git", "Kubernetes"]
    comp_8 = compare_skills(candidate_skills, jd_8)
    assert comp_8["skill_match_percentage"] == 25.0

def test_irrelevant_candidate_skills_do_not_inflate_score():
    """Verify candidate skills absent from the JD requirements do NOT inflate match percentage."""
    jd_skills = ["Python", "SQL"]
    
    # Candidate A has only 1 matching skill
    candidate_a = ["Python"]
    comp_a = compare_skills(candidate_a, jd_skills)
    assert comp_a["skill_match_percentage"] == 50.0

    # Candidate B has the same 1 matching skill + 20 irrelevant technical skills
    candidate_b = ["Python", "HTML/CSS", "JavaScript", "React", "CAD", "MATLAB", "Excel", "Thermodynamics", "UI/UX", "Java", "C++", "C#", "Ruby", "PHP", "Swift", "Kotlin", "Rust", "Go", "Perl", "Scala", "Dart"]
    comp_b = compare_skills(candidate_b, jd_skills)
    assert comp_b["skill_match_percentage"] == 50.0  # Must strictly remain 50%, NOT increase
    assert comp_b["matched_skills"] == ["Python"]

def test_compare_skills_zero_required_skills():
    """Verify zero division guard when target JD has zero required skills."""
    comparison = compare_skills(["Python"], [])
    assert comparison["matched_skills"] == []
    assert comparison["missing_skills"] == []
    assert comparison["skill_match_ratio"] == 0.0
    assert comparison["skill_match_percentage"] == 0.0
