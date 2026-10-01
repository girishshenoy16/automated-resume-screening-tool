# Dashboard Data Contract & JSON Schema (`dashboard_schema.md`)

## 1. Overview & Data Contract Purpose

The **Automated Resume Screening Tool / Resume Screening & ATS Platform** relies on a decoupled, static data contract between the offline Python processing pipeline (`src/reporter.py`) and the client-side recruiter decision-support frontend (`docs/app.js`).

The data artifact is exported as:
```text
docs/data/dashboard_data.json
```

This JSON file acts as an immutable snapshot consumed by GitHub Pages. It enables zero-latency rendering of executive KPI cards, sortable/searchable leaderboards, interactive score decomposition drawers, and Chart.js analytical visualizations without requiring an active backend or runtime database.

---

## 2. Top-Level Schema Definition

The root object of `dashboard_data.json` contains seven mandatory top-level sections:

```json
{
  "metadata": { ... },
  "job": { ... },
  "summary": { ... },
  "candidates": [ ... ],
  "skills": { ... },
  "eda_insights": { ... },
  "configuration": { ... }
}
```

---

## 3. Section Specifications

### 3.1 `metadata` Section
Contains operational provenance and pipeline build information.

| Field | Type | Nullable | Description / Range |
|---|---|:---:|---|
| `generated_at` | `string` (ISO 8601) | No | UTC timestamp when the pipeline finished execution. |
| `pipeline_version` | `string` | No | Semantic version of the engine (e.g. `"1.0.0"`). |
| `tool_name` | `string` | No | System name: `"Automated Resume Screening Tool"`. |
| `architecture` | `string` | No | Engine summary: `"Hybrid Lexical TF-IDF & Boundary-Safe Skill Matching Engine"`. |

### 3.2 `job` Section
Defines the benchmark target Job Description metadata and required technical skills.

| Field | Type | Nullable | Description / Range |
|---|---|:---:|---|
| `title` | `string` | No | Benchmark job title: `"Senior Python & Data Engineer"`. |
| `department` | `string` | No | Organizational unit: `"Data Platform Engineering"`. |
| `required_skills_count`| `integer` | No | Count of technical skills in benchmark requisition (`8`). |
| `required_skills` | `array[string]` | No | List of canonical required technical skills. |

### 3.3 `summary` Section
Provides aggregate screening cohort metrics for top-level KPI cards.

| Field | Type | Nullable | Description / Range |
|---|---|:---:|---|
| `total_candidates` | `integer` | No | Number of resumes processed in cohort (`10`). |
| `shortlist_count` | `integer` | No | Candidates with composite score $\ge 70.0\%$ (`1`). |
| `review_count` | `integer` | No | Candidates with score in $[50.0\%, 69.9\%]$ (`2`). |
| `low_match_count` | `integer` | No | Candidates with score $< 50.0\%$ (`7`). |
| `average_composite_score` | `number` | No | Cohort mean score (e.g. `31.2`). |
| `shortlist_percentage`| `number` | No | Percentage of pool shortlisted (e.g. `10.0`). |

### 3.4 `candidates` Section (Array of Candidate Objects)
Chronologically ranked list of screened candidate records (sorted by `rank` ascending / `composite_score` descending).

Each item in `candidates` contains:

| Field | Type | Nullable | Description / Range |
|---|---|:---:|---|
| `candidate_id` | `string` | No | Unique identifier (e.g. `"cand_02"`). |
| `candidate_name` | `string` | No | Full name of the candidate persona. |
| `file_name` | `string` | No | Source filename in `resumes/` folder. |
| `format` | `string` | No | Document format: `"PDF"`, `"DOCX"`, or `"TXT"`. |
| `composite_score` | `number` | No | Final hybrid percentage score ($0.0$ to $100.0$). |
| `signal` | `string` | No | System signal code: `"SHORTLIST"`, `"REVIEW"`, or `"LOW MATCH"`. |
| `alignment_label` | `string` | No | Recruiter label: `"High Match"`, `"Moderate Match"`, or `"Low Match"`. |
| `skill_match_percentage`| `number`| No | Skill match percentage ($0.0$ to $100.0$). |
| `tfidf_percentage` | `number` | No | Scaled cosine similarity percentage ($0.0$ to $100.0$). |
| `matched_skills` | `array[string]` | No | Intersection of candidate technical skills and target JD. |
| `missing_skills` | `array[string]` | No | Target JD skills absent from the candidate resume. |
| `all_detected_skills` | `array[string]` | No | All taxonomy technical skills recognized in resume. |
| `soft_skills` | `array[string]` | No | Informational soft skills recognized (excluded from score). |
| `top_shared_terms` | `array[string]` | No | Top shared n-grams driving TF-IDF similarity. |
| `character_count` | `integer` | No | Raw character length of candidate resume text. |
| `rank` | `integer` | No | Ordinal rank in cohort ($1$ to $10$). |

### 3.5 `skills` Section
Tracks dataset-wide skill frequencies across the screened candidate cohort.

| Field | Type | Nullable | Description / Range |
|---|---|:---:|---|
| `required_skills` | `array[string]` | No | Requisition technical skills (`8` items). |
| `candidate_skill_frequencies`| `object` | No | Key-value mapping of skill name to count of matching candidates. |

### 3.6 `eda_insights` Section
Encapsulates exploratory data analysis metrics computed across the **10,000-record Kaggle source dataset**. Powers the lower two Chart.js graphs.

