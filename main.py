"""
Automated Resume Screening Tool — Standalone CLI Screening Pipeline.

Main entry point executing end-to-end document parsing, text normalization,
boundary-safe skill extraction, joint TF-IDF cosine relevance modeling,
hybrid scoring, report generation, and static analytical plot rendering.
"""

import sys
import time
import json
from pathlib import Path

from src import config
from src.extractor import extract_text
from src.cleaner import clean_text
from src.skill_extractor import extract_skills, compare_skills
from src.matcher import compute_tfidf_similarity
from src.reporter import (
    compute_composite_score,
    generate_all_plots,
    export_csv_report,
    export_summary_json,
    export_dashboard_data_json,
)

def print_banner():
    print("=" * 80)
    print("  AUTOMATED RESUME SCREENING TOOL — ENTERPRISE RECRUITER DECISION-SUPPORT")
    print("  Version: 1.0.0 | Architecture: Hybrid Lexical TF-IDF + Skill Taxonomy")
    print("=" * 80)

def extract_candidate_name_from_text(raw_text: str, fallback_filename: str) -> str:
    """
    Extract candidate name by inspecting curated metadata, header lines,
    or formatting filename cleanly.
    """
    # 1. Check curated candidate metadata if available
    if config.CURATED_CANDIDATES_FILE.exists():
        try:
            with open(config.CURATED_CANDIDATES_FILE, "r", encoding="utf-8") as f:
                curated = json.load(f)
            fname = Path(fallback_filename).name
            for c in curated:
                if c.get("filename") == fname and c.get("name"):
                    return c.get("name")
        except Exception:
            pass

    # 2. Parse top non-divider lines from resume text
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    for line in lines:
        cleaned = line.replace("=", "").replace("-", "").replace("*", "").strip()
        if cleaned and any(c.isalpha() for c in cleaned) and len(cleaned) < 45:
            if not cleaned.lower().startswith("job") and not cleaned.lower().startswith("profile"):
                return cleaned.title()

    # 3. Fallback to clean filename parsing
    stem = Path(fallback_filename).stem
    parts = [p for p in stem.split("_") if not p.isdigit() and p.lower() != "candidate"]
    if len(parts) >= 2:
        return f"{parts[0].capitalize()} {parts[1].capitalize()}"
    return stem.replace("_", " ").title()

