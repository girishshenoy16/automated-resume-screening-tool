# Automated Resume Screening & ATS Decision-Support System: Technical Project Report

**Author:** Antigravity Engineering Team  
**System Name:** Automated Resume Screening Tool / Resume Screening & ATS Platform  
**Version:** 1.0.0  
**Target Benchmark Requisition:** Senior Python & Data Engineer  
**Date:** September 2026  

---

## 1. Abstract

Recruitment pipelines at technology enterprises routinely handle hundreds to thousands of applicant resumes per open requisition. Manual screening of unstructured documents across multiple formats introduces significant operational latency, recruiter fatigue, and screening inconsistency. 

This project presents the **Automated Resume Screening Tool**, an explainable, deterministic recruiter decision-support system. Combining multi-format document parsing (`.pdf`, `.docx`, `.txt`), token-safe NLP normalization, boundary-safe regular expression skill extraction, and sublinear TF-IDF lexical cosine similarity, the system scores and categorizes candidate resumes against benchmark job descriptions. Across a curated 10-candidate benchmark cohort derived from a 10,000-record Kaggle resume dataset, the automated pipeline executed in **2.37 seconds** (~237 ms per resume) with zero unhandled errors, successfully triaging profiles into three actionable tiers: **High Match** (`SHORTLIST`), **Moderate Match** (`REVIEW`), and **Low Match** (`LOW MATCH`).

---

## 2. Problem Statement & Motivation

Modern talent acquisition workflows face three persistent bottlenecks:
1. **Format Heterogeneity**: Applicant resumes arrive as binary PDFs, Microsoft Word archives (`.docx`), and plain text (`.txt`), often with disparate internal structures (tables, multi-column layouts, varying encodings).
2. **Technical Token Mangling**: Conventional text sanitization algorithms inadvertently strip non-alphanumeric programming symbols (e.g., stripping `+` turns `C++` into `c`; stripping `#` turns `C#` into `c`; stripping leading dots turns `.NET` into `net`).
3. **Black-Box Opacity**: Opaque deep-learning models and LLM wrappers frequently hallucinate evaluations, suffer from non-deterministic outputs, and fail to provide recruiters with transparent, mathematically verifiable justification for screening signals.

The system addresses these challenges through a transparent, explainable decision-support architecture where every score can be mathematically decomposed into hard technical skill coverage and lexical relevance.

---

## 3. Dataset Provenance & Benchmark Curation

### 3.1 Raw Dataset Specification
The underlying dataset originates from the Kaggle *AI Resume Analyzer / Job Role Prediction Dataset* (`data/raw/`):
- `training_data.csv`: 10,001 resume records spanning 12 employment categories.
- `job_roles.csv`: 325 job role descriptions with associated skill requirements.
- `skills_database.json` & `skills_list.csv`: Categorized domain skills taxonomy.
- `test_resumes.json`: Structured benchmark personas.

### 3.2 Exploratory Data Analysis (EDA) Highlights
Analysis of 10,000 source records revealed:
- **Experience Distribution**: $42.2\%$ of records fall in 0–2 years, $47.6\%$ in 3–5 years, $9.0\%$ in 6–10 years, and $1.2\%$ in 11–15 years (median: 3.0 years, mean: 3.1 years).
- **Category Representation**: Technology constitutes the plurality with 2,511 records ($25.1\%$), followed by Data & Analytics (568), Healthcare (488), and Marketing & Sales (463).

### 3.3 Controlled 10-Candidate Benchmark Cohort
To rigorously benchmark the screening engine, 10 synthetic candidate profiles were curated and formatted across real-world document parsers:
- **4 PDFs**: Alex Morgan (Senior Python), David Kim (ML Intern), Marcus Vance (Backend Dev), Jason Miller (Mechanical Eng).
- **4 DOCXs**: Priya Patel (Data Analyst), Emily Chen (BI Analyst), Sarah Jenkins (Frontend Dev), Aisha Khan (Fresh Graduate).
- **2 TXTs**: Elena Rostova (Fullstack Dev), Carlos Gomez (Career Changer).

---

## 4. NLP Methodology & Algorithmic Architecture

### 4.1 Token-Safe Text Cleaning (`src/cleaner.py`)
To preserve critical technical programming symbols while stripping noise:
1. Strips web URLs and email addresses via regular expressions.
2. Masks protected tokens before punctuation removal:
   - `(?i)\bc\+\+` $\rightarrow$ `__TOKEN_CPP__`
   - `(?i)\bc\#` $\rightarrow$ `__TOKEN_CSHARP__`
   - `(?i)(?<!\w)\.net\b` $\rightarrow$ `__TOKEN_DOTNET__`
   - `(?i)\bnode\.js\b` $\rightarrow$ `__TOKEN_NODEJS__`
   - `(?i)\bci/cd\b` $\rightarrow$ `__TOKEN_CICD__`
3. Converts text to lowercase and strips non-alphanumeric characters (`[^\w\s]`).
4. Restores protected tokens back to normalized lowercase equivalents.
5. Collapses redundant whitespace and line breaks.

### 4.2 Boundary-Safe Technical Skill Extraction (`src/skill_extractor.py`)
- Employs negative lookaround assertions (`(?<![\w\+])c\+\+(?![\w\+])`) and word boundaries (`\b`) to eliminate false-positive substring collisions (e.g. verifying that `"JavaScript"` never matches `"Java"`).
- **Dynamic Denominator Matching**: Matches are evaluated against the required technical skills extracted from the active Job Description ($|S_{\text{JD\_tech}}| = 8$ in benchmark).
- **Soft Skills Partitioning**: Soft skills (`Communication`, `Leadership`, `Teamwork`) are tagged as informational and strictly excluded from numerical scoring.

