"""
Automated Resume Screening Tool — Scoring, Reporting & Visualization Engine.

Computes hybrid composite screening scores, assigns transparent screening signals,
renders 5 high-resolution static analytical plots via Matplotlib & Seaborn in outputs/plots/,
and exports structured reports (.csv, .json) and docs/data/dashboard_data.json.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Headless non-interactive rendering backend
import matplotlib.pyplot as plt
import seaborn as sns

try:
    from src import config
except ImportError:
    import config

# ==============================================================================
# Scoring Logic
# ==============================================================================

def compute_composite_score(tfidf_pct: float, skill_pct: float) -> float:
    """
    Calculate composite hybrid screening score using configured weights.

    Formula:
        Score = (TFIDF_WEIGHT * tfidf_pct) + (SKILL_WEIGHT * skill_pct)
    """
    score = (config.TFIDF_WEIGHT * tfidf_pct) + (config.SKILL_WEIGHT * skill_pct)
    return round(max(0.0, min(100.0, score)), 2)

# ==============================================================================
# Static Visual Plot Generators (300 DPI)
# ==============================================================================

def setup_plot_style():
    """Apply consistent, publication-ready styling across all static plots."""
    sns.set_theme(style="whitegrid", font="sans-serif")
    plt.rcParams.update({
        "figure.facecolor": "#FFFFFF",
        "axes.facecolor": "#F8FAFC",
        "grid.color": "#E2E8F0",
        "grid.linestyle": "--",
        "grid.alpha": 0.7,
        "axes.edgecolor": "#CBD5E1",
        "font.size": 10,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.titlecolor": "#1E293B",
        "axes.labelsize": 11,
        "axes.labelcolor": "#475569",
        "xtick.color": "#475569",
        "ytick.color": "#475569",
    })

def generate_plot_score_distribution(candidates: list[dict], output_path: Path):
    """Plot 1: Candidate Score Distribution with screening threshold cutoffs."""
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

    scores = [c["composite_score"] for c in candidates]
    names = [c["candidate_name"].split()[0] for c in candidates]

    # Color each bar based on decision signal
    colors = []
    for s in scores:
        if s >= config.SHORTLIST_THRESHOLD:
            colors.append("#10B981")  # Emerald green
        elif s >= config.REVIEW_THRESHOLD:
            colors.append("#F59E0B")  # Amber
        else:
            colors.append("#EF4444")  # Red

    bars = ax.bar(names, scores, color=colors, width=0.6, edgecolor="#334155", linewidth=0.8)

    # Threshold guidelines
    ax.axhline(config.SHORTLIST_THRESHOLD, color="#059669", linestyle="--", linewidth=1.5,
               label=f"Shortlist Threshold ({config.SHORTLIST_THRESHOLD:.0f}%)")
    ax.axhline(config.REVIEW_THRESHOLD, color="#D97706", linestyle=":", linewidth=1.5,
               label=f"Review Threshold ({config.REVIEW_THRESHOLD:.0f}%)")

    # Bar value labels
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, fontweight="bold", color="#1E293B")

    ax.set_ylim(0, 110)
    ax.set_title("Candidate Composite Screening Score Distribution", pad=12)
    ax.set_xlabel("Candidate (First Name)", labelpad=8)
    ax.set_ylabel("Composite Score (%)", labelpad=8)
    ax.legend(loc="upper right", frameon=True, facecolor="#FFFFFF")

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300)
    plt.close(fig)

def generate_plot_skill_gap(candidates: list[dict], jd_skills: list[str], output_path: Path):
    """Plot 2: Skill Gap Analysis showing applicant pool coverage of required JD skills."""
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

    total_candidates = len(candidates)
    skill_counts = {skill: 0 for skill in jd_skills}
    for c in candidates:
        for sk in c.get("matched_skills", []):
            if sk in skill_counts:
                skill_counts[sk] += 1

    # Sort skills by frequency descending
    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
    skills = [x[0] for x in sorted_skills]
    counts = [x[1] for x in sorted_skills]
    coverage_pcts = [(cnt / total_candidates) * 100 for cnt in counts]

    # Palette: gradient based on coverage
    palette = sns.color_palette("Blues_r", n_colors=len(skills))
    bars = ax.barh(skills[::-1], coverage_pcts[::-1], color=palette, edgecolor="#334155", linewidth=0.8)

    for bar in bars:
        w = bar.get_width()
        ax.annotate(f"{w:.0f}% ({int(w * total_candidates / 100)}/{total_candidates})",
                    xy=(w, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=9, fontweight="bold", color="#1E293B")

    ax.set_xlim(0, 115)
    ax.set_title("Target JD Technical Skill Pool Coverage & Gap Analysis", pad=12)
    ax.set_xlabel("Candidate Pool Coverage (%)", labelpad=8)
    ax.set_ylabel("Required Technical Skill", labelpad=8)

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300)
    plt.close(fig)

def generate_plot_experience_eda(eda_summary: dict, output_path: Path):
    """Plot 3: Experience Distribution EDA across raw Kaggle records."""
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

    exp_data = eda_summary.get("experience_distribution", {}).get("percentages", {})
    labels = list(exp_data.keys())
    values = list(exp_data.values())

    palette = sns.color_palette("viridis", n_colors=len(labels))
    bars = ax.bar(labels, values, color=palette, width=0.55, edgecolor="#334155", linewidth=0.8)

    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, fontweight="bold", color="#1E293B")

    median_exp = eda_summary.get("experience_distribution", {}).get("median_years", 0)
    mean_exp = eda_summary.get("experience_distribution", {}).get("mean_years", 0)

    ax.set_ylim(0, max(values) * 1.25)
    ax.set_title(f"EDA: Candidate Experience Distribution (N = {eda_summary.get('total_records', 0):,} Records)", pad=12)
    ax.set_xlabel("Experience Level Bracket", labelpad=8)
    ax.set_ylabel("Percentage of Total Dataset (%)", labelpad=8)

    # Informational subtitle annotation
    ax.text(0.98, 0.92, f"Median: {median_exp:.1f} yrs | Mean: {mean_exp:.1f} yrs",
            transform=ax.transAxes, ha="right", va="top",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#FFFFFF", edgecolor="#CBD5E1"))

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300)
    plt.close(fig)

def generate_plot_category_eda(eda_summary: dict, output_path: Path):
    """Plot 4: Job Category Distribution across Kaggle training dataset."""
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

    cat_data = eda_summary.get("category_distribution", {})
    categories = list(cat_data.keys())
    counts = list(cat_data.values())

    palette = sns.color_palette("crest", n_colors=len(categories))
    bars = ax.barh(categories[::-1], counts[::-1], color=palette, edgecolor="#334155", linewidth=0.8)

    for bar in bars:
        w = bar.get_width()
        ax.annotate(f"{w:,}",
                    xy=(w, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=9, fontweight="bold", color="#1E293B")

    ax.set_xlim(0, max(counts) * 1.18)
    ax.set_title("EDA: Top Candidate Career Categories in Reference Dataset", pad=12)
    ax.set_xlabel("Candidate Resume Count", labelpad=8)
    ax.set_ylabel("Category", labelpad=8)

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300)
    plt.close(fig)

def generate_plot_top_skills_eda(eda_summary: dict, output_path: Path):
    """Plot 5: Top Technical Skills EDA across Kaggle resume records."""
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

    skill_data = eda_summary.get("top_technical_skills", {})
    skills = list(skill_data.keys())
    counts = list(skill_data.values())

    palette = sns.color_palette("mako", n_colors=len(skills))
    bars = ax.barh(skills[::-1], counts[::-1], color=palette, edgecolor="#334155", linewidth=0.8)

    for bar in bars:
        w = bar.get_width()
        ax.annotate(f"{w:,}",
                    xy=(w, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=9, fontweight="bold", color="#1E293B")

    ax.set_xlim(0, max(counts) * 1.18)
    ax.set_title("EDA: Top Detected Technical Competencies in Source Dataset", pad=12)
    ax.set_xlabel("Occurrences in Candidate Resumes", labelpad=8)
    ax.set_ylabel("Technical Skill", labelpad=8)

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300)
    plt.close(fig)

def generate_all_plots(candidates: list[dict], jd_skills: list[str], eda_summary: dict):
    """Generate and save all 5 publication-ready static analytical plots to outputs/plots/."""
    config.PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    generate_plot_score_distribution(candidates, config.PLOT_SCORE_DIST)
    generate_plot_skill_gap(candidates, jd_skills, config.PLOT_SKILL_GAP)
    generate_plot_experience_eda(eda_summary, config.PLOT_EXP_DIST)
    generate_plot_category_eda(eda_summary, config.PLOT_CAT_DIST)
    generate_plot_top_skills_eda(eda_summary, config.PLOT_TOP_SKILLS)
    print(f"[*] Generated 5 static analytical plots in: {config.PLOTS_DIR}")

# ==============================================================================
# Report & Data Contract Exporters
# ==============================================================================

def export_csv_report(candidates: list[dict], output_path: Path):
    """Export recruiter-friendly tabular CSV report."""
    rows = []
    for c in candidates:
        rows.append({
            "Rank": c["rank"],
            "Candidate Name": c["candidate_name"],
            "File Name": c["file_name"],
            "Format": c["format"],
            "Composite Score (%)": c["composite_score"],
            "Signal": c["signal"],
            "Alignment Label": c["alignment_label"],
            "Skill Match (%)": c["skill_match_percentage"],
            "TF-IDF Relevance (%)": c["tfidf_percentage"],
            "Detected JD Skills": "; ".join(c["matched_skills"]),
            "Missing Skills": "; ".join(c["missing_skills"]),
            "Informational Soft Skills": "; ".join(c.get("soft_skills", []))
        })
    df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"[*] CSV Screening Report exported to: {output_path}")

def export_summary_json(candidates: list[dict], jd_skills: list[str], output_path: Path):
    """Export detailed audit and execution metadata to JSON."""
    total = len(candidates)
    shortlist_cnt = sum(1 for c in candidates if c["signal"] == config.SIGNAL_SHORTLIST)
    review_cnt = sum(1 for c in candidates if c["signal"] == config.SIGNAL_REVIEW)
    low_cnt = sum(1 for c in candidates if c["signal"] == config.SIGNAL_LOW_MATCH)

    avg_score = round(float(np.mean([c["composite_score"] for c in candidates])), 2) if total else 0.0
    avg_skill = round(float(np.mean([c["skill_match_percentage"] for c in candidates])), 2) if total else 0.0
    avg_tfidf = round(float(np.mean([c["tfidf_percentage"] for c in candidates])), 2) if total else 0.0

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_screened": total,
        "job_title": "Senior Python & Data Engineer",
        "required_skills_count": len(jd_skills),
        "required_skills": jd_skills,
        "weights": {
            "tfidf_weight": config.TFIDF_WEIGHT,
            "skill_weight": config.SKILL_WEIGHT
        },
        "thresholds": {
            "shortlist_threshold": config.SHORTLIST_THRESHOLD,
            "review_threshold": config.REVIEW_THRESHOLD
        },
        "decision_counts": {
            "SHORTLIST": shortlist_cnt,
            "REVIEW": review_cnt,
            "LOW MATCH": low_cnt
        },
        "decision_percentages": {
            "SHORTLIST": round((shortlist_cnt / total) * 100, 1) if total else 0.0,
            "REVIEW": round((review_cnt / total) * 100, 1) if total else 0.0,
            "LOW MATCH": round((low_cnt / total) * 100, 1) if total else 0.0
        },
        "averages": {
            "average_composite_score": avg_score,
            "average_skill_score": avg_skill,
            "average_tfidf_score": avg_tfidf
        },
        "top_candidate": candidates[0] if candidates else None
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"[*] Audit Summary JSON exported to: {output_path}")

def export_dashboard_data_json(
    candidates: list[dict],
    jd_skills: list[str],
    eda_summary: dict,
    output_path: Path
):
    """
    Export the comprehensive JSON data contract directly consumed by the
    GitHub Pages recruiter dashboard frontend (docs/data/dashboard_data.json).
    """
    total = len(candidates)
    shortlist_cnt = sum(1 for c in candidates if c["signal"] == config.SIGNAL_SHORTLIST)
    review_cnt = sum(1 for c in candidates if c["signal"] == config.SIGNAL_REVIEW)
    low_cnt = sum(1 for c in candidates if c["signal"] == config.SIGNAL_LOW_MATCH)
    avg_score = round(float(np.mean([c["composite_score"] for c in candidates])), 2) if total else 0.0

    # Pool skill counts
    pool_skills = {s: 0 for s in jd_skills}
    for c in candidates:
        for sk in c.get("matched_skills", []):
            if sk in pool_skills:
                pool_skills[sk] += 1

    dashboard_contract = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "pipeline_version": "1.0.0",
            "tool_name": "Automated Resume Screening Tool",
            "architecture": "Hybrid Lexical TF-IDF & Boundary-Safe Skill Matching Engine"
        },
        "job": {
            "title": "Senior Python & Data Engineer",
            "department": "Data Platform Engineering",
            "required_skills_count": len(jd_skills),
            "required_skills": jd_skills
        },
        "summary": {
            "total_candidates": total,
            "shortlist_count": shortlist_cnt,
            "review_count": review_cnt,
            "low_match_count": low_cnt,
            "average_composite_score": avg_score,
            "shortlist_percentage": round((shortlist_cnt / total) * 100, 1) if total else 0.0
        },
        "candidates": candidates,
        "skills": {
            "required_skills": jd_skills,
            "candidate_skill_frequencies": pool_skills
        },
        "eda_insights": {
            "total_raw_records": eda_summary.get("total_records", 0),
            "experience_distribution": eda_summary.get("experience_distribution", {}),
            "category_distribution": eda_summary.get("category_distribution", {}),
            "top_technical_skills": eda_summary.get("top_technical_skills", {})
        },
        "configuration": {
            "weights": {
                "tfidf_weight": config.TFIDF_WEIGHT,
                "skill_weight": config.SKILL_WEIGHT
            },
            "thresholds": {
                "shortlist_threshold": config.SHORTLIST_THRESHOLD,
                "review_threshold": config.REVIEW_THRESHOLD
            },
            "signals": {
                "shortlist": config.SIGNAL_SHORTLIST,
                "review": config.SIGNAL_REVIEW,
                "low_match": config.SIGNAL_LOW_MATCH
            }
        }
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dashboard_contract, f, indent=2)
    print(f"[*] GitHub Pages Dashboard Data JSON exported to: {output_path}")
