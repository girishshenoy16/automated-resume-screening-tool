"""
Automated unit tests for composite scoring, decision signal bands, ranking, and static plots (TASK-20 Part 2).
Validates 40/60 weighting, threshold cutoffs (70/50), alignment labels, and plot asset generation.
"""

from pathlib import Path
import pytest

from src import config
from src.reporter import compute_composite_score

def test_composite_score_formula():
    """Verify that composite score strictly equals (0.40 * TF-IDF) + (0.60 * Skill Match)."""
    # Case 1: 100% TF-IDF, 100% Skill Match
    assert compute_composite_score(100.0, 100.0) == 100.0

    # Case 2: 0% TF-IDF, 0% Skill Match
    assert compute_composite_score(0.0, 0.0) == 0.0

    # Case 3: 50.0% TF-IDF, 80.0% Skill Match -> (0.40 * 50) + (0.60 * 80) = 20 + 48 = 68.0
    assert compute_composite_score(50.0, 80.0) == 68.0

    # Case 4: Benchmark Candidate 1 (Alex Morgan) actual pipeline numbers:
    # tfidf: 39.78, skill: 100.0 -> (0.40 * 39.78) + (0.60 * 100.0) = 15.912 + 60.0 = 75.912 -> 75.91
    assert compute_composite_score(39.78, 100.0) == 75.91

    # Case 5: Benchmark Candidate 2 (Priya Patel):
    # tfidf: 17.97, skill: 87.50 -> (0.40 * 17.97) + (0.60 * 87.50) = 7.188 + 52.5 = 59.688 -> 59.69
    assert compute_composite_score(17.97, 87.50) == 59.69

def test_composite_score_bounds():
    """Verify composite score is bounded strictly within [0.0, 100.0]%."""
    assert compute_composite_score(-10.0, -20.0) == 0.0
    assert compute_composite_score(150.0, 120.0) == 100.0

def test_decision_signals_and_alignment_labels():
    """Verify screening decision signals and neutral alignment labels."""
    # SHORTLIST (High Match)
    sig, lbl = config.get_screening_signal(100.0)
    assert sig == config.SIGNAL_SHORTLIST and lbl == config.LABEL_SHORTLIST == "High Match"

    sig, lbl = config.get_screening_signal(75.91)
    assert sig == config.SIGNAL_SHORTLIST and lbl == "High Match"

    sig, lbl = config.get_screening_signal(70.0)
    assert sig == config.SIGNAL_SHORTLIST and lbl == "High Match"

    # Boundary: Just below 70.0
    sig, lbl = config.get_screening_signal(69.99)
    assert sig == config.SIGNAL_REVIEW and lbl == config.LABEL_REVIEW == "Moderate Match"

    # REVIEW (Moderate Match)
    sig, lbl = config.get_screening_signal(59.69)
    assert sig == config.SIGNAL_REVIEW and lbl == "Moderate Match"

    sig, lbl = config.get_screening_signal(50.0)
    assert sig == config.SIGNAL_REVIEW and lbl == "Moderate Match"

    # Boundary: Just below 50.0
    sig, lbl = config.get_screening_signal(49.99)
    assert sig == config.SIGNAL_LOW_MATCH and lbl == config.LABEL_LOW_MATCH == "Low Match"

    # LOW MATCH (Low Match)
    sig, lbl = config.get_screening_signal(43.45)
    assert sig == config.SIGNAL_LOW_MATCH and lbl == "Low Match"

    sig, lbl = config.get_screening_signal(0.0)
    assert sig == config.SIGNAL_LOW_MATCH and lbl == "Low Match"

def test_weights_sum_to_one():
    """Verify configuration weights sum strictly to 1.0."""
    assert config.TFIDF_WEIGHT + config.SKILL_WEIGHT == pytest.approx(1.0)
    assert config.TFIDF_WEIGHT == 0.40
    assert config.SKILL_WEIGHT == 0.60

def test_static_plots_exist_and_non_empty():
    """Verify all 5 static analytical plots exist in outputs/plots/ and are valid PNG files."""
    plot_files = [
        config.PLOT_SCORE_DIST,
        config.PLOT_SKILL_GAP,
        config.PLOT_EXP_DIST,
        config.PLOT_CAT_DIST,
        config.PLOT_TOP_SKILLS,
    ]

    for p in plot_files:
        assert p.exists(), f"Missing static plot: {p.name}"
        size = p.stat().st_size
        assert size > 10_000, f"Plot file {p.name} is unusually small ({size} bytes)"

        # Check PNG header signature (first 8 bytes: 89 50 4E 47 0D 0A 1A 0A)
        with open(p, "rb") as f:
            header = f.read(8)
        assert header == b"\x89PNG\r\n\x1a\n", f"File {p.name} is not a valid PNG"
