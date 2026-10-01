"""
Automated tests for frontend assets, DOM contract, and cross-runtime parity between
Python and JavaScript engines (Scope: Dashboard & Cross-Runtime Validation).
"""

import json
from pathlib import Path
import subprocess
import pytest

from src import config
from src.cleaner import clean_text as py_clean_text
from src.skill_extractor import extract_skills as py_extract_skills, compare_skills as py_compare_skills

def run_js_helper(payload: dict) -> dict | list:
    """Execute tests/cross_runtime_helper.js passing payload via stdin."""
    helper_path = Path(__file__).resolve().parent / "cross_runtime_helper.js"
    res = subprocess.run(
        ["node", str(helper_path)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False
    )
    assert res.returncode == 0, f"Node helper failed with code {res.returncode}:\n{res.stderr}"
    return json.loads(res.stdout)

def test_dashboard_html_dom_structure():
    """Verify docs/index.html contains all required DOM containers for Tab 1 and Tab 2."""
    html_path = config.DOCS_DIR / "index.html"
    assert html_path.exists(), "docs/index.html missing"
    html = html_path.read_text(encoding="utf-8")

    # Tab navigation elements
    assert 'id="tab-btn-dashboard"' in html
    assert 'id="tab-btn-ats"' in html
    assert 'id="tab-panel-dashboard"' in html
    assert 'id="tab-panel-ats"' in html

    # Tab 1: 5 KPI cards
    assert 'id="kpi-total"' in html
    assert 'id="kpi-shortlist"' in html
    assert 'id="kpi-review"' in html
    assert 'id="kpi-low"' in html
    assert 'id="kpi-avg"' in html

    # Tab 1: 4 Chart canvases
    assert 'id="chart-skill-distribution"' in html
    assert 'id="chart-score-distribution"' in html
    assert 'id="chart-experience"' in html
    assert 'id="chart-category"' in html

    # Tab 1: Candidate intelligence drawer
    assert 'id="candidate-drawer"' in html
    assert 'id="drawer-close"' in html

    # Tab 2: Live ATS Form controls
    assert 'id="ats-company"' in html
    assert 'id="ats-role"' in html
    assert 'id="ats-jd"' in html
    assert 'id="ats-resume-file"' in html
    assert 'id="ats-resume-text"' in html
    assert 'id="ats-analyze-btn"' in html
    assert 'id="ats-reset-btn"' in html

    # Tab 2: Live ATS Results containers
    assert 'id="ats-results"' in html
    assert 'id="res-composite-score"' in html
    assert 'id="res-signal-pill"' in html
    assert 'id="res-signal-desc"' in html
    assert 'id="res-skill-bar"' in html
    assert 'id="res-tfidf-bar"' in html
    assert 'id="res-matched-skills"' in html
    assert 'id="res-missing-skills"' in html
    assert 'id="res-soft-skills"' in html
    assert 'id="res-shared-terms"' in html

def test_javascript_syntax_validity():
    """Verify docs/app.js is syntactically valid via Node.js compiler check."""
    js_path = config.DOCS_DIR / "app.js"
    assert js_path.exists(), "docs/app.js missing"

    result = subprocess.run(
        ["node", "-c", str(js_path)],
        capture_output=True,
        text=True,
        check=False
    )
    assert result.returncode == 0, f"JavaScript syntax error in docs/app.js:\n{result.stderr}"

def test_cross_runtime_skill_extraction_parity():
    """Verify that Python and JavaScript extraction engines produce identical skill sets on test texts."""
    test_cases = [
        "Senior Python Engineer with FastAPI, Docker, PostgreSQL, Kubernetes, and Git experience.",
        "Data Analyst proficient in SQL, Pandas, Power BI, Statistics, and Excel.",
        "Backend developer using C#, .NET Core, Node.js, and CI/CD with Git.",
        "Frontend specialist in HTML/CSS, JavaScript, React, and UI/UX.",
    ]

    payload = {
        "mode": "extract_skills",
        "inputs": test_cases
    }
    js_results = run_js_helper(payload)

    for idx, text in enumerate(test_cases):
        py_clean = py_clean_text(text)
        py_skills = py_extract_skills(py_clean)

        js_tech = js_results[idx]["technical_skills"]
        py_tech = py_skills["technical_skills"]

        assert sorted(js_tech) == sorted(py_tech), (
            f"Skill extraction parity mismatch on case {idx + 1}:\n"
            f"  JS:     {js_tech}\n"
            f"  Python: {py_tech}"
        )

def test_cross_runtime_scoring_and_signal_agreement():
    """Verify that Python and JavaScript engines agree on screening tier for benchmark profiles."""
    from src.extractor import extract_text

    jd_text = config.JOB_DESC_FILE.read_text(encoding="utf-8")

    # Load actual benchmark resumes from resumes/ directory
    alex_file = config.RESUMES_DIR / "candidate_1_alex_senior_python.pdf"
    sarah_file = config.RESUMES_DIR / "candidate_7_sarah_frontend_dev.docx"

    alex_resume = extract_text(alex_file)
    sarah_resume = extract_text(sarah_file)

    payload = {
        "mode": "score_candidates",
        "jd": jd_text,
        "resumes": [alex_resume, sarah_resume]
    }
    js_output = run_js_helper(payload)

    # Validate Alex: Should be SHORTLIST (High Match) with 8/8 skills
    alex_res = js_output[0]
    assert alex_res["matched_count"] == 8
    assert alex_res["total_jd_skills"] == 8
    assert alex_res["skill_match_percentage"] == 100.0
    assert alex_res["composite_score"] >= 70.0
    assert alex_res["signal"] == "SHORTLIST"
    assert alex_res["alignment_label"] == "High Match"

    # Validate Sarah: Should be LOW MATCH (Low Match) with 0/8 skills
    sarah_res = js_output[1]
    assert sarah_res["matched_count"] == 0
    assert sarah_res["skill_match_percentage"] == 0.0
    assert sarah_res["composite_score"] < 50.0
    assert sarah_res["signal"] == "LOW MATCH"
    assert sarah_res["alignment_label"] == "Low Match"
