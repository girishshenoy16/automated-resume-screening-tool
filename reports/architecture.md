# Technical Architecture & Algorithmic Specifications (`architecture.md`)

## 1. System Overview & Architectural Paradigm

The **Automated Resume Screening Tool / Resume Screening & ATS Platform** is an enterprise-grade recruiter decision-support system designed to automate high-volume resume parsing, skill matching, lexical relevance analysis, and candidate screening triage.

The system is architected around two operational modes:
1. **Batch Screening Pipeline (Python)**: An automated processing engine that ingests multi-format candidate resumes (`.pdf`, `.docx`, `.txt`), parses and extracts text, matches skills against a target Job Description (JD), computes TF-IDF textual similarity, assigns transparent decision signals, outputs audit reports (`.csv`, `.json`), generates 5 static plots (`outputs/plots/`), and compiles the data contract for GitHub Pages (`docs/data/dashboard_data.json`).
2. **Interactive Live ATS Platform (Browser-Compatible Client)**: A static, client-side web application hosted on GitHub Pages (`docs/index.html`) featuring:
   - **Tab 1: Screening Dashboard**: An executive dashboard presenting cohort KPIs, a searchable/filterable candidate leaderboard, candidate intelligence drawers with full score decomposition, and 4 interactive Chart.js visualizations.
   - **Tab 2: Live ATS Checker**: An interactive single-candidate screening interface allowing recruiters to specify target requisition details, upload or paste resume text, run in-browser text extraction and TF-IDF matching, and inspect detailed skill gap explainability.

---

## 2. End-to-End System Architecture

```text
+-----------------------------------------------------------------------------------------------+
|                                    DATA INGESTION LAYER                                       |
|                                                                                               |
|   +--------------------------+       +-------------------------+       +-------------------+  |
|   |  Kaggle Source Dataset   |       | Benchmark Requisition   |       | Curated Taxonomy  |  |
|   |  (10,000 raw records)    |       | (data/job_description)  |       | (37 Tech, 7 Soft) |  |
|   +------------+-------------+       +------------+------------+       +---------+---------+  |
|                |                                  |                              |            |
+----------------|----------------------------------|------------------------------|------------+
                 |                                  |                              |
                 v                                  v                              v
+-----------------------------------------------------------------------------------------------+
|                                    PROCESSING ENGINE LAYER                                    |
|                                                                                               |
|   +---------------------------------------------------------------------------------------+   |
|   | 1. Document Extraction Engine (src/extractor.py)                                       |   |
|   |    Multi-Format Parser: PDF (pdfplumber + pypdf) | Word (.docx) | Plain Text (.txt)   |   |
|   +-------------------------------------------+-------------------------------------------+   |
|                                               |                                               |
|                                               v                                               |
|   +---------------------------------------------------------------------------------------+   |
|   | 2. NLP Text Normalization Engine (src/cleaner.py)                                     |   |
|   |    URL/Email Stripping -> Token Masking -> Lowercase -> Punctuation Strip -> Unmask   |   |
|   |    Protected Programming Tokens: C++, C#, .NET, Node.js, CI/CD                        |   |
|   +-------------------+-----------------------------------------------+-------------------+   |
|                       |                                               |                       |
|                       v                                               v                       |
|   +---------------------------------------+       +---------------------------------------+   |
|   | 3. Boundary-Safe Skill Extractor      |       | 4. Lexical TF-IDF Relevance Engine    |   |
|   |    (src/skill_extractor.py)           |       |    (src/matcher.py)                   |   |
|   |    - Boundary lookaround regex        |       |    - Joint (1,2)-gram vocabulary      |   |
|   |    - Dynamic JD-based denominator     |       |    - Sublinear TF scaling             |   |
|   |    - Soft skills isolated             |       |    - Cosine similarity in vector space|   |
|   +-------------------+-------------------+       +-------------------+-------------------+   |
|                       |                                               |                       |
|                       +-----------------------+-----------------------+                       |
|                                               |                                               |
|                                               v                                               |
|   +---------------------------------------------------------------------------------------+   |
|   | 5. Hybrid Composite Scoring & Ranking Engine (src/reporter.py)                        |   |
|   |    Score = (0.40 * TF-IDF Relevance) + (0.60 * Technical Skill Match)                 |   |
|   |    Screening Signals: Shortlist (>=70%) | Review (50-69.9%) | Low Match (<50%)        |   |
|   +-------------------------------------------+-------------------------------------------+   |
|                                               |                                               |
+-----------------------------------------------|-----------------------------------------------+
                                                |
                                                v
+-----------------------------------------------------------------------------------------------+
|                                   OUTPUT & PRESENTATION LAYER                                 |
|                                                                                               |
|   +---------------------------------------+       +---------------------------------------+   |
|   | Tabular & Audit Reports               |       | Static Analytical Plots (outputs/)    |   |
|   | - outputs/screened_candidates_report  |       | - candidate_score_distribution.png    |   |
|   | - outputs/screening_summary.json      |       | - skill_gap_analysis.png              |   |
|   +---------------------------------------+       | - experience_distribution_eda.png     |   |
|                                                   | - category_distribution_eda.png       |   |
|   +---------------------------------------+       | - top_technical_skills_eda.png        |   |
|   | GitHub Pages Executive Platform (docs/)|       +---------------------------------------+   |
|   | - Tab 1: Screening Dashboard          |                                                   |
|   | - Tab 2: Live ATS Checker Engine      |                                                   |
|   | - docs/data/dashboard_data.json       |                                                   |
|   +---------------------------------------+                                                   |
+-----------------------------------------------------------------------------------------------+
```

