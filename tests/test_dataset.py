"""
Automated tests for dataset loading, raw file integrity, schemas,
processed artifacts, and synthetic candidate profiles (TASK-16).
"""

import json
from pathlib import Path
import pandas as pd
import pytest

from src import config

def test_raw_dataset_files_exist():
    """Verify all expected Kaggle source dataset files exist in data/raw/."""
    expected_files = [
        "training_data.csv",
        "job_roles.csv",
        "test_resumes.json",
        "skills_database.json",
        "skills_list.csv",
    ]
    for filename in expected_files:
        file_path = config.RAW_DATA_DIR / filename
        assert file_path.exists(), f"Missing required raw dataset file: {filename}"
        assert file_path.stat().st_size > 0, f"Raw file is empty: {filename}"

def test_raw_training_data_schema():
    """Verify training_data.csv schema, non-empty row count, and expected columns."""
    csv_path = config.RAW_DATA_DIR / "training_data.csv"
    df = pd.read_csv(csv_path, nrows=10)
    expected_cols = {
        "Resume ID",
        "Resume Text",
        "Education",
        "Experience Years",
        "Skills",
        "Job Role",
        "Category",
    }
    assert expected_cols.issubset(set(df.columns)), f"Columns missing from training_data.csv: {expected_cols - set(df.columns)}"

def test_processed_artifacts_exist_and_valid():
    """Verify data/processed/ artifacts exist with valid JSON structure."""
    assert config.CURATED_CANDIDATES_FILE.exists(), "curated_candidates.json missing"
    assert config.EDA_SUMMARY_FILE.exists(), "eda_summary.json missing"

    with open(config.CURATED_CANDIDATES_FILE, "r", encoding="utf-8") as f:
        candidates = json.load(f)
    assert isinstance(candidates, list), "curated_candidates.json must be a list"
    assert len(candidates) == 10, f"Expected exactly 10 curated candidates, got {len(candidates)}"

    for cand in candidates:
        assert "id" in cand
        assert "name" in cand
        assert "format" in cand
        assert "filename" in cand
        assert "skills" in cand
        assert "summary" in cand
        assert len(cand["summary"].strip()) > 30, f"Candidate {cand.get('name')} has insufficient summary"

    with open(config.EDA_SUMMARY_FILE, "r", encoding="utf-8") as f:
        eda = json.load(f)
    assert "experience_distribution" in eda
    assert "category_distribution" in eda
    assert "total_records" in eda
    assert eda["total_records"] == 10000

def test_benchmark_resumes_multi_format():
    """Verify 10 multi-format resume files exist in resumes/ with correct extensions."""
    assert config.RESUMES_DIR.exists(), "resumes/ directory missing"
    resume_files = [
        rf for rf in config.RESUMES_DIR.iterdir()
        if rf.is_file() and rf.suffix.lower() in config.SUPPORTED_EXTENSIONS
    ]
    assert len(resume_files) == 10, f"Expected 10 resumes, found {len(resume_files)}"

    format_counts = {".pdf": 0, ".docx": 0, ".txt": 0}
    for rf in resume_files:
        ext = rf.suffix.lower()
        format_counts[ext] += 1
        assert rf.stat().st_size > 0, f"Resume file is 0 bytes: {rf.name}"

    assert format_counts[".pdf"] == 4, f"Expected 4 PDFs, got {format_counts['.pdf']}"
    assert format_counts[".docx"] == 4, f"Expected 4 DOCX, got {format_counts['.docx']}"
    assert format_counts[".txt"] == 2, f"Expected 2 TXT, got {format_counts['.txt']}"

def test_operational_benchmark_data():
    """Verify benchmark job description and skills taxonomy files exist and are populated."""
    assert config.JOB_DESC_FILE.exists(), "data/job_description.txt missing"
    jd_text = config.JOB_DESC_FILE.read_text(encoding="utf-8")
    assert len(jd_text.strip()) > 100, "Job description text too short"

    assert config.SKILLS_FILE.exists(), "data/skills_dataset.json missing"
    with open(config.SKILLS_FILE, "r", encoding="utf-8") as f:
        taxonomy = json.load(f)

    assert "technical_skills" in taxonomy
    assert "soft_skills" in taxonomy
    assert len(taxonomy["technical_skills"]) >= 30, "Technical skills list too small"
    assert len(taxonomy["soft_skills"]) >= 5, "Soft skills list too small"