| Field | Type | Nullable | Description / Range |
|---|---|:---:|---|
| `total_raw_records` | `integer` | No | Total sample size analyzed (`10000`). |
| `experience_distribution`| `object` | No | Experience band counts, percentages, median, and mean. |
| `experience_distribution.counts`| `object` | No | Bracket counts: `"0-2 Years"`, `"3-5 Years"`, `"6-10 Years"`, etc. |
| `experience_distribution.percentages`| `object` | No | Bracket percentages (sums to $100.0\%$). |
| `experience_distribution.median_years`| `number` | No | Median experience in years (`3.0`). |
| `experience_distribution.mean_years`| `number` | No | Mean experience in years (`3.1`). |
| `category_distribution`| `object` | No | Frequency count per job category (Technology, Healthcare, etc.). |
| `top_technical_skills` | `object` | No | Frequency count of top skills extracted across source corpus. |

### 3.7 `configuration` Section
Transparently surfaces pipeline operational parameters and decision thresholds.

| Field | Type | Nullable | Description / Range |
|---|---|:---:|---|
| `weights.tfidf_weight` | `number` | No | Textual similarity weighting factor (`0.4`). |
| `weights.skill_weight` | `number` | No | Technical skill match weighting factor (`0.6`). |
| `thresholds.shortlist_threshold`| `number`| No | Cutoff for High Match (`70.0`). |
| `thresholds.review_threshold` | `number`| No | Cutoff for Moderate Match (`50.0`). |
| `signals` | `object` | No | Maps signal keys to enum codes (`"SHORTLIST"`, etc.). |

---

## 4. Sample JSON Payload

```json
{
  "metadata": {
    "generated_at": "2026-09-18T14:57:51.123189+00:00",
    "pipeline_version": "1.0.0",
    "tool_name": "Automated Resume Screening Tool",
    "architecture": "Hybrid Lexical TF-IDF & Boundary-Safe Skill Matching Engine"
  },
  "job": {
    "title": "Senior Python & Data Engineer",
    "department": "Data Platform Engineering",
    "required_skills_count": 8,
    "required_skills": [
      "Docker", "FastAPI", "Git", "Kubernetes",
      "Pandas", "PostgreSQL", "Python", "SQL"
    ]
  },
  "summary": {
    "total_candidates": 10,
    "shortlist_count": 1,
    "review_count": 2,
    "low_match_count": 7,
    "average_composite_score": 31.2,
    "shortlist_percentage": 10.0
  },
  "candidates": [
    {
      "candidate_id": "cand_02",
      "candidate_name": "Alex Morgan",
      "file_name": "candidate_1_alex_senior_python.pdf",
      "format": "PDF",
      "composite_score": 75.91,
      "signal": "SHORTLIST",
      "alignment_label": "High Match",
      "skill_match_percentage": 100.0,
      "tfidf_percentage": 39.78,
      "matched_skills": [
        "Docker", "FastAPI", "Git", "Kubernetes",
        "Pandas", "PostgreSQL", "Python", "SQL"
      ],
      "missing_skills": [],
      "all_detected_skills": [
        "CI/CD", "Docker", "FastAPI", "Git", "Kubernetes",
        "Pandas", "PostgreSQL", "Python", "Redis", "SQL"
      ],
      "soft_skills": [],
      "top_shared_terms": [
        "data", "python", "using", "postgresql", "services"
      ],
      "character_count": 1781,
      "rank": 1
    }
  ],
  "skills": {
    "required_skills": [
      "Docker", "FastAPI", "Git", "Kubernetes",
      "Pandas", "PostgreSQL", "Python", "SQL"
    ],
    "candidate_skill_frequencies": {
      "Docker": 5,
      "FastAPI": 3,
      "Git": 6,
      "Kubernetes": 2,
      "Pandas": 3,
      "PostgreSQL": 3,
      "Python": 6,
      "SQL": 7
    }
  },
  "eda_insights": {
    "total_raw_records": 10000,
    "experience_distribution": {
      "counts": {
        "0-2 Years": 4220,
        "3-5 Years": 4765,
        "6-10 Years": 899,
        "11-15 Years": 116,
        "16+ Years": 0
      },
      "percentages": {
        "0-2 Years": 42.2,
        "3-5 Years": 47.6,
        "6-10 Years": 9.0,
        "11-15 Years": 1.2,
        "16+ Years": 0.0
      },
      "median_years": 3.0,
      "mean_years": 3.1
    },
    "category_distribution": {
      "Technology": 2511,
      "Data & Analytics": 568,
      "Healthcare": 488,
      "Marketing & Sales": 463,
      "Engineering & Manufacturing": 435,
      "Creative & Design": 334,
      "Skilled Trades": 279,
      "Operations & Supply Chain": 266
    },
    "top_technical_skills": {
      "Communication": 2143,
      "Problem Solving": 2109,
      "Sql": 1162,
      "Leadership": 862,
      "Python": 731,
      "Javascript": 641,
      "Safety": 541,
      "Java": 513,
      "Research": 512,
      "Creativity": 505
    }
  },
  "configuration": {
    "weights": {
      "tfidf_weight": 0.4,
      "skill_weight": 0.6
    },
    "thresholds": {
      "shortlist_threshold": 70.0,
      "review_threshold": 50.0
    },
    "signals": {
      "shortlist": "SHORTLIST",
      "review": "REVIEW",
      "low_match": "LOW MATCH"
    }
  }
}
```