---

## 3. Mathematical Formulations

### 3.1 Sublinear TF-IDF Vector Space Model
To quantify textual alignment without term saturation or length distortion, the lexical engine represents documents in a joint $(1, 2)$-gram vector space with sublinear term frequency scaling:

$$\text{tf}_{\text{sublinear}}(t, d) = 1 + \ln(\text{tf}(t, d)) \quad \text{for } \text{tf}(t, d) > 0$$

Inverse Document Frequency (IDF) over the joint corpus $D = \{d_{\text{JD}}, d_{\text{Resume}}\}$ is defined as:

$$\text{idf}(t, D) = \ln\left(\frac{N + 1}{\text{df}(t) + 1}\right) + 1$$

The resulting document vectors $\vec{v}_{\text{JD}}$ and $\vec{v}_{\text{Resume}}$ are $L_2$-normalized:

$$\hat{v} = \frac{\vec{v}}{\|\vec{v}\|_2} = \frac{\vec{v}}{\sqrt{\sum_{i=1}^{M} v_i^2}}$$

Cosine similarity between the target JD and candidate resume is bounded in $[0.0, 1.0]$ and scaled to a percentage $S_{\text{tfidf}} \in [0.0, 100.0]\%$:

$$\text{Cosine Similarity}(\vec{v}_{\text{JD}}, \vec{v}_{\text{Resume}}) = \frac{\vec{v}_{\text{JD}} \cdot \vec{v}_{\text{Resume}}}{\|\vec{v}_{\text{JD}}\|_2 \|\vec{v}_{\text{Resume}}\|_2}$$

$$S_{\text{tfidf}} = \min\left(100.0, \max\left(0.0, \text{Cosine Similarity} \times 100\right)\right)$$

### 3.2 Dynamic JD-Based Technical Skill Match Ratio
Skill matching is strictly evaluated against the **technical skills required by the active Job Description**, avoiding inflated denominators from unused taxonomy terms:

$$\text{Skill Match Ratio} = \frac{|S_{\text{candidate\_tech}} \cap S_{\text{JD\_tech}}|}{|S_{\text{JD\_tech}}|}$$

$$S_{\text{skill}} = \text{round}\left(\text{Skill Match Ratio} \times 100.0, 2\right)$$

- **Dynamic Denominator**: If a requisition requires 8 skills, the denominator is 8; if a requisition requires 4 skills, the denominator is 4. The complete 37-skill taxonomy is never used as the denominator.
- **Irrelevant Skill Immunity**: Candidate skills present on the resume that are not in $S_{\text{JD\_tech}}$ do not increase the match ratio.
- **Soft Skills Exclusion**: Soft skills are classified as informational and excluded from numerical scoring.

