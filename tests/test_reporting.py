"""
Automated unit tests for reporting exports and data contracts (TASK-20 / Reporting Scope).
Validates screened_candidates_report.csv, screening_summary.json, and dashboard_data.json.
"""

import json
from pathlib import Path
import pandas as pd
import pytest

from src import config

def test_screened_candidates_csv_report():
    """Verify screened_candidates_report.csv structure, columns, ordering, and alignment labels."""
    assert config.REPORT_CSV_FILE.exists(), "screened_candidates_report.csv missing"
    df = pd.read_csv(config.REPORT_CSV_FILE)

    assert len(df) == 10, f"Expected 10 candidates in CSV, got {len(df)}"

    expected_columns = [
        "Rank",
        "Candidate Name",
        "File Name",
        "Format",
        "Composite Score (%)",
        "Signal",
        "Alignment Label",
        "Skill Match (%)",
        "TF-IDF Relevance (%)",
        "Detected JD Skills",
        "Missing Skills",
        "Informational Soft Skills",
    ]
    assert list(df.columns) == expected_columns, f"CSV column mismatch: {list(df.columns)}"

    # Verify descending rank and score order
    assert list(df["Rank"]) == list(range(1, 11))
    scores = list(df["Composite Score (%)"])
    assert scores == sorted(scores, reverse=True), "Candidates in CSV are not sorted by score descending"

    # Verify alignment labels strictly use the updated terminology
    valid_labels = {"High Match", "Moderate Match", "Low Match"}
    actual_labels = set(df["Alignment Label"])
    assert actual_labels.issubset(valid_labels), f"Invalid alignment labels in CSV: {actual_labels - valid_labels}"
    assert "High Alignment" not in actual_labels
    assert "Moderate Alignment" not in actual_labels
    assert "Low Measured Alignment" not in actual_labels

    # Verify Candidate 1 is Alex Morgan with SHORTLIST
    top_cand = df.iloc[0]
    assert top_cand["Candidate Name"] == "Alex Morgan"
    assert top_cand["Signal"] == "SHORTLIST"
    assert top_cand["Alignment Label"] == "High Match"
    assert top_cand["Composite Score (%)"] >= 70.0

def test_screening_summary_json():
    """Verify screening_summary.json audit file content and schema."""
    assert config.SUMMARY_JSON_FILE.exists(), "screening_summary.json missing"
    with open(config.SUMMARY_JSON_FILE, "r", encoding="utf-8") as f:
        summary = json.load(f)

    assert summary["total_screened"] == 10
    assert summary["required_skills_count"] == 8
    assert len(summary["required_skills"]) == 8
    assert summary["weights"]["tfidf_weight"] == 0.40
    assert summary["weights"]["skill_weight"] == 0.60
    assert summary["thresholds"]["shortlist_threshold"] == 70.0
    assert summary["thresholds"]["review_threshold"] == 50.0

    counts = summary["decision_counts"]
    assert counts["SHORTLIST"] == 1
    assert counts["REVIEW"] == 2
    assert counts["LOW MATCH"] == 7

    assert summary["top_candidate"]["candidate_name"] == "Alex Morgan"

def test_dashboard_data_json_contract():
    """Verify docs/data/dashboard_data.json data contract consumed by the frontend."""
    assert config.DASHBOARD_DATA_FILE.exists(), "dashboard_data.json missing"
    raw_content = config.DASHBOARD_DATA_FILE.read_text(encoding="utf-8")

    # Confirm zero occurrences of deprecated labels in the serialized file
    assert "High Alignment" not in raw_content
    assert "Moderate Alignment" not in raw_content
    assert "Low Measured Alignment" not in raw_content

    data = json.loads(raw_content)

    # Validate top-level contract sections
    required_sections = ["metadata", "job", "summary", "candidates", "skills", "eda_insights", "configuration"]
    for section in required_sections:
        assert section in data, f"Section '{section}' missing from dashboard_data.json"

    # Validate candidates array
    cands = data["candidates"]
    assert len(cands) == 10
    for idx, c in enumerate(cands, start=1):
        assert c["rank"] == idx
        assert "composite_score" in c
        assert "signal" in c
        assert c["alignment_label"] in ["High Match", "Moderate Match", "Low Match"]
        assert "skill_match_percentage" in c
        assert "tfidf_percentage" in c
        assert "matched_skills" in c
        assert "missing_skills" in c

    # Validate aggregate summary
    sm = data["summary"]
    assert sm["total_candidates"] == 10
    assert sm["shortlist_count"] == 1
    assert sm["review_count"] == 2
    assert sm["low_match_count"] == 7

    # Validate skills breakdown
    sk = data["skills"]
    assert len(sk["required_skills"]) == 8
    assert len(sk["candidate_skill_frequencies"]) == 8
    for skill_name, freq in sk["candidate_skill_frequencies"].items():
        assert 0 <= freq <= 10

    # Validate EDA section
    eda = data["eda_insights"]
    assert eda["total_raw_records"] == 10000
    assert "experience_distribution" in eda
    assert "category_distribution" in eda
