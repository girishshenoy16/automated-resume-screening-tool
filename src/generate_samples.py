"""
Synthetic Multi-Format Resume Generator & Dataset Curation Script.

Ingests Kaggle source data from data/raw/, computes exploratory data analysis
(EDA) metrics into data/processed/eda_summary.json, curates 10 realistic
synthetic candidate personas into data/processed/curated_candidates.json,
and generates authentic multi-format resume documents (.pdf, .docx, .txt) in resumes/.
"""

import sys
import json
from collections import Counter
from pathlib import Path
import pandas as pd
from fpdf import FPDF
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Ensure repository root is on sys.path when executed directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src import config
except ImportError:
    import config

def compute_eda_summary() -> dict:
    """
    Compute distribution metrics from data/raw/training_data.csv and export
    structured EDA insights for reporting and dashboard visualization.
    """
    training_csv = config.RAW_DATA_DIR / "training_data.csv"
    if not training_csv.exists():
        raise FileNotFoundError(f"Training dataset not found at {training_csv}")

    df = pd.read_csv(training_csv)
    total_records = len(df)

    # 1. Experience Distribution
    exp_bins = [-1, 2, 5, 10, 15, 100]
    exp_labels = ["0-2 Years", "3-5 Years", "6-10 Years", "11-15 Years", "16+ Years"]
    df["Exp_Bracket"] = pd.cut(df["Experience Years"], bins=exp_bins, labels=exp_labels)
    exp_counts = df["Exp_Bracket"].value_counts()[exp_labels].to_dict()
    exp_pcts = {k: round((v / total_records) * 100, 1) for k, v in exp_counts.items()}

    # 2. Category Distribution
    cat_counts = df["Category"].value_counts().head(8).to_dict()

    # 3. Top Technical Skills
    with open(config.SKILLS_FILE, "r", encoding="utf-8") as f:
        skills_tax = json.load(f)
    tech_set = {s.lower() for s in skills_tax.get("technical_skills", [])}

    skill_counter = Counter()
    for skills_str in df["Skills"].dropna():
        parts = [s.strip() for s in str(skills_str).split("|") if s.strip()]
        for p in parts:
            if p.lower() in tech_set or len(parts) < 10:
                skill_counter[p.title()] += 1

    top_skills = dict(skill_counter.most_common(10))

    eda_summary = {
        "dataset_name": "AI Resume Analyzer – Job Role Prediction Dataset",
        "total_records": total_records,
        "features": list(df.columns),
        "experience_distribution": {
            "counts": exp_counts,
            "percentages": exp_pcts,
            "median_years": float(df["Experience Years"].median()),
            "mean_years": round(float(df["Experience Years"].mean()), 1)
        },
        "category_distribution": cat_counts,
        "top_technical_skills": top_skills
    }

    config.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(config.EDA_SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(eda_summary, f, indent=2)

    print(f"[*] EDA Summary successfully exported to: {config.EDA_SUMMARY_FILE}")
    return eda_summary

def get_curated_personas() -> list[dict]:
    """
    Define 10 grounded benchmark personas derived from Kaggle dataset records.
    Each persona possesses realistic work histories, education, and skill profiles.
    """
    return [
        {
            "id": "candidate_1",
            "filename": "candidate_1_alex_senior_python.pdf",
            "name": "Alex Morgan",
            "format": "PDF",
            "target_role": "Senior Python & Data Engineer",
            "experience_years": 7,
            "education": "Bachelor of Science in Computer Science, University of Washington",
            "email": "alex.morgan.tech@example.com",
            "phone": "+1 (555) 234-5678",
            "location": "Seattle, WA",
            "expected_tier": "SHORTLIST",
            "grounded_source": "training_data.csv - High-match Senior Python records",
            "skills": ["Python", "SQL", "Docker", "FastAPI", "Pandas", "PostgreSQL", "Git", "Kubernetes", "Redis", "CI/CD"],
            "summary": "Accomplished Senior Python & Data Engineer with 7+ years of experience designing high-throughput data ingestion pipelines, containerized microservice architectures, and analytical platforms. Expert in building fault-tolerant backend REST APIs with Python and FastAPI, tuning relational data models in PostgreSQL, and deploying container workloads across Kubernetes clusters.",
            "experience": [
                {
                    "title": "Senior Data Platform Engineer",
                    "company": "Apex Analytics Corp",
                    "period": "2021 - Present",
                    "details": [
                        "Architected scalable data ingestion services and high-throughput REST APIs using Python and FastAPI handling 20M+ events daily.",
                        "Designed, optimized, and maintained complex relational databases, analytical data warehouses, and schema migrations using SQL and PostgreSQL.",
                        "Constructed distributed data processing workflows and feature transformation pipelines leveraging Pandas.",
                        "Packaged, containerized, and deployed scalable microservices using Docker and managed container orchestration with Kubernetes.",
                        "Drove engineering excellence, code review practices, branch management, and automated release workflows using Git."
                    ]
                },
                {
                    "title": "Backend Software & Data Engineer",
                    "company": "CloudMatrix Solutions",
                    "period": "2018 - 2021",
                    "details": [
                        "Developed asynchronous backend services in Python connecting distributed caching layers in Redis and PostgreSQL.",
                        "Optimized database queries, indexing strategies, and pipeline execution latencies for large-scale enterprise datasets.",
                        "Collaborated in Agile sprints following strict Git feature-branch and code review standards."
                    ]
                }
            ]
        },
        {
            "id": "candidate_2",
            "filename": "candidate_2_priya_data_analyst.docx",
            "name": "Priya Patel",
            "format": "DOCX",
            "target_role": "Data Analyst / Analytics Engineer",
            "experience_years": 4,
            "education": "Master of Science in Business Analytics, Purdue University",
            "email": "priya.patel.analytics@example.com",
            "phone": "+1 (555) 345-6789",
            "location": "Chicago, IL",
            "expected_tier": "SHORTLIST",
            "grounded_source": "training_data.csv - Data Analyst records",
            "skills": ["Python", "SQL", "Pandas", "PostgreSQL", "Docker", "Git", "FastAPI", "Power BI", "Statistics"],
            "summary": "Analytical Data Engineer & Analyst with 4 years of expertise translating raw transactional data into high-performance pipelines and actionable business intelligence. Proficient in advanced SQL, data transformation pipelines using Python and Pandas, relational schemas in PostgreSQL, containerization with Docker, and REST APIs using FastAPI.",
            "experience": [
                {
                    "title": "Data Engineer & Senior Analyst",
                    "company": "Insight Metrics Group",
                    "period": "2022 - Present",
                    "details": [
                        "Constructed automated data processing workflows and ETL transformation pipelines leveraging Python and Pandas.",
                        "Engineered relational database models and complex analytical queries in PostgreSQL and SQL.",
                        "Containerized analytics services using Docker and built data querying REST APIs with FastAPI.",
                        "Managed branch deployments, version control, and collaborative code reviews via Git."
                    ]
                },
                {
                    "title": "Junior Data Analyst",
                    "company": "FirstPoint Financial",
                    "period": "2020 - 2022",
                    "details": [
                        "Extracted and scrubbed financial transaction records utilizing SQL databases and Python.",
                        "Designed executive Power BI dashboards and documented departmental analytics pipelines."
                    ]
                }
            ]
        },
        {
            "id": "candidate_3",
            "filename": "candidate_3_david_ml_intern.pdf",
            "name": "David Kim",
            "format": "PDF",
            "target_role": "Machine Learning Engineer / Data Scientist",
            "experience_years": 1,
            "education": "Bachelor of Science in Artificial Intelligence, Carnegie Mellon University",
            "email": "david.kim.ai@example.com",
            "phone": "+1 (555) 456-7890",
            "location": "Pittsburgh, PA",
            "expected_tier": "REVIEW",
            "grounded_source": "training_data.csv - Machine Learning Engineer records",
            "skills": ["Python", "SQL", "Docker", "Pandas", "Git", "PyTorch", "TensorFlow", "Machine Learning"],
            "summary": "Enthusiastic Machine Learning Engineer with 1 year of hands-on experience developing deep learning architectures and statistical models. Solid foundation in Python, data processing with Pandas, database queries in SQL, Docker containers, and reproducible experimentation.",
            "experience": [
                {
                    "title": "Machine Learning Research Intern",
                    "company": "Cognitive AI Labs",
                    "period": "2023 - 2024",
                    "details": [
                        "Implemented transformer and convolutional neural network models using PyTorch, TensorFlow, and Python.",
                        "Preprocessed high-dimensional datasets using Pandas and optimized data loading using SQL.",
                        "Containerized machine learning inference pipelines using Docker for reproducible testing environments.",
                        "Tracked model experiments and codebase revisions following Git version control best practices."
                    ]
                }
            ]
        },
        {
            "id": "candidate_4",
            "filename": "candidate_4_emily_bi_analyst.docx",
            "name": "Emily Chen",
            "format": "DOCX",
            "target_role": "Business Intelligence Analyst",
            "experience_years": 5,
            "education": "Bachelor of Science in Information Systems, University of Illinois",
            "email": "emily.chen.bi@example.com",
            "phone": "+1 (555) 567-8901",
            "location": "Dallas, TX",
            "expected_tier": "REVIEW",
            "grounded_source": "training_data.csv - BI Analyst records",
            "skills": ["SQL", "Power BI", "Tableau", "Data Warehousing", "Excel", "Data Science"],
            "summary": "Results-oriented Business Intelligence Analyst with 5 years of experience architecting tabular data models, star-schema data marts, and reporting dashboards. Expert in SQL data transformation, ETL management, and Power BI visualization.",
            "experience": [
                {
                    "title": "Lead BI Analyst",
                    "company": "Vanguard Retail Enterprises",
                    "period": "2021 - Present",
                    "details": [
                        "Architected central enterprise data warehouse marts using advanced SQL stored procedures.",
                        "Deployed automated self-service Power BI workspaces across 6 operational divisions.",
                        "Spearheaded data governance and business KPI standardization across the company."
                    ]
                },
                {
                    "title": "Data Visualization Specialist",
                    "company": "Apex Logistics",
                    "period": "2019 - 2021",
                    "details": [
                        "Constructed operational supply chain KPI tracking views in Tableau.",
                        "Validated relational database schemas and performed data reconciliation in Excel."
                    ]
                }
            ]
        },
        {
            "id": "candidate_5",
            "filename": "candidate_5_marcus_backend_dev.pdf",
            "name": "Marcus Vance",
            "format": "PDF",
            "target_role": "Backend Systems Developer",
            "experience_years": 6,
            "education": "Bachelor of Science in Software Engineering, Georgia Tech",
            "email": "marcus.vance.dev@example.com",
            "phone": "+1 (555) 678-9012",
            "location": "Atlanta, GA",
            "expected_tier": "REVIEW",
            "grounded_source": "training_data.csv - Backend Developer records",
            "skills": ["Python", "SQL", "PostgreSQL", "Docker", "Git", "Kubernetes", "Linux", "Redis", "Flask"],
            "summary": "Backend Software Developer with 6 years of expertise building robust web services, database architectures, and asynchronous message processors. Strong focus on Python backend engineering, PostgreSQL schema design, SQL query tuning, Docker containerization, and Kubernetes cluster orchestration.",
            "experience": [
                {
                    "title": "Senior Backend Developer",
                    "company": "Nexus Web Systems",
                    "period": "2020 - Present",
                    "details": [
                        "Developed microservices in Python utilizing Flask and PostgreSQL for core transaction flows.",
                        "Containerized backend applications with Docker and deployed workloads onto Kubernetes clusters.",
                        "Engineered high-performance relational database schemas and executed complex SQL queries.",
                        "Maintained continuous integration workflows and managed branch deployments via Git."
                    ]
                }
            ]
        },
        {
            "id": "candidate_6",
            "filename": "candidate_6_elena_fullstack.txt",
            "name": "Elena Rostova",
            "format": "TXT",
            "target_role": "Full Stack Developer",
            "experience_years": 5,
            "education": "Bachelor of Science in Computer Science, State University",
            "email": "elena.rostova.fs@example.com",
            "phone": "+1 (555) 789-0123",
            "location": "Boston, MA",
            "expected_tier": "REVIEW",
            "grounded_source": "test_resumes.json - Synthetic benchmark persona derived from relevant profile",
            "skills": ["Python", "SQL", "Docker", "Git", "FastAPI", "JavaScript", "Node.js", "HTML/CSS"],
            "summary": "Versatile Full Stack Developer with 5 years of full lifecycle software engineering experience across frontend web technologies and backend services. Proficient in Python, building REST APIs with FastAPI, SQL database operations, Docker containerization, and Git.",
            "experience": [
                {
                    "title": "Full Stack Software Engineer",
                    "company": "BrightCore Technologies",
                    "period": "2021 - Present",
                    "details": [
                        "Built backend microservices and REST APIs using Python, FastAPI, and relational SQL databases.",
                        "Constructed responsive user interfaces with JavaScript and HTML/CSS.",
                        "Containerized web application components using Docker and managed code reviews using Git."
                    ]
                }
            ]
        },
        {
            "id": "candidate_7",
            "filename": "candidate_7_sarah_frontend_dev.docx",
            "name": "Sarah Jenkins",
            "format": "DOCX",
            "target_role": "Frontend UI/UX Engineer",
            "experience_years": 3,
            "education": "Bachelor of Fine Arts in Web Design, Pratt Institute",
            "email": "sarah.jenkins.ui@example.com",
            "phone": "+1 (555) 890-1234",
            "location": "Brooklyn, NY",
            "expected_tier": "LOW MATCH",
            "grounded_source": "training_data.csv - Frontend Developer records",
            "skills": ["JavaScript", "React", "HTML/CSS", "UI/UX"],
            "summary": "Creative and user-focused Frontend Developer with 3 years of experience building modern Single Page Applications (SPAs) and component libraries. Dedicated to pixel-perfect design, accessibility standards, and intuitive user interfaces.",
            "experience": [
                {
                    "title": "Frontend Developer",
                    "company": "PixelCraft Studios",
                    "period": "2022 - Present",
                    "details": [
                        "Developed high-traffic responsive user interfaces in React, JavaScript, and modern HTML/CSS.",
                        "Conducted comprehensive usability testing and implemented UX wireframes from Figma designs."
                    ]
                }
            ]
        },
        {
            "id": "candidate_8",
            "filename": "candidate_8_carlos_career_changer.txt",
            "name": "Carlos Gomez",
            "format": "TXT",
            "target_role": "Junior Tech Associate",
            "experience_years": 1,
            "education": "Certificate in Applied Programming, DevAcademy; BA in Communications",
            "email": "carlos.gomez.transition@example.com",
            "phone": "+1 (555) 901-2345",
            "location": "Austin, TX",
            "expected_tier": "LOW MATCH",
            "grounded_source": "training_data.csv - Junior Transition profiles",
            "skills": ["Python", "SQL", "Excel", "Communication", "Problem Solving"],
            "summary": "Motivated career changer transitioning from communications to technology following intensive coursework in Python programming and relational databases. Strong interpersonal abilities, analytical curiosity, and commitment to learning.",
            "experience": [
                {
                    "title": "Junior Operations & Data Assistant",
                    "company": "Beacon Communications",
                    "period": "2023 - Present",
                    "details": [
                        "Wrote basic Python automation scripts to parse internal CSV reports and log records.",
                        "Queried organizational databases using basic SQL select statements and performed reconciliations in Excel."
                    ]
                }
            ]
        },
        {
            "id": "candidate_9",
            "filename": "candidate_9_aisha_fresh_graduate.docx",
            "name": "Aisha Khan",
            "format": "DOCX",
            "target_role": "Associate Software Engineer",
            "experience_years": 0,
            "education": "Bachelor of Science in Computer Science, Ohio State University (Recent Graduate)",
            "email": "aisha.khan.grad@example.com",
            "phone": "+1 (555) 012-3456",
            "location": "Columbus, OH",
            "expected_tier": "LOW MATCH",
            "grounded_source": "training_data.csv - 0-Year CS Graduate records",
            "skills": ["C++", "Java", "Linux", "Git"],
            "summary": "Recent Computer Science graduate with strong academic grounding in object-oriented programming, data structures, algorithms, and operating system concepts. Seeking an entry-level software engineering role.",
            "experience": [
                {
                    "title": "Undergraduate Teaching Assistant",
                    "company": "Department of Computer Science",
                    "period": "2023 - 2024",
                    "details": [
                        "Guided 60+ students through lab assignments covering C++, memory allocation, and data structures.",
                        "Managed course assignment repositories and pull requests on Git within a Linux laboratory environment."
                    ]
                }
            ]
        },
        {
            "id": "candidate_10",
            "filename": "candidate_10_jason_mechanical_eng.pdf",
            "name": "Jason Miller",
            "format": "PDF",
            "target_role": "Mechanical Systems Engineer",
            "experience_years": 4,
            "education": "Bachelor of Science in Mechanical Engineering, Penn State University",
            "email": "jason.miller.mech@example.com",
            "phone": "+1 (555) 123-4567",
            "location": "Detroit, MI",
            "expected_tier": "LOW MATCH",
            "grounded_source": "training_data.csv - Mechanical Engineering records",
            "skills": ["CAD", "MATLAB", "Thermodynamics", "Teamwork"],
            "summary": "Mechanical Design Engineer with 4 years of experience specializing in CAD drafting, finite element analysis, and thermodynamic system optimization. Dedicated team player experienced in manufacturing tolerances.",
            "experience": [
                {
                    "title": "Mechanical Systems Engineer",
                    "company": "Apex Propulsion Systems",
                    "period": "2021 - Present",
                    "details": [
                        "Designed parametric 3D mechanical assemblies and tooling fixtures using CAD modeling tools.",
                        "Modeled fluid and thermodynamic heat transfer simulations in MATLAB.",
                        "Collaborated with cross-discipline manufacturing teams to resolve assembly line quality defects."
                    ]
                }
            ]
        }
    ]

# ==============================================================================
# Multi-Format Resume Renderers
# ==============================================================================

def generate_pdf_resume(filepath: Path, p: dict):
    """Render structured candidate resume to a high-quality PDF using fpdf2."""
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Header Name
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(0, 10, p["name"], new_x="LMARGIN", new_y="NEXT")
    
    # Subheader Info
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(74, 85, 104)
    contact_line = f"{p['email']}  |  {p['phone']}  |  {p['location']}"
    pdf.cell(0, 6, contact_line, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Divider line
    pdf.set_draw_color(203, 213, 225)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    # Professional Summary
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(43, 108, 176)
    pdf.cell(0, 7, "PROFESSIONAL SUMMARY", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(45, 55, 72)
    pdf.multi_cell(0, 5, p["summary"])
    pdf.ln(4)

    # Technical Skills
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(43, 108, 176)
    pdf.cell(0, 7, "TECHNICAL SKILLS & COMPETENCIES", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(45, 55, 72)
    skills_text = ", ".join(p["skills"])
    pdf.multi_cell(0, 5, skills_text)
    pdf.ln(4)

    # Professional Experience
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(43, 108, 176)
    pdf.cell(0, 7, "PROFESSIONAL EXPERIENCE", new_x="LMARGIN", new_y="NEXT")

    for exp in p["experience"]:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(26, 32, 44)
        pdf.cell(0, 6, f"{exp['title']} - {exp['company']} ({exp['period']})", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(45, 55, 72)
        for detail in exp["details"]:
            pdf.cell(6, 5, "-", new_x="RIGHT", new_y="TOP")
            pdf.multi_cell(0, 5, detail)
            pdf.ln(1)
        pdf.ln(2)

    # Education
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(43, 108, 176)
    pdf.cell(0, 7, "EDUCATION", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(45, 55, 72)
    pdf.multi_cell(0, 5, p["education"])

    pdf.output(str(filepath))

def generate_docx_resume(filepath: Path, p: dict):
    """Render structured candidate resume to a clean Microsoft Word (.docx) file."""
    doc = docx.Document()
    
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Name Header
    h1 = doc.add_heading(p["name"], level=0)
    h1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in h1.runs:
        run.font.size = Pt(20)
        run.font.color.rgb = RGBColor(26, 54, 93)

    # Contact Info
    contact = doc.add_paragraph(f"{p['email']}  |  {p['phone']}  |  {p['location']}")
    contact.runs[0].font.size = Pt(9.5)
    contact.runs[0].font.color.rgb = RGBColor(100, 116, 139)

    # Summary Section
    h_sum = doc.add_heading("PROFESSIONAL SUMMARY", level=1)
    for run in h_sum.runs:
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(43, 108, 176)
    p_sum = doc.add_paragraph(p["summary"])
    p_sum.runs[0].font.size = Pt(10)

    # Skills Section
    h_sk = doc.add_heading("TECHNICAL SKILLS & COMPETENCIES", level=1)
    for run in h_sk.runs:
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(43, 108, 176)
    p_sk = doc.add_paragraph(", ".join(p["skills"]))
    p_sk.runs[0].font.size = Pt(10)

    # Experience Section
    h_exp = doc.add_heading("PROFESSIONAL EXPERIENCE", level=1)
    for run in h_exp.runs:
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(43, 108, 176)

    for exp in p["experience"]:
        p_role = doc.add_paragraph()
        r_title = p_role.add_run(f"{exp['title']} — {exp['company']}")
        r_title.bold = True
        r_title.font.size = Pt(10.5)
        r_date = p_role.add_run(f"  ({exp['period']})")
        r_date.italic = True
        r_date.font.size = Pt(9.5)

        for detail in exp["details"]:
            bp = doc.add_paragraph(detail, style="List Bullet")
            bp.runs[0].font.size = Pt(9.5)

    # Education Section
    h_edu = doc.add_heading("EDUCATION", level=1)
    for run in h_edu.runs:
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(43, 108, 176)
    p_edu = doc.add_paragraph(p["education"])
    p_edu.runs[0].font.size = Pt(10)

    doc.save(str(filepath))

def generate_txt_resume(filepath: Path, p: dict):
    """Render structured candidate resume to a plain UTF-8 text document."""
    lines = [
        p["name"],
        f"{p['email']} | {p['phone']} | {p['location']}",
        "-" * 70,
        "",
        "PROFESSIONAL SUMMARY",
        "-" * 70,
        p["summary"],
        "",
        "TECHNICAL SKILLS & COMPETENCIES",
        "-" * 70,
        ", ".join(p["skills"]),
        "",
        "PROFESSIONAL EXPERIENCE",
        "-" * 70,
    ]

    for exp in p["experience"]:
        lines.append(f"{exp['title']} - {exp['company']} ({exp['period']})")
        for detail in exp["details"]:
            lines.append(f"  * {detail}")
        lines.append("")

    lines.extend([
        "EDUCATION",
        "-" * 70,
        p["education"],
        ""
    ])

    content = "\n".join(lines)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

# ==============================================================================
# Main Generator Orchestrator
# ==============================================================================

def main():
    print("=" * 70)
    print("AI Resume Screening Tool — Resume Generator & Dataset Curation")
    print("=" * 70)

    # 1. Compute & Save EDA Metrics
    print("[1/3] Ingesting raw Kaggle records and computing EDA summary...")
    compute_eda_summary()

    # 2. Curate 10 Grounded Personas
    print("[2/3] Curating 10 grounded synthetic benchmark personas...")
    personas = get_curated_personas()

    with open(config.CURATED_CANDIDATES_FILE, "w", encoding="utf-8") as f:
        json.dump(personas, f, indent=2)
    print(f"[*] Curated candidate profiles exported to: {config.CURATED_CANDIDATES_FILE}")

    # 3. Render Multi-Format Documents into resumes/
    print("[3/3] Rendering multi-format resume documents into resumes/...")
    config.RESUMES_DIR.mkdir(parents=True, exist_ok=True)

    counts = {"PDF": 0, "DOCX": 0, "TXT": 0}
    for p in personas:
        out_path = config.RESUMES_DIR / p["filename"]
        fmt = p["format"].upper()
        if fmt == "PDF":
            generate_pdf_resume(out_path, p)
            counts["PDF"] += 1
        elif fmt == "DOCX":
            generate_docx_resume(out_path, p)
            counts["DOCX"] += 1
        elif fmt == "TXT":
            generate_txt_resume(out_path, p)
            counts["TXT"] += 1
        print(f"    -> Generated [{fmt}]: {p['filename']}")

    print("-" * 70)
    print(f"[*] Completed resume generation: {counts['PDF']} PDFs, {counts['DOCX']} DOCXs, {counts['TXT']} TXTs (Total: {len(personas)})")
    print("=" * 70)

if __name__ == "__main__":
    main()
