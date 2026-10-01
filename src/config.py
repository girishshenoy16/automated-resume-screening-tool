"""
Automated Resume Screening Tool — Centralized System Configuration.

Provides single-source-of-truth constants, directory paths, scoring weights,
decision thresholds, and signal mappings across all pipeline modules.
"""

from pathlib import Path

# ==============================================================================
# Directory and File Paths
# ==============================================================================

# Resolved to the repository root directory (parent of src/)
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
RESUMES_DIR = BASE_DIR / "resumes"
OUTPUTS_DIR = BASE_DIR / "outputs"
PLOTS_DIR = OUTPUTS_DIR / "plots"
DOCS_DIR = BASE_DIR / "docs"
DASHBOARD_DATA_DIR = DOCS_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
IMAGES_DIR = BASE_DIR / "images"

# Operational Data Files
JOB_DESC_FILE = DATA_DIR / "job_description.txt"
SKILLS_FILE = DATA_DIR / "skills_dataset.json"
CURATED_CANDIDATES_FILE = PROCESSED_DATA_DIR / "curated_candidates.json"
EDA_SUMMARY_FILE = PROCESSED_DATA_DIR / "eda_summary.json"

# Output Deliverables
REPORT_CSV_FILE = OUTPUTS_DIR / "screened_candidates_report.csv"
SUMMARY_JSON_FILE = OUTPUTS_DIR / "screening_summary.json"
DASHBOARD_DATA_FILE = DASHBOARD_DATA_DIR / "dashboard_data.json"

# Static Visual Plots
PLOT_SCORE_DIST = PLOTS_DIR / "candidate_score_distribution.png"
PLOT_SKILL_GAP = PLOTS_DIR / "skill_gap_analysis.png"
PLOT_EXP_DIST = PLOTS_DIR / "experience_distribution_eda.png"
PLOT_CAT_DIST = PLOTS_DIR / "category_distribution_eda.png"
PLOT_TOP_SKILLS = PLOTS_DIR / "top_technical_skills_eda.png"

# ==============================================================================
# Model and Pipeline Parameters
# ==============================================================================

RANDOM_STATE = 42

# Supported Document File Extensions
SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt"]

# Hybrid Scoring Weights (Must sum to 1.0)
TFIDF_WEIGHT = 0.40
SKILL_WEIGHT = 0.60

# Recruiter Screening Decision Thresholds (in percentage 0-100)
SHORTLIST_THRESHOLD = 70.0
REVIEW_THRESHOLD = 50.0

# Screening Decision Signals & Neutral Alignment Labels
SIGNAL_SHORTLIST = "SHORTLIST"
SIGNAL_REVIEW = "REVIEW"
SIGNAL_LOW_MATCH = "LOW MATCH"

LABEL_SHORTLIST = "High Match"
LABEL_REVIEW = "Moderate Match"
LABEL_LOW_MATCH = "Low Match"

def get_screening_signal(composite_score: float) -> tuple[str, str]:
    """
    Categorize a composite score into an explainable decision signal and alignment label.

    Args:
        composite_score: Overall percentage score (0.0 to 100.0).

    Returns:
        tuple[str, str]: (Signal, Alignment Label)
    """
    if composite_score >= SHORTLIST_THRESHOLD:
        return SIGNAL_SHORTLIST, LABEL_SHORTLIST
    elif composite_score >= REVIEW_THRESHOLD:
        return SIGNAL_REVIEW, LABEL_REVIEW
    else:
        return SIGNAL_LOW_MATCH, LABEL_LOW_MATCH
