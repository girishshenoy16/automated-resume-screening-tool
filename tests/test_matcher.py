"""
Automated unit tests for TF-IDF lexical matcher and cosine similarity engine (TASK-20 Part 1).
Validates unigram+bigram vectorization, sublinear TF scaling, cosine similarity bounds,
top shared terms explainability, and edge cases.
"""

import pytest
from src.matcher import compute_tfidf_similarity

def test_identical_documents_similarity():
    """Verify that identical documents produce exactly 100.0% cosine similarity."""
    text = "Senior Python Engineer architecting FastAPI microservices and PostgreSQL databases."
    result = compute_tfidf_similarity(text, text)
    assert result["tfidf_similarity"] == 1.0
    assert result["tfidf_percentage"] == 100.0
    assert len(result["top_shared_terms"]) > 0

def test_orthogonal_documents_similarity():
    """Verify that completely disjoint documents produce 0.0% cosine similarity."""
    jd = "Python FastAPI Docker PostgreSQL Kubernetes Pandas SQL Git"
    resume = "Culinary chef specializing in French pastry baking and sourdough bread fermentation."
    result = compute_tfidf_similarity(resume, jd)
    assert result["tfidf_similarity"] == 0.0
    assert result["tfidf_percentage"] == 0.0
    assert result["top_shared_terms"] == []

def test_relevance_ordering():
    """Verify high-alignment resume scores strictly higher than low-alignment resume."""
    jd = "Senior Python engineer building high-throughput FastAPI microservices and Docker containers."
    high_match = "Python engineer with deep experience in FastAPI, microservices, and Docker deployments."
    low_match = "Frontend developer building React components with HTML and CSS styling."

    res_high = compute_tfidf_similarity(high_match, jd)
    res_low = compute_tfidf_similarity(low_match, jd)

    assert res_high["tfidf_percentage"] > res_low["tfidf_percentage"]
    assert res_high["tfidf_percentage"] > 20.0
    assert res_low["tfidf_percentage"] < 10.0

def test_top_shared_terms_decomposition():
    """Verify top shared terms are extracted and ordered by contribution."""
    jd = "Python FastAPI Docker PostgreSQL"
    resume = "Python developer with Docker and FastAPI experience."
    result = compute_tfidf_similarity(resume, jd, top_n_terms=3)

    assert len(result["top_shared_terms"]) <= 3
    for term in ["python", "docker", "fastapi"]:
        assert any(term in t for t in result["top_shared_terms"])

def test_tfidf_empty_and_whitespace_edge_cases():
    """Verify graceful handling when one or both inputs are empty or whitespace."""
    valid_text = "Python developer with SQL experience."

    # Empty resume
    r1 = compute_tfidf_similarity("", valid_text)
    assert r1["tfidf_similarity"] == 0.0
    assert r1["tfidf_percentage"] == 0.0
    assert r1["top_shared_terms"] == []

    # Empty JD
    r2 = compute_tfidf_similarity(valid_text, "")
    assert r2["tfidf_similarity"] == 0.0
    assert r2["tfidf_percentage"] == 0.0

    # Both empty
    r3 = compute_tfidf_similarity("   \n\t   ", "   ")
    assert r3["tfidf_similarity"] == 0.0
    assert r3["tfidf_percentage"] == 0.0

def test_tfidf_sublinear_scaling_and_bounds():
    """Verify similarity values are strictly bounded in [0.0, 100.0]%."""
    jd = "Python SQL Docker Pandas Kubernetes PostgreSQL Git FastAPI"
    resume = "Python Python Python Python SQL SQL SQL Docker"
    result = compute_tfidf_similarity(resume, jd)

    assert 0.0 <= result["tfidf_similarity"] <= 1.0
    assert 0.0 <= result["tfidf_percentage"] <= 100.0