### 4.3 Sublinear TF-IDF Vector Space Model (`src/matcher.py`)
- Computes term frequencies with sublinear scaling: $\text{tf}_{\text{sublinear}} = 1 + \ln(\text{tf})$ for $\text{tf} > 0$.
- Employs joint unigrams and bigrams (`ngram_range=(1, 2)`) with English stop-word elimination.
- Calculates $L_2$-normalized cosine similarity:
  $$S_{\text{tfidf}} = \min\left(100.0, \max\left(0.0, \frac{\vec{v}_{\text{JD}} \cdot \vec{v}_{\text{Resume}}}{\|\vec{v}_{\text{JD}}\|_2 \|\vec{v}_{\text{Resume}}\|_2} \times 100\right)\right)$$

### 4.4 Hybrid Composite Scoring Formula (`src/reporter.py`)
Screening scores are calculated as:
$$\text{Composite Score} = (0.40 \times S_{\text{tfidf}}) + (0.60 \times S_{\text{skill}})$$

Decision signals and recruiter labels:
- $\ge 70.0\%$: `SHORTLIST` / **High Match**
- $50.0\% - 69.9\%$: `REVIEW` / **Moderate Match**
- $< 50.0\%$: `LOW MATCH` / **Low Match**

---

## 5. Empirical Benchmarking Results

Execution of `main.py` against the 10 benchmark candidates yielded:

| Rank | Candidate Name | Format | Score | Signal | Alignment Label | Skill Match | TF-IDF | Matched Skills |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | Alex Morgan | PDF | 75.9% | `SHORTLIST` | High Match | 100.0% (8/8) | 39.8% | Docker, FastAPI, Git, Kubernetes, Pandas, PostgreSQL, Python, SQL |
| 2 | Priya Patel | DOCX | 59.7% | `REVIEW` | Moderate Match | 87.5% (7/8) | 18.0% | Docker, FastAPI, Git, Pandas, PostgreSQL, Python, SQL |
| 3 | Marcus Vance | PDF | 50.6% | `REVIEW` | Moderate Match | 75.0% (6/8) | 14.0% | Docker, Git, Kubernetes, PostgreSQL, Python, SQL |
| 4 | Elena Rostova | TXT | 43.5% | `LOW MATCH` | Low Match | 62.5% (5/8) | 14.9% | Docker, FastAPI, Git, Python, SQL |
| 5 | David Kim | PDF | 42.2% | `LOW MATCH` | Low Match | 62.5% (5/8) | 11.8% | Docker, Git, Pandas, Python, SQL |
| 6 | Carlos Gomez | TXT | 17.5% | `LOW MATCH` | Low Match | 25.0% (2/8) | 6.3% | Python, SQL |
| 7 | Aisha Khan | DOCX | 10.2% | `LOW MATCH` | Low Match | 12.5% (1/8) | 6.8% | Git |
| 8 | Emily Chen | DOCX | 9.9% | `LOW MATCH` | Low Match | 12.5% (1/8) | 6.0% | SQL |
| 9 | Jason Miller | PDF | 1.7% | `LOW MATCH` | Low Match | 0.0% (0/8) | 4.1% | None |
| 10 | Sarah Jenkins | DOCX | 0.9% | `LOW MATCH` | Low Match | 0.0% (0/8) | 2.2% | None |

### Performance Metrics:
- **Total Pipeline Latency**: $2.37$ seconds ($236.8$ ms/resume).
- **Shortlist Rate**: $10.0\%$ (1/10 candidates).
- **Review Rate**: $20.0\%$ (2/10 candidates).
- **Low Match Rate**: $70.0\%$ (7/10 candidates).
- **Average Cohort Score**: $31.2\%$.

---

## 6. Analytical Visualizations

The pipeline generates five publication-ready static plots in `outputs/plots/`:
1. `candidate_score_distribution.png`: Compares candidate composite scores against decision threshold lines (70% shortlist, 50% review).
2. `skill_gap_analysis.png`: Horizontal bar chart depicting candidate pool coverage and gaps for each required JD technical skill.
3. `experience_distribution_eda.png`: Bar chart detailing experience band representation across 10,000 source dataset records.
4. `category_distribution_eda.png`: Horizontal bar breakdown of job categories in the source corpus.
5. `top_technical_skills_eda.png`: Most frequently occurring technical competencies in the raw dataset.

---

## 7. Responsible AI & Transparency Guardrails

1. **Deterministic Decision Support**: The system does not make autonomous hiring decisions; it is architected as an auditable recruiter decision-support tool.
2. **Protected Demographic Blindness**: Names, emails, phone numbers, and physical addresses are excluded from scoring calculations.
3. **No Opaque Embeddings or Hallucination**: Every score component is traceable to exact lexical n-grams and verifiable skill keyword matches.
4. **Dynamic Requisition Scoping**: Denominators dynamically adapt to the active Job Description, preventing candidates from being penalized for skills irrelevant to the specific role.

---

## 8. Conclusion

The Automated Resume Screening Tool proves that transparent lexical NLP models and boundary-safe token extraction provide a robust, lightning-fast alternative to black-box machine learning for resume triage. With complete sub-second multi-format extraction, explainable scoring, automated testing (56 passed unit tests), and a responsive 2-tab executive web application, the system delivers an enterprise-grade recruiting decision-support solution.