def run_pipeline() -> int:
    start_time = time.time()
    print_banner()

    # --------------------------------------------------------------------------
    # Step 1: Verify Prerequisites
    # --------------------------------------------------------------------------
    print("\n[Stage 1/5] Verifying System Prerequisites & Operational Data...")
    if not config.JOB_DESC_FILE.exists():
        print(f"Error: Target Job Description not found at: {config.JOB_DESC_FILE}")
        return 1

    if not config.SKILLS_FILE.exists():
        print(f"Error: Skills taxonomy not found at: {config.SKILLS_FILE}")
        return 1

    if not config.RESUMES_DIR.exists():
        print(f"Error: Resumes directory not found at: {config.RESUMES_DIR}")
        return 1

    resume_files = sorted([
        f for f in config.RESUMES_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in config.SUPPORTED_EXTENSIONS
    ])

    if not resume_files:
        print(f"Warning: No supported resume documents (.pdf, .docx, .txt) found in: {config.RESUMES_DIR}")
        return 1

    print(f"  [+] Target JD: {config.JOB_DESC_FILE.name}")
    print(f"  [+] Taxonomy: {config.SKILLS_FILE.name}")
    print(f"  [+] Candidate Pool: {len(resume_files)} documents found in {config.RESUMES_DIR.name}/")

    # --------------------------------------------------------------------------
    # Step 2: Parse & Analyze Target Job Description
    # --------------------------------------------------------------------------
    print("\n[Stage 2/5] Ingesting and Analyzing Benchmark Job Description...")
    raw_jd = config.JOB_DESC_FILE.read_text(encoding="utf-8")
    cleaned_jd = clean_text(raw_jd)
    jd_skills_dict = extract_skills(raw_jd)
    jd_tech_skills = jd_skills_dict["technical_skills"]

    print(f"  [+] Extracted {len(jd_tech_skills)} Required Technical Skills:")
    print(f"      {', '.join(jd_tech_skills)}")

    # --------------------------------------------------------------------------
    # Step 3: Batch Process Candidate Resumes
    # --------------------------------------------------------------------------
    print(f"\n[Stage 3/5] Screening {len(resume_files)} Candidate Resumes across Multi-Format Parsers...")
    candidates = []

    for idx, r_file in enumerate(resume_files, 1):
        # 1. Document Extraction
        raw_text = extract_text(r_file)
        fmt = r_file.suffix.upper().replace(".", "")

        # 2. Candidate Name Resolution
        name = extract_candidate_name_from_text(raw_text, r_file.name)

        # 3. NLP Text Normalization
        cleaned_text = clean_text(raw_text)

        # 4. Skill Extraction & Comparison
        cand_skills = extract_skills(raw_text)
        cand_tech = cand_skills["technical_skills"]
        cand_soft = cand_skills["soft_skills"]

        comparison = compare_skills(cand_tech, jd_tech_skills)
        skill_score = comparison["skill_match_percentage"]

        # 5. TF-IDF Cosine Similarity
        tfidf_res = compute_tfidf_similarity(cleaned_text, cleaned_jd)
        tfidf_score = tfidf_res["tfidf_percentage"]

        # 6. Composite Hybrid Score & Screening Signal
        comp_score = compute_composite_score(tfidf_score, skill_score)
        signal, label = config.get_screening_signal(comp_score)

        candidate_record = {
            "candidate_id": f"cand_{idx:02d}",
            "candidate_name": name,
            "file_name": r_file.name,
            "format": fmt,
            "composite_score": comp_score,
            "signal": signal,
            "alignment_label": label,
            "skill_match_percentage": skill_score,
            "tfidf_percentage": tfidf_score,
            "matched_skills": comparison["matched_skills"],
            "missing_skills": comparison["missing_skills"],
            "all_detected_skills": cand_tech,
            "soft_skills": cand_soft,
            "top_shared_terms": tfidf_res["top_shared_terms"],
            "character_count": len(raw_text)
        }
        candidates.append(candidate_record)
        print(f"  [{idx:02d}/{len(resume_files):02d}] Processed {r_file.name:<38} -> Score: {comp_score:5.1f}% [{signal}]")

    # --------------------------------------------------------------------------
    # Step 4: Rank Candidates & Export Reports / Plots
    # --------------------------------------------------------------------------
    print("\n[Stage 4/5] Ranking Candidates and Generating Reports & Visualizations...")
    # Sort descending by composite score, tie-break on skill score
    candidates.sort(key=lambda x: (x["composite_score"], x["skill_match_percentage"]), reverse=True)
    for rank_idx, cand in enumerate(candidates, 1):
        cand["rank"] = rank_idx

    # Ingest EDA metrics for reporting and dashboard data contract
    eda_summary = {}
    if config.EDA_SUMMARY_FILE.exists():
        with open(config.EDA_SUMMARY_FILE, "r", encoding="utf-8") as f:
            eda_summary = json.load(f)

    # 1. Export CSV
    export_csv_report(candidates, config.REPORT_CSV_FILE)

    # 2. Export Audit Summary JSON
    export_summary_json(candidates, jd_tech_skills, config.SUMMARY_JSON_FILE)

    # 3. Export Dashboard Data JSON
    export_dashboard_data_json(candidates, jd_tech_skills, eda_summary, config.DASHBOARD_DATA_FILE)

    # 4. Render 5 Static PNG Plots
    generate_all_plots(candidates, jd_tech_skills, eda_summary)

    # --------------------------------------------------------------------------
    # Step 5: Render Terminal Leaderboard & Execution Summary
    # --------------------------------------------------------------------------
    print("\n[Stage 5/5] Final Screening Results & Leaderboard")
    print("-" * 110)
    print(f"{'Rank':<5} {'Candidate Name':<22} {'Format':<7} {'Score':<8} {'Signal':<11} {'Alignment':<16} {'Skills':<8} {'TF-IDF':<8} {'Matched'}")
    print("-" * 110)

    for c in candidates:
        sig_tag = f"[{c['signal']}]"
        matched_str = f"{len(c['matched_skills'])}/{len(jd_tech_skills)}"
        print(f"{c['rank']:<5} {c['candidate_name']:<22} {c['format']:<7} {c['composite_score']:5.1f}%  {sig_tag:<11} {c['alignment_label']:<16} {c['skill_match_percentage']:5.1f}%  {c['tfidf_percentage']:5.1f}%  {matched_str}")

    print("-" * 110)

    # Screening KPIs
    total = len(candidates)
    shortlist_cnt = sum(1 for c in candidates if c["signal"] == config.SIGNAL_SHORTLIST)
    review_cnt = sum(1 for c in candidates if c["signal"] == config.SIGNAL_REVIEW)
    low_cnt = sum(1 for c in candidates if c["signal"] == config.SIGNAL_LOW_MATCH)
    elapsed = time.time() - start_time

    print(f"\nExecution Summary:")
    print(f"  • Total Candidates Screened: {total}")
    print(f"  • Shortlisted (>= 70%):     {shortlist_cnt} ({shortlist_cnt/total*100:.1f}%)")
    print(f"  • Review Queue (50-69%):    {review_cnt} ({review_cnt/total*100:.1f}%)")
    print(f"  • Low Match (< 50%):        {low_cnt} ({low_cnt/total*100:.1f}%)")
    print(f"  • Total Pipeline Latency:   {elapsed:.2f} seconds ({elapsed/total*1000:.1f} ms/resume)")
    print(f"\nArtifact Deliverables Ready:")
    print(f"  • Tabular Report:           {config.REPORT_CSV_FILE}")
    print(f"  • Audit Log:                {config.SUMMARY_JSON_FILE}")
    print(f"  • GitHub Pages Data:        {config.DASHBOARD_DATA_FILE}")
    print(f"  • Static Visual Plots:      {config.PLOTS_DIR}/ (5 PNG plots generated)")
    print("=" * 80)
    print("  Pipeline execution complete with zero unhandled errors!")
    print("=" * 80)

    return 0

if __name__ == "__main__":
    sys.exit(run_pipeline())
