# Proof-Building & Phased Commit Strategy (`proof_building_plan.md`)

## Overview

This document defines the **6-Day Phased Commit Strategy** for the **Automated Resume Screening Tool / Resume Screening & ATS Platform**. 

For software engineering portfolios, hiring managers and technical interviewers look for realistic, incremental Git histories demonstrating disciplined branch hygiene, conventional commit messages, and continuous validation rather than a single massive initial commit.

---

## 6-Day Development Timeline

```text
Day 1: Project Scaffolding, Virtual Environment & Raw Dataset Ingestion
Day 2: Multi-Format Document Parsers & Token-Safe NLP Normalization
Day 3: Boundary-Safe Skill Matcher, TF-IDF Vectorizer & Static Plot Generation
Day 4: Batch Pipeline Execution, Structured Reporting & Test Suite Authoring
Day 5: 2-Tab Executive Platform (Screening Dashboard + Live ATS Checker)
Day 6: Final QA Audit, Full Documentation Suite & Portfolio Presentation
```

---

## Day 1: Scaffolding, Environment & Raw Data Ingestion

### Objective:
Set up repository structure, install virtual environment dependencies, organize raw Kaggle dataset, and establish centralized configuration.

### Git Commands:
```bash
git init
git checkout -b main

# Commit 1.1: Project scaffolding & environment configuration
git add .gitignore requirements.txt
git commit -m "chore: initialize project scaffolding and dependency specifications"

# Commit 1.2: Centralized system configuration
git add src/config.py src/__init__.py
git commit -m "feat(config): establish centralized paths, weights, and screening thresholds"

# Commit 1.3: Raw dataset integration and documentation
git add data/raw/ data/dataset_notes.md
git commit -m "docs(dataset): ingest Kaggle resume dataset and document file schemas"
```

### Portfolio Milestone & Evidence:
- Terminal screenshot showing clean virtual environment activation and `requirements.txt` installation.
- Schema verification of `data/raw/training_data.csv` and `data/raw/job_roles.csv`.

---

## Day 2: Multi-Format Document Extraction & NLP Cleaner

### Objective:
Build document parsers supporting `.pdf`, `.docx`, and `.txt` with automatic fallback, and implement token-safe text cleaning that preserves programming symbols (`C++`, `C#`, `.NET`, `Node.js`, `CI/CD`).

### Git Commands:
```bash
# Commit 2.1: Multi-format document parser
git add src/extractor.py
git commit -m "feat(extractor): implement fault-tolerant PDF, DOCX, and TXT extraction"

# Commit 2.2: Token-safe text normalizer
git add src/cleaner.py
git commit -m "feat(cleaner): implement URL/email stripping and protected token masking"

# Commit 2.3: Curated benchmark profiles generation
git add data/job_description.txt data/skills_dataset.json resumes/
git commit -m "feat(data): establish benchmark JD and curate 10 multi-format candidate resumes"
```

### Portfolio Milestone & Evidence:
- Unit test verification proving `C++`, `C#`, and `.NET` survive punctuation stripping intact.
- Verified file listing in `resumes/` containing 4 PDFs, 4 DOCXs, and 2 TXTs.

---

## Day 3: Skill Matching, TF-IDF Vectorizer & Visualizations

### Objective:
Implement boundary-safe skill extraction with dynamic denominators, construct sublinear TF-IDF cosine similarity vectorizer, and generate 5 static analytical plots.

### Git Commands:
```bash
# Commit 3.1: Boundary-safe skill matcher
git add src/skill_extractor.py
git commit -m "feat(skills): implement boundary lookaround matching and dynamic JD denominator"

# Commit 3.2: Lexical TF-IDF matcher
git add src/matcher.py
git commit -m "feat(matcher): construct sublinear TF-IDF n-gram vectorizer and cosine similarity"

# Commit 3.3: Static plot generation engine
git add src/reporter.py outputs/plots/
git commit -m "feat(reporter): generate 5 publication-ready static analytical plots in outputs/"
```

### Portfolio Milestone & Evidence:
- Output verification of all 5 static PNG plots in `outputs/plots/` (score distribution, skill gap, experience EDA, category EDA, top skills).
- Terminal log verifying zero division guards and dynamic denominator scaling.

---

## Day 4: Batch Pipeline Execution & Automated Testing Suite

### Objective:
Wire end-to-end CLI pipeline runner (`main.py`), generate CSV/JSON audit deliverables, and author full `pytest` suite across 9 modules.

### Git Commands:
```bash
# Commit 4.1: CLI pipeline execution
git add main.py outputs/screened_candidates_report.csv outputs/screening_summary.json
git commit -m "feat(pipeline): wire main CLI runner and export structured screening reports"

# Commit 4.2: Automated unit & edge-case testing suite
git add tests/test_dataset.py tests/test_extractor.py tests/test_cleaner.py tests/test_skill_extractor.py tests/test_matcher.py tests/test_scoring_ranking.py tests/test_reporting.py tests/test_edge_cases.py
git commit -m "test: implement comprehensive 56-test automated validation suite"
```

### Portfolio Milestone & Evidence:
- Terminal screenshot showing `pytest -v` output with 56 passed tests in < 5 seconds.
- Inspection of `outputs/screened_candidates_report.csv` showing Alex Morgan ranked #1.

---

## Day 5: 2-Tab Executive Platform & GitHub Pages Deployment

### Objective:
Build responsive client-side web application in `docs/` featuring Tab 1 (Screening Dashboard with 4 Chart.js charts and candidate inspect drawer) and Tab 2 (Live ATS Checker with in-browser extraction and explainability).

### Git Commands:
```bash
# Commit 5.1: GitHub Pages HTML structure & CSS design system
git add docs/index.html docs/style.css
git commit -m "feat(ui): design executive 2-tab ATS interface with responsive styling"

# Commit 5.2: Client-side Live ATS engine & Chart.js integration
git add docs/app.js docs/data/dashboard_data.json docs/data/skills_taxonomy.json
git commit -m "feat(engine): implement browser TF-IDF engine, Live ATS checker, and Chart.js graphs"

# Commit 5.3: Cross-runtime parity testing
git add tests/test_cross_runtime.py tests/cross_runtime_helper.js
git commit -m "test(cross-runtime): verify Python and JavaScript algorithmic scoring parity"
```

### Portfolio Milestone & Evidence:
- Browser screenshot of Tab 1 (Executive Dashboard with KPI cards and leaderboard).
- Browser screenshot of Tab 2 (Live ATS Checker showing candidate score hero card and skill gap breakdown).

---

## Day 6: Final QA Audit, Documentation & Portfolio Presentation

### Objective:
Perform comprehensive file tree audit against the formal Definition of Done, author complete documentation suite (`README.md`, formal technical reports, executive briefing, interview prep), and freeze release.

### Git Commands:
```bash
# Commit 6.1: Formal documentation suite
git add reports/dashboard_schema.md reports/architecture.md reports/project_report.md reports/executive_summary.md reports/interview_prep.md reports/proof_building_plan.md
git commit -m "docs(reports): author architectural specs, project report, executive briefing, and interview guide"

# Commit 6.2: Portfolio README and release freeze
git add README.md task.md
git commit -m "docs(readme): finalize GitHub portfolio presentation and freeze Phase 10-13 scope"
```

### Portfolio Milestone & Evidence:
- Fully styled `README.md` with project architecture, benchmark leaderboard, live GitHub Pages link, and embedded plot images.
- Clean `git status` with zero untracked files and 100% test pass rate.