### 3.3 Hybrid Composite Score
The final screening score balances broad contextual relevance with hard technical requirements:

$$\text{Composite Score} = \left(w_{\text{tfidf}} \times S_{\text{tfidf}}\right) + \left(w_{\text{skill}} \times S_{\text{skill}}\right)$$

Where:
- $w_{\text{tfidf}} = 0.40$ (40% Textual Relevance)
- $w_{\text{skill}} = 0.60$ (60% Technical Skill Match)
- $w_{\text{tfidf}} + w_{\text{skill}} = 1.00$

### 3.4 Decision Signal Thresholds & Neutral Alignment Labels
Candidate profiles are triaged into actionable screening cohorts:

$$\text{Decision Signal}(S_{\text{composite}}) = \begin{cases}
\text{SHORTLIST} \ (\text{High Match}) & \text{if } S_{\text{composite}} \ge 70.0\% \\
\text{REVIEW} \ (\text{Moderate Match}) & \text{if } 50.0\% \le S_{\text{composite}} < 70.0\% \\
\text{LOW MATCH} \ (\text{Low Match}) & \text{if } S_{\text{composite}} < 50.0\%
\end{cases}$$

---

## 4. Token-Safe NLP & Regex Mechanisms

Standard regex word-boundary anchors (`\b`) fail on programming tokens containing non-alphanumeric symbols (`+`, `#`, `.`, `/`). To prevent token mangling or false positives, the cleaner and skill extractor use two complementary mechanisms:

### 4.1 Masked Normalization (`src/cleaner.py`)
1. Before punctuation stripping, protected tokens are replaced with unambiguous alphanumeric masks:
   - `(?i)\bc\+\+` $\rightarrow$ `__TOKEN_CPP__`
   - `(?i)\bc\#` $\rightarrow$ `__TOKEN_CSHARP__`
   - `(?i)(?<!\w)\.net\b` $\rightarrow$ `__TOKEN_DOTNET__`
   - `(?i)\bnode\.js\b` $\rightarrow$ `__TOKEN_NODEJS__`
   - `(?i)\bci/cd\b` $\rightarrow$ `__TOKEN_CICD__`
2. Document text is converted to lowercase and non-alphanumeric punctuation is stripped (`[^\w\s]`).
3. Tokens are unmasked back to canonical lowercase forms (`c++`, `c#`, `.net`, `node.js`, `ci/cd`).

### 4.2 Lookaround Boundary Assertions (`src/skill_extractor.py`)
Custom compiled regex patterns use negative lookahead and lookbehind assertions:
- **C++**: `(?<![\w\+])c\+\+(?![\w\+])` (Prevents matching inside `C+++` or alphanumeric words)
- **C#**: `(?<![\w\#])c\#(?![\w\#])`
- **.NET**: `(?<![\w\.])\.net(?![\w\.])` (Distinguishes `.net` from words ending in `net` like `internet`, `telnet`)
- **Java vs. JavaScript**: Canonical word boundary `\bjava\b` guarantees that `"JavaScript developer"` matches only `JavaScript` and does not trigger a false match for `Java`.

---

## 5. Client-Side Browser Engine Architecture (`docs/app.js`)

To enable the **Tab 2 Live ATS Checker** on GitHub Pages without requiring a Python server:
1. **Document Parsers**:
   - PDF parsing: `pdfjsLib` (PDF.js v3.11.174) extracts text page-by-page.
   - Word parsing: `mammoth.js` (v1.8.0) extracts text from `.docx` array buffers.
   - Text parsing: Standard HTML5 `FileReader` API.
2. **Text Normalization**: Port of `clean_text()` in JavaScript mirrors token masking and regex replacement.
3. **TF-IDF Vectorizer**: Pure-browser JavaScript implementation with unigram/bigram tokenization, sublinear TF ($1 + \ln(\text{tf})$), IDF calculation, and cosine similarity.
4. **Dynamic Explainability**: Populates hero match score, signal badges, metric bars, matched/missing skill chips, and shared lexical terms in real-time.
