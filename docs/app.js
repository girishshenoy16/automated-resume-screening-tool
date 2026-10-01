/* ═══════════════════════════════════════════════════════════════
   AUTOMATED RESUME SCREENING TOOL — EXECUTIVE ATS PLATFORM
   Phase 10: Tab 1 (Screening Dashboard) + Tab 2 (Live ATS Checker)
   ═══════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  /* ── Configure PDF.js Worker ──────────────────────────────── */
  if (typeof window !== 'undefined' && window.pdfjsLib) {
    window.pdfjsLib.GlobalWorkerOptions.workerSrc =
      'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
  }

  /* ── State ────────────────────────────────────────────────── */
  let DATA = null;                  // full dashboard_data.json
  let TAXONOMY = null;              // skills_taxonomy.json
  let candidates = [];              // candidates array
  let sortKey = 'rank';             // current sort column
  let sortAsc = true;               // sort direction
  let activeFilter = 'ALL';         // signal filter
  let searchQuery = '';             // search string
  let selectedFile = null;          // file selected in Tab 2
  let resumeInputMode = 'upload';   // 'upload' or 'paste'

  // Default embedded skills taxonomy fallback
  const DEFAULT_DASHBOARD_DATA = {"metadata": {"generated_at": "2026-09-18T14:57:51.123189+00:00","pipeline_version": "1.0.0","tool_name": "Automated Resume Screening Tool","architecture": "Hybrid Lexical TF-IDF & Boundary-Safe Skill Matching Engine"},"job": {"title": "Senior Python & Data Engineer","department": "Data Platform Engineering","required_skills_count": 8,"required_skills": ["Docker","FastAPI","Git","Kubernetes","Pandas","PostgreSQL","Python","SQL"]},"summary": {"total_candidates": 10,"shortlist_count": 1,"review_count": 2,"low_match_count": 7,"average_composite_score": 31.2,"shortlist_percentage": 10.0},"candidates": [{"candidate_id": "cand_02","candidate_name": "Alex Morgan","file_name": "candidate_1_alex_senior_python.pdf","format": "PDF","composite_score": 75.91,"signal": "SHORTLIST","alignment_label": "High Match","skill_match_percentage": 100.0,"tfidf_percentage": 39.78,"matched_skills": ["Docker","FastAPI","Git","Kubernetes","Pandas","PostgreSQL","Python","SQL"],"missing_skills": [],"all_detected_skills": ["CI/CD","Docker","FastAPI","Git","Kubernetes","Pandas","PostgreSQL","Python","Redis","SQL"],"soft_skills": [],"top_shared_terms": ["data","python","using","postgresql","services"],"character_count": 1781,"rank": 1},{"candidate_id": "cand_03","candidate_name": "Priya Patel","file_name": "candidate_2_priya_data_analyst.docx","format": "DOCX","composite_score": 59.69,"signal": "REVIEW","alignment_label": "Moderate Match","skill_match_percentage": 87.5,"tfidf_percentage": 17.97,"matched_skills": ["Docker","FastAPI","Git","Pandas","PostgreSQL","Python","SQL"],"missing_skills": ["Kubernetes"],"all_detected_skills": ["Docker","FastAPI","Git","Pandas","PostgreSQL","Power BI","Python","SQL","Statistics"],"soft_skills": [],"top_shared_terms": ["data","python","using","pipelines","sql"],"character_count": 1337,"rank": 2},{"candidate_id": "cand_06","candidate_name": "Marcus Vance","file_name": "candidate_5_marcus_backend_dev.pdf","format": "PDF","composite_score": 50.58,"signal": "REVIEW","alignment_label": "Moderate Match","skill_match_percentage": 75.0,"tfidf_percentage": 13.96,"matched_skills": ["Docker","Git","Kubernetes","PostgreSQL","Python","SQL"],"missing_skills": ["FastAPI","Pandas"],"all_detected_skills": ["Docker","Flask","Git","Kubernetes","Linux","PostgreSQL","Python","Redis","SQL"],"soft_skills": [],"top_shared_terms": ["python","engineering","backend","sql","postgresql"],"character_count": 1018,"rank": 3},{"candidate_id": "cand_07","candidate_name": "Elena Rostova","file_name": "candidate_6_elena_fullstack.txt","format": "TXT","composite_score": 43.45,"signal": "LOW MATCH","alignment_label": "Low Match","skill_match_percentage": 62.5,"tfidf_percentage": 14.88,"matched_skills": ["Docker","FastAPI","Git","Python","SQL"],"missing_skills": ["Kubernetes","Pandas","PostgreSQL"],"all_detected_skills": ["Docker","FastAPI","Git","HTML/CSS","JavaScript","Node.js","Python","SQL"],"soft_skills": [],"top_shared_terms": ["python","using","sql","git","fastapi"],"character_count": 1245,"rank": 4},{"candidate_id": "cand_04","candidate_name": "David Kim","file_name": "candidate_3_david_ml_intern.pdf","format": "PDF","composite_score": 42.2,"signal": "LOW MATCH","alignment_label": "Low Match","skill_match_percentage": 62.5,"tfidf_percentage": 11.76,"matched_skills": ["Docker","Git","Pandas","Python","SQL"],"missing_skills": ["FastAPI","Kubernetes","PostgreSQL"],"all_detected_skills": ["Docker","Git","Machine Learning","Pandas","PyTorch","Python","SQL","TensorFlow"],"soft_skills": [],"top_shared_terms": ["using","data","python","sql","pandas"],"character_count": 1043,"rank": 5},{"candidate_id": "cand_09","candidate_name": "Carlos Gomez","file_name": "candidate_8_carlos_career_changer.txt","format": "TXT","composite_score": 17.52,"signal": "LOW MATCH","alignment_label": "Low Match","skill_match_percentage": 25.0,"tfidf_percentage": 6.3,"matched_skills": ["Python","SQL"],"missing_skills": ["Docker","FastAPI","Git","Kubernetes","Pandas","PostgreSQL"],"all_detected_skills": ["Excel","Python","SQL"],"soft_skills": ["Communication","Problem Solving"],"top_shared_terms": ["python","data","sql","using","relational"],"character_count": 1157,"rank": 6},{"candidate_id": "cand_10","candidate_name": "Aisha Khan","file_name": "candidate_9_aisha_fresh_graduate.docx","format": "DOCX","composite_score": 10.24,"signal": "LOW MATCH","alignment_label": "Low Match","skill_match_percentage": 12.5,"tfidf_percentage": 6.84,"matched_skills": ["Git"],"missing_skills": ["Docker","FastAPI","Kubernetes","Pandas","PostgreSQL","Python","SQL"],"all_detected_skills": ["C++","Git","Java","Linux"],"soft_skills": [],"top_shared_terms": ["data","git","engineering","science","computer science"],"character_count": 755,"rank": 7},{"candidate_id": "cand_05","candidate_name": "Emily Chen","file_name": "candidate_4_emily_bi_analyst.docx","format": "DOCX","composite_score": 9.9,"signal": "LOW MATCH","alignment_label": "Low Match","skill_match_percentage": 12.5,"tfidf_percentage": 5.99,"matched_skills": ["SQL"],"missing_skills": ["Docker","FastAPI","Git","Kubernetes","Pandas","PostgreSQL","Python"],"all_detected_skills": ["Data Science","Data Warehousing","Excel","Power BI","SQL","Tableau"],"soft_skills": [],"top_shared_terms": ["data","sql","using","science","experience"],"character_count": 1057,"rank": 8},{"candidate_id": "cand_01","candidate_name": "Jason Miller","file_name": "candidate_10_jason_mechanical_eng.pdf","format": "PDF","composite_score": 1.66,"signal": "LOW MATCH","alignment_label": "Low Match","skill_match_percentage": 0.0,"tfidf_percentage": 4.14,"matched_skills": [],"missing_skills": ["Docker","FastAPI","Git","Kubernetes","Pandas","PostgreSQL","Python","SQL"],"all_detected_skills": ["CAD","MATLAB","Thermodynamics"],"soft_skills": ["Teamwork"],"top_shared_terms": ["engineer","engineering","using","experience","design"],"character_count": 816,"rank": 9},{"candidate_id": "cand_08","candidate_name": "Sarah Jenkins","file_name": "candidate_7_sarah_frontend_dev.docx","format": "DOCX","composite_score": 0.86,"signal": "LOW MATCH","alignment_label": "Low Match","skill_match_percentage": 0.0,"tfidf_percentage": 2.16,"matched_skills": [],"missing_skills": ["Docker","FastAPI","Git","Kubernetes","Pandas","PostgreSQL","Python","SQL"],"all_detected_skills": ["HTML/CSS","JavaScript","React","UI/UX"],"soft_skills": [],"top_shared_terms": ["design","high","experience","skills","technical skills"],"character_count": 735,"rank": 10}],"skills": {"required_skills": ["Docker","FastAPI","Git","Kubernetes","Pandas","PostgreSQL","Python","SQL"],"candidate_skill_frequencies": {"Docker": 5,"FastAPI": 3,"Git": 6,"Kubernetes": 2,"Pandas": 3,"PostgreSQL": 3,"Python": 6,"SQL": 7}},"eda_insights": {"total_raw_records": 10000,"experience_distribution": {"counts": {"0-2 Years": 4220,"3-5 Years": 4765,"6-10 Years": 899,"11-15 Years": 116,"16+ Years": 0},"percentages": {"0-2 Years": 42.2,"3-5 Years": 47.6,"6-10 Years": 9.0,"11-15 Years": 1.2,"16+ Years": 0.0},"median_years": 3.0,"mean_years": 3.1},"category_distribution": {"Technology": 2511,"Data & Analytics": 568,"Healthcare": 488,"Marketing & Sales": 463,"Engineering & Manufacturing": 435,"Creative & Design": 334,"Skilled Trades": 279,"Operations & Supply Chain": 266},"top_technical_skills": {"Communication": 2143,"Problem Solving": 2109,"Sql": 1162,"Leadership": 862,"Python": 731,"Javascript": 641,"Safety": 541,"Java": 513,"Research": 512,"Creativity": 505}},"configuration": {"weights": {"tfidf_weight": 0.4,"skill_weight": 0.6},"thresholds": {"shortlist_threshold": 70.0,"review_threshold": 50.0},"signals": {"shortlist": "SHORTLIST","review": "REVIEW","low_match": "LOW MATCH"}}};

  const DEFAULT_TAXONOMY = {
    technical_skills: [
      "Python", "SQL", "Docker", "FastAPI", "Pandas", "PostgreSQL",
      "Git", "Kubernetes", "NumPy", "C++", "C#", ".NET", "Node.js",
      "CI/CD", "Machine Learning", "Power BI", "Data Science", "AWS",
      "Flask", "Django", "MongoDB", "Redis", "Java", "JavaScript",
      "HTML/CSS", "React", "PyTorch", "TensorFlow", "Tableau",
      "Linux", "Excel", "MATLAB", "CAD", "Statistics",
      "Data Warehousing", "Thermodynamics", "UI/UX"
    ],
    soft_skills: [
      "Communication", "Leadership", "Teamwork", "Problem Solving",
      "Time Management", "Critical Thinking", "Adaptability"
    ]
  };

  // Sample Benchmark Texts for 1-Click Testing (Matches data/job_description.txt verbatim)
  const SAMPLE_BENCHMARK_JD = `Job Title: Senior Python & Data Engineer
Department: Data Platform Engineering
Location: Hybrid / Remote

About the Role:
We are seeking a seasoned Senior Python & Data Engineer to lead the design, implementation, and optimization of our high-scale data ingestion pipelines and microservice architectures. In this role, you will collaborate with cross-functional analytics teams to build fault-tolerant backend services, maintain relational data models, and deploy containerized services into production environments.

Key Responsibilities:
- Architect and maintain robust, high-throughput backend services and REST APIs using Python and FastAPI.
- Design, optimize, and maintain complex relational databases, analytical data warehouses, and schema migrations using SQL and PostgreSQL.
- Construct distributed data processing workflows and feature transformation pipelines leveraging Pandas.
- Package, containerize, and deploy scalable microservices using Docker and manage container orchestration with Kubernetes.
- Drive engineering excellence, code review practices, branch management, and automated release workflows using Git.
- Optimize database queries, indexing strategies, and pipeline execution latencies for large-scale datasets.

Required Technical Skills:
- Python
- SQL
- Docker
- FastAPI
- Pandas
- PostgreSQL
- Git
- Kubernetes

Qualifications:
- Bachelor's or Master's degree in Computer Science, Software Engineering, Data Engineering, or equivalent practical experience.
- Strong problem-solving mindset and disciplined software engineering practices.`;

  const SAMPLE_CANDIDATE_RESUME = `Alex Morgan
Senior Python Engineer & Data Platform Specialist
alex.morgan@example.com | github.com/alexmorgan-dev

Summary:
Results-driven Senior Software Engineer with over 6 years of expertise architecting high-throughput data processing pipelines, scalable microservices, and containerized backend architectures in production environments.

Core Technical Skills:
- Programming Languages: Python, SQL
- Frameworks & Libraries: FastAPI, Pandas, Redis
- Databases: PostgreSQL, MongoDB
- Containers & Orchestration: Docker, Kubernetes
- Version Control & DevOps: Git, CI/CD

Professional Experience:
Senior Backend Engineer — CloudData Solutions (2021 – Present)
- Architected and deployed 12+ low-latency microservices using Python and FastAPI, handling 15M daily requests.
- Optimized complex SQL queries and index strategies in PostgreSQL, decreasing average pipeline query latency by 42%.
- Containerized legacy services with Docker and orchestrated automated multi-cluster deployments on Kubernetes.
- Engineered automated ETL data pipelines utilizing Pandas for automated data cleaning, aggregation, and anomaly detection.
- Enforced automated branch protection, Git code review standards, and CI/CD test automation.

Data Platform Engineer — Apex Analytics (2018 – 2021)
- Designed resilient data ingestion workers using Python, PostgreSQL, and Redis caching.
- Maintained production Git repositories and automated Docker build pipelines.`;

  /* ── DOM References ───────────────────────────────────────── */
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  /* ── Bootstrap ────────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', init);

  async function init() {
    setupTabNavigation();
    setupAtsFormControls();

    // Fetch batch dashboard data and taxonomy concurrently
    try {
      const [dashResp, taxResp] = await Promise.allSettled([
        fetch('data/dashboard_data.json'),
        fetch('data/skills_taxonomy.json')
      ]);

      if (dashResp.status === 'fulfilled' && dashResp.value.ok) {
        DATA = await dashResp.value.json();
        candidates = DATA.candidates || [];
        renderDashboard();
      } else {
        console.info('[Dashboard] Live fetch failed (e.g. file:// protocol). Using embedded benchmark data.');
        DATA = DEFAULT_DASHBOARD_DATA;
        candidates = DATA.candidates || [];
        renderDashboard();
        showOfflineNotice();
      }

      if (taxResp.status === 'fulfilled' && taxResp.value.ok) {
        TAXONOMY = await taxResp.value.json();
      } else {
        console.info('[Live ATS] Using embedded fallback taxonomy.');
        TAXONOMY = DEFAULT_TAXONOMY;
      }
    } catch (err) {
      console.error('[Initialization Error]', err);
      TAXONOMY = DEFAULT_TAXONOMY;
    }
  }

  /* ═══════════════════════════════════════════════════════════
     TAB NAVIGATION SYSTEM
     ════════════════════════════════════════════════════════════ */
  function setupTabNavigation() {
    const btnDashboard = $('#tab-btn-dashboard');
    const btnAts = $('#tab-btn-ats');
    const panelDashboard = $('#tab-panel-dashboard');
    const panelAts = $('#tab-panel-ats');

    if (!btnDashboard || !btnAts) return;

    btnDashboard.addEventListener('click', () => {
      btnDashboard.classList.add('active');
      btnDashboard.setAttribute('aria-selected', 'true');
      btnAts.classList.remove('active');
      btnAts.setAttribute('aria-selected', 'false');

      panelDashboard.classList.add('active');
      panelAts.classList.remove('active');
    });

    btnAts.addEventListener('click', () => {
      btnAts.classList.add('active');
      btnAts.setAttribute('aria-selected', 'true');
      btnDashboard.classList.remove('active');
      btnDashboard.setAttribute('aria-selected', 'false');

      panelAts.classList.add('active');
      panelDashboard.classList.remove('active');
    });
  }

  /* ═══════════════════════════════════════════════════════════
     TAB 1: BATCH SCREENING DASHBOARD
     ════════════════════════════════════════════════════════════ */
  function renderDashboard() {
    renderHeader();
    renderKPIs();
    renderTable();
    renderCharts();
    bindDashboardEvents();
  }

  function showDashboardError(msg) {
    const main = $('#tab-panel-dashboard');
    if (main) {
      main.innerHTML = `
        <div style="text-align:center;padding:60px 20px;color:#dc2626;">
          <h2 style="margin-bottom:12px;">⚠️ Data Load Error</h2>
          <p style="color:#64748b;">${msg}</p>
          <p style="color:#94a3b8;font-size:0.82rem;margin-top:8px;">
            Ensure <code>data/dashboard_data.json</code> exists and the page is served via HTTP (not file://).
          </p>
        </div>`;
    }
  }

  function renderHeader() {
    const job = DATA.job || {};
    const meta = DATA.metadata || {};

    setText('#header-role-title', job.title ? `${job.title} — Requisition` : 'Recruiter Decision-Support System');
    setText('#header-department', job.department || 'Data Platform Engineering');
    setText('#header-pipeline-version', `v${meta.pipeline_version || '1.0.0'}`);

    if (meta.generated_at) {
      const d = new Date(meta.generated_at);
      setText('#header-timestamp', d.toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
      }));
    }
  }

  function renderKPIs() {
    const s = DATA.summary || {};
    setText('#kpi-total-value', s.total_candidates ?? '—');
    setText('#kpi-shortlist-value', s.shortlist_count ?? '—');
    setText('#kpi-review-value', s.review_count ?? '—');
    setText('#kpi-low-value', s.low_match_count ?? '—');
    setText('#kpi-avg-value', s.average_composite_score != null
      ? `${s.average_composite_score.toFixed(1)}%` : '—');
  }

  function renderTable() {
    const tbody = $('#leaderboard-body');
    if (!tbody) return;

    let rows = candidates.filter((c) => {
      if (activeFilter !== 'ALL' && c.signal !== activeFilter) return false;
      if (searchQuery && !c.candidate_name.toLowerCase().includes(searchQuery)) return false;
      return true;
    });

    rows.sort((a, b) => {
      let va = a[sortKey], vb = b[sortKey];
      if (typeof va === 'string') va = va.toLowerCase();
      if (typeof vb === 'string') vb = vb.toLowerCase();
      if (va < vb) return sortAsc ? -1 : 1;
      if (va > vb) return sortAsc ? 1 : -1;
      return 0;
    });

    if (rows.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" class="no-results">No candidates match your filters.</td></tr>`;
    } else {
      tbody.innerHTML = rows.map((c) => buildRow(c)).join('');
    }

    setText('#table-footer', `Showing ${rows.length} of ${candidates.length} candidates`);

    tbody.querySelectorAll('.btn-inspect').forEach((btn) => {
      btn.addEventListener('click', () => {
        const idx = parseInt(btn.dataset.index, 10);
        openDrawer(candidates[idx]);
      });
    });
  }

  function buildRow(c) {
    const idx = candidates.indexOf(c);
    const signalClass = getSignalClass(c.signal);
    const rankClass = c.rank === 1 ? 'rank-badge--top' : '';

    return `<tr>
      <td><span class="rank-badge ${rankClass}">${c.rank}</span></td>
      <td style="font-weight:600;color:#0f172a;">${esc(c.candidate_name)}</td>
      <td><span style="font-size:0.75rem;color:#64748b;">${esc(c.format)}</span></td>
      <td>
        <div class="table-score-cell">
          <div class="table-score-bar">
            <div class="table-score-bar-fill table-score-bar-fill--composite" style="width:${c.composite_score}%"></div>
          </div>
          <span class="table-score-text">${c.composite_score.toFixed(1)}%</span>
        </div>
      </td>
      <td>
        <div class="table-score-cell">
          <div class="table-score-bar">
            <div class="table-score-bar-fill table-score-bar-fill--skill" style="width:${c.skill_match_percentage}%"></div>
          </div>
          <span class="table-score-text">${c.skill_match_percentage.toFixed(1)}%</span>
        </div>
      </td>
      <td>
        <div class="table-score-cell">
          <div class="table-score-bar">
            <div class="table-score-bar-fill table-score-bar-fill--tfidf" style="width:${c.tfidf_percentage}%"></div>
          </div>
          <span class="table-score-text">${c.tfidf_percentage.toFixed(1)}%</span>
        </div>
      </td>
      <td><span class="signal-badge ${signalClass}">${esc(c.signal)}</span></td>
      <td><button class="btn-inspect" data-index="${idx}" aria-label="Inspect ${esc(c.candidate_name)}">Inspect</button></td>
    </tr>`;
  }

  function openDrawer(c) {
    if (!c) return;

    setText('#drawer-candidate-name', c.candidate_name);

    const signalEl = $('#drawer-signal');
    signalEl.textContent = c.alignment_label || c.signal;
    signalEl.className = `signal-badge ${getSignalClass(c.signal)}`;

    setBar('#drawer-tfidf-bar', c.tfidf_percentage);
    setText('#drawer-tfidf-value', `${c.tfidf_percentage.toFixed(1)}%`);
    setBar('#drawer-skill-bar', c.skill_match_percentage);
    setText('#drawer-skill-value', `${c.skill_match_percentage.toFixed(1)}%`);
    setText('#drawer-composite-value', `${c.composite_score.toFixed(1)}%`);

    const reqCount = DATA.job.required_skills_count || 8;
    setText('#drawer-matched-count', `(${c.matched_skills.length}/${reqCount})`);
    renderChips('#drawer-matched-skills', c.matched_skills, 'skill-chip--matched');
    renderChips('#drawer-missing-skills', c.missing_skills, 'skill-chip--missing');

    const softSection = $('#drawer-soft-section');
    if (c.soft_skills && c.soft_skills.length > 0) {
      softSection.style.display = '';
      renderChips('#drawer-soft-skills', c.soft_skills, 'skill-chip--soft');
    } else {
      softSection.style.display = 'none';
    }

    renderChips('#drawer-shared-terms', c.top_shared_terms || [], 'skill-chip--term');

    setText('#drawer-file-name', c.file_name || '—');
    setText('#drawer-format', c.format || '—');
    setText('#drawer-char-count', c.character_count != null
      ? c.character_count.toLocaleString() : '—');

    $('#drawer-backdrop').classList.add('active');
    const drawer = $('#candidate-drawer');
    drawer.classList.add('open');
    drawer.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';

    $('#drawer-close').focus();
  }

  function closeDrawer() {
    $('#drawer-backdrop').classList.remove('active');
    const drawer = $('#candidate-drawer');
    drawer.classList.remove('open');
    drawer.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  function renderChips(selector, items, chipClass) {
    const el = $(selector);
    if (!el) return;
    if (!items || items.length === 0) {
      el.innerHTML = '<span style="font-size:0.78rem;color:#94a3b8;">None</span>';
      return;
    }
    el.innerHTML = items.map((s) =>
      `<span class="skill-chip ${chipClass}">${esc(s)}</span>`
    ).join('');
  }

  /* ── Chart.js Visualizations ──────────────────────────────── */
  const chartInstances = {};

  function renderCharts() {
    renderSkillDistribution();
    renderScoreDistribution();
    renderExperienceDonut();
    renderCategoryBar();
  }

  function renderSkillDistribution() {
    const skills = DATA.skills || {};
    const freqs = skills.candidate_skill_frequencies || {};
    const labels = Object.keys(freqs);
    const values = Object.values(freqs);

    createChart('chart-skill-distribution', {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Candidates with Skill',
          data: values,
          backgroundColor: '#2563eb',
          borderColor: '#1d4ed8',
          borderWidth: 1,
          borderRadius: 4,
          maxBarThickness: 48
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => `${ctx.parsed.y} of ${candidates.length} candidates`
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: candidates.length,
            ticks: { stepSize: 1, font: { size: 11 } },
            grid: { color: '#f1f5f9' },
            title: { display: true, text: 'Candidates', font: { size: 11, weight: '600' }, color: '#64748b' }
          },
          x: {
            ticks: { font: { size: 11 } },
            grid: { display: false }
          }
        }
      }
    });
  }

  function renderScoreDistribution() {
    const sorted = [...candidates].sort((a, b) => b.composite_score - a.composite_score);
    const labels = sorted.map((c) => c.candidate_name.split(' ')[0]);
    const scores = sorted.map((c) => c.composite_score);
    const colors = sorted.map((c) => {
      if (c.signal === 'SHORTLIST') return '#059669';
      if (c.signal === 'REVIEW') return '#d97706';
      return '#94a3b8';
    });

    createChart('chart-score-distribution', {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Composite Score (%)',
          data: scores,
          backgroundColor: colors,
          borderColor: colors.map((c) => c),
          borderWidth: 1,
          borderRadius: 4,
          maxBarThickness: 48
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              title: (items) => {
                const idx = items[0].dataIndex;
                return sorted[idx].candidate_name;
              },
              label: (ctx) => `Score: ${ctx.parsed.y.toFixed(1)}%`,
              afterLabel: (ctx) => {
                const c = sorted[ctx.dataIndex];
                const matchLabel =
                  c.signal === 'SHORTLIST' ? 'High Match' :
                  c.signal === 'REVIEW'    ? 'Moderate Match' : 'Low Match';
                return `Match: ${matchLabel}`;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            ticks: { callback: (v) => v + '%', font: { size: 11 } },
            grid: { color: '#f1f5f9' },
            title: { display: true, text: 'Composite Score', font: { size: 11, weight: '600' }, color: '#64748b' }
          },
          x: {
            ticks: { font: { size: 11 } },
            grid: { display: false }
          }
        }
      }
    });
  }

  function renderExperienceDonut() {
    const eda = DATA.eda_insights || {};
    const exp = eda.experience_distribution || {};
    const counts = exp.counts || {};
    const labels = Object.keys(counts);
    const values = Object.values(counts);

    const palette = ['#bfdbfe', '#93c5fd', '#60a5fa', '#3b82f6', '#2563eb'];

    createChart('chart-experience', {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Records',
          data: values,
          backgroundColor: palette.slice(0, labels.length).reverse(),
          borderColor: palette.slice(0, labels.length).reverse().map((c) => c),
          borderWidth: 1,
          borderRadius: 4,
          maxBarThickness: 36
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const total = values.reduce((a, b) => a + b, 0);
                const pct = exp.percentages
                  ? (exp.percentages[ctx.label] || 0).toFixed(1)
                  : ((ctx.parsed.x / total) * 100).toFixed(1);
                return ` ${ctx.parsed.x.toLocaleString()} records (${pct}%)`;
              }
            }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: { font: { size: 11 } },
            grid: { color: '#f1f5f9' },
            title: { display: true, text: 'Number of Records', font: { size: 11, weight: '600' }, color: '#64748b' }
          },
          y: {
            ticks: { font: { size: 11 } },
            grid: { display: false }
          }
        }
      }
    });
  }


  function renderCategoryBar() {
    const eda = DATA.eda_insights || {};
    const cats = eda.category_distribution || {};
    const entries = Object.entries(cats).sort((a, b) => b[1] - a[1]);
    const labels = entries.map((e) => e[0]);
    const values = entries.map((e) => e[1]);

    const palette = [
      '#2563eb', '#7c3aed', '#059669', '#d97706',
      '#dc2626', '#db2777', '#0891b2', '#4f46e5'
    ];

    createChart('chart-category', {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Records',
          data: values,
          backgroundColor: palette.slice(0, labels.length),
          borderColor: palette.slice(0, labels.length),
          borderWidth: 1,
          borderRadius: 4,
          maxBarThickness: 28
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const total = (eda.total_raw_records || values.reduce((a, b) => a + b, 0));
                const pct = ((ctx.parsed.x / total) * 100).toFixed(1);
                return ` ${ctx.parsed.x.toLocaleString()} records (${pct}%)`;
              }
            }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: { font: { size: 11 } },
            grid: { color: '#f1f5f9' },
            title: { display: true, text: 'Number of Records', font: { size: 11, weight: '600' }, color: '#64748b' }
          },
          y: {
            ticks: { font: { size: 11 } },
            grid: { display: false }
          }
        }
      }
    });
  }

  function createChart(canvasId, config) {
    if (typeof Chart === 'undefined') {
      console.warn('[Dashboard] Chart.js is not loaded.');
      return;
    }
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    if (chartInstances[canvasId]) {
      chartInstances[canvasId].destroy();
    }
    try {
      chartInstances[canvasId] = new Chart(canvas.getContext('2d'), config);
    } catch (err) {
      console.warn('[Dashboard] Chart error for ' + canvasId + ':', err);
    }
  }

  function showOfflineNotice() {
    const overview = document.querySelector('#screening-overview .section-title-wrap');
    if (overview && !document.querySelector('#offline-notice')) {
      const notice = document.createElement('div');
      notice.id = 'offline-notice';
      notice.style.cssText = 'background:#eff6ff;border:1px solid #bfdbfe;border-radius:6px;padding:8px 14px;font-size:0.75rem;color:#1e40af;margin-top:8px;';
      notice.innerHTML = 'ℹ️ <strong>Offline Snapshot Active:</strong> Running from local snapshot data. To connect to live pipeline runs, serve via <code>python -m http.server 8080</code> in the <code>docs/</code> folder.';
      overview.appendChild(notice);
    }
  }

  function bindDashboardEvents() {
    const searchInput = $('#search-input');
    if (searchInput) {
      searchInput.addEventListener('input', () => {
        searchQuery = searchInput.value.trim().toLowerCase();
        renderTable();
      });
    }

    const filterSelect = $('#signal-filter');
    if (filterSelect) {
      filterSelect.addEventListener('change', () => {
        activeFilter = filterSelect.value;
        renderTable();
      });
    }

    $$('.leaderboard-table th.sortable').forEach((th) => {
      th.addEventListener('click', () => {
        const key = th.dataset.sort;
        if (sortKey === key) {
          sortAsc = !sortAsc;
        } else {
          sortKey = key;
          sortAsc = key === 'rank';
        }
        $$('.leaderboard-table th.sortable').forEach((h) => {
          h.classList.remove('sort-asc', 'sort-desc');
        });
        th.classList.add(sortAsc ? 'sort-asc' : 'sort-desc');
        renderTable();
      });
    });

    const closeBtn = $('#drawer-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', closeDrawer);
    }

    const backdrop = $('#drawer-backdrop');
    if (backdrop) {
      backdrop.addEventListener('click', closeDrawer);
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeDrawer();
    });
  }

  /* ═══════════════════════════════════════════════════════════
     TAB 2: LIVE ATS CHECKER ENGINE
     ════════════════════════════════════════════════════════════ */
  function setupAtsFormControls() {
    // Mode switcher (Upload vs Paste)
    const btnToggleUpload = $('#toggle-upload');
    const btnTogglePaste = $('#toggle-paste');
    const panelUpload = $('#panel-upload');
    const panelPaste = $('#panel-paste');

    if (btnToggleUpload && btnTogglePaste) {
      btnToggleUpload.addEventListener('click', () => {
        resumeInputMode = 'upload';
        btnToggleUpload.classList.add('active');
        btnToggleUpload.setAttribute('aria-selected', 'true');
        btnTogglePaste.classList.remove('active');
        btnTogglePaste.setAttribute('aria-selected', 'false');
        panelUpload.classList.add('active');
        panelPaste.classList.remove('active');
      });

      btnTogglePaste.addEventListener('click', () => {
        resumeInputMode = 'paste';
        btnTogglePaste.classList.add('active');
        btnTogglePaste.setAttribute('aria-selected', 'true');
        btnToggleUpload.classList.remove('active');
        btnToggleUpload.setAttribute('aria-selected', 'false');
        panelPaste.classList.add('active');
        panelUpload.classList.remove('active');
      });
    }

    // File input & Drag-and-Drop
    const fileInput = $('#ats-resume-file');
    const dropzone = $('#file-dropzone');
    const selectedFileDisplay = $('#selected-file-name');

    if (fileInput && dropzone) {
      fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
          selectedFile = e.target.files[0];
          selectedFileDisplay.textContent = `Selected: ${selectedFile.name} (${(selectedFile.size / 1024).toFixed(1)} KB)`;
          clearAtsError();
        }
      });

      ['dragenter', 'dragover'].forEach((eventName) => {
        dropzone.addEventListener(eventName, (e) => {
          e.preventDefault();
          e.stopPropagation();
          dropzone.classList.add('dragover');
        });
      });

      ['dragleave', 'drop'].forEach((eventName) => {
        dropzone.addEventListener(eventName, (e) => {
          e.preventDefault();
          e.stopPropagation();
          dropzone.classList.remove('dragover');
        });
      });

      dropzone.addEventListener('drop', (e) => {
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
          selectedFile = e.dataTransfer.files[0];
          fileInput.files = e.dataTransfer.files;
          selectedFileDisplay.textContent = `Selected: ${selectedFile.name} (${(selectedFile.size / 1024).toFixed(1)} KB)`;
          clearAtsError();
        }
      });
    }

    // Clear validation styling when user edits fields
    ['#ats-company', '#ats-role', '#ats-jd', '#ats-resume-text'].forEach((sel) => {
      const el = $(sel);
      if (el) {
        el.addEventListener('input', () => {
          el.classList.remove('form-input--error', 'form-textarea--error');
          const box = $('#ats-error-box');
          if (box) box.style.display = 'none';
        });
      }
    });

    // One-Click Sample Loaders
    const btnSampleJd = $('#ats-load-sample-jd');
    if (btnSampleJd) {
      btnSampleJd.addEventListener('click', () => {
        $('#ats-company').value = 'Apex Data Infrastructure';
        $('#ats-role').value = 'Senior Python & Data Engineer';
        $('#ats-jd').value = SAMPLE_BENCHMARK_JD;
        clearAtsError();
      });
    }

    const btnSampleResume = $('#ats-load-sample-resume');
    if (btnSampleResume) {
      btnSampleResume.addEventListener('click', () => {
        $('#ats-resume-text').value = SAMPLE_CANDIDATE_RESUME;
        clearAtsError();
      });
    }

    // Primary CTA: Analyze Resume
    const btnAnalyze = $('#ats-analyze-btn');
    if (btnAnalyze) {
      btnAnalyze.addEventListener('click', handleLiveAtsAnalysis);
    }

    // Reset Form Button
    const btnReset = $('#ats-reset-btn');
    if (btnReset) {
      btnReset.addEventListener('click', resetAtsForm);
    }
  }

  /* ── Extraction Helpers ───────────────────────────────────── */
  async function extractTextFromFile(file) {
    if (!file) throw new Error('No file provided.');

    const name = file.name.toLowerCase();

    // Plain text
    if (name.endsWith('.txt')) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = () => reject(new Error('Failed to read TXT file.'));
        reader.readAsText(file);
      });
    }

    // PDF via PDF.js
    if (name.endsWith('.pdf')) {
      if (typeof window.pdfjsLib === 'undefined') {
        throw new Error('PDF parsing library (PDF.js) is not loaded. Please paste resume text instead.');
      }
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await window.pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      let fullText = '';
      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const textContent = await page.getTextContent();
        const pageText = textContent.items.map((item) => item.str).join(' ');
        fullText += pageText + ' ';
      }
      return fullText.trim();
    }

    // DOCX via Mammoth.js
    if (name.endsWith('.docx')) {
      if (typeof window.mammoth === 'undefined') {
        throw new Error('DOCX parsing library (Mammoth.js) is not loaded. Please paste resume text instead.');
      }
      const arrayBuffer = await file.arrayBuffer();
      const result = await window.mammoth.extractRawText({ arrayBuffer });
      return result.value.trim();
    }

    throw new Error(`Unsupported file extension for "${file.name}". Please provide .pdf, .docx, or .txt.`);
  }

  /* ── Text Normalization Port (matches src/cleaner.py) ──────── */
  const PROTECTED_TOKENS = [
    { pattern: /\bc\+\+/gi, mask: '__token_cpp__' },
    { pattern: /\bc\#/gi, mask: '__token_csharp__' },
    { pattern: /(?<!\w)\.net\b/gi, mask: '__token_dotnet__' },
    { pattern: /\bnode\.js\b/gi, mask: '__token_nodejs__' },
    { pattern: /\bci\/cd\b/gi, mask: '__token_cicd__' }
  ];

  const UNMASK_MAP = {
    '__token_cpp__': 'c++',
    '__token_csharp__': 'c#',
    '__token_dotnet__': '.net',
    '__token_nodejs__': 'node.js',
    '__token_cicd__': 'ci/cd'
  };

  function cleanText(rawText) {
    if (!rawText || typeof rawText !== 'string') return '';

    // 1. Remove URLs
    let text = rawText.replace(/https?:\/\/\S+|www\.\S+/gi, ' ');

    // 2. Remove email addresses
    text = text.replace(/[\w\.-]+@[\w\.-]+\.\w+/gi, ' ');

    // 3. Mask protected tokens
    PROTECTED_TOKENS.forEach(({ pattern, mask }) => {
      text = text.replace(pattern, mask);
    });

    // 4. Lowercase
    text = text.toLowerCase();

    // 5. Strip non-alphanumeric punctuation (keep letters, digits, spaces, and underscores for masks)
    text = text.replace(/[^\w\s]/g, ' ');

    // 6. Unmask protected tokens
    Object.entries(UNMASK_MAP).forEach(([mask, original]) => {
      text = text.replaceAll(mask, original);
    });

    // 7. Collapse whitespace and trim
    return text.replace(/\s+/g, ' ').trim();
  }

  /* ── Skills Extraction Port (matches src/skill_extractor.py) ── */
  function buildSkillPattern(skill) {
    const sk = skill.toLowerCase().trim();
    if (sk === 'c++') {
      return /(?<![\w\+])c\+\+(?![\w\+])/i;
    } else if (sk === 'c#') {
      return /(?<![\w\#])c\#(?![\w\#])/i;
    } else if (sk === '.net') {
      return /(?<![\w\.])\.net(?![\w\.])/i;
    } else if (sk === 'ci/cd') {
      return /\bci\/cd\b/i;
    } else if (sk === 'node.js') {
      return /\bnode\.js\b/i;
    } else if (sk.includes(' ') || sk.includes('/') || sk.includes('-')) {
      const parts = sk.split(/[\s\/\-]+/).filter(Boolean).map(escapeRegex);
      return new RegExp('\\b' + parts.join('[\\s\\/\\-]+') + '\\b', 'i');
    } else {
      return new RegExp('\\b' + escapeRegex(sk) + '\\b', 'i');
    }
  }

  function extractSkillsFromText(text) {
    const tax = TAXONOMY || DEFAULT_TAXONOMY;
    const foundTech = new Set();
    const foundSoft = new Set();

    (tax.technical_skills || []).forEach((skill) => {
      const pat = buildSkillPattern(skill);
      if (pat.test(text)) {
        foundTech.add(skill);
      }
    });

    (tax.soft_skills || []).forEach((skill) => {
      const pat = buildSkillPattern(skill);
      if (pat.test(text)) {
        foundSoft.add(skill);
      }
    });

    return {
      technical_skills: Array.from(foundTech).sort(),
      soft_skills: Array.from(foundSoft).sort()
    };
  }

  /* ── TF-IDF Relevance Port (matches specifications) ───────── */
  const STOP_WORDS = new Set([
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any',
    'are', 'aren', 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below',
    'between', 'both', 'but', 'by', 'can', 'could', 'did', 'do', 'does', 'doing', 'down',
    'during', 'each', 'few', 'for', 'from', 'further', 'had', 'has', 'have', 'having',
    'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if',
    'in', 'into', 'is', 'isn', 'it', 'its', 'itself', 'just', 'll', 'm', 'me', 'might',
    'more', 'most', 'my', 'myself', 'no', 'nor', 'not', 'now', 'o', 'of', 'off', 'on',
    'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 're',
    's', 'same', 'she', 'should', 'so', 'some', 'such', 't', 'than', 'that', 'the',
    'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'this',
    'those', 'through', 'to', 'too', 'under', 'until', 'up', 've', 'very', 'was', 'we',
    'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will',
    'with', 'won', 'would', 'y', 'you', 'your', 'yours', 'yourself', 'yourselves'
  ]);

  function tokenizeNgrams(text) {
    // Token pattern capturing alphanumeric tokens and programming symbols
    const matches = text.match(/\b\w[\w.+/#-]*\b/g) || [];
    const tokens = [];

    matches.forEach((t) => {
      const cleanT = t.toLowerCase();
      if (cleanT.length > 1 && !STOP_WORDS.has(cleanT)) {
        tokens.push(cleanT);
      } else if (cleanT === 'c') {
        tokens.push(cleanT);
      }
    });

    // Unigrams + Bigrams
    const ngrams = [...tokens];
    for (let i = 0; i < tokens.length - 1; i++) {
      ngrams.push(`${tokens[i]} ${tokens[i + 1]}`);
    }

    return ngrams;
  }

  function computeTfidfSimilarity(cleanedJd, cleanedResume) {
    if (!cleanedJd.trim() || !cleanedResume.trim()) {
      return { tfidf_percentage: 0.0, top_shared_terms: [] };
    }

    const jdTokens = tokenizeNgrams(cleanedJd);
    const resTokens = tokenizeNgrams(cleanedResume);

    if (jdTokens.length === 0 || resTokens.length === 0) {
      return { tfidf_percentage: 0.0, top_shared_terms: [] };
    }

    // Build raw term frequencies
    const tfJd = {};
    const tfRes = {};

    jdTokens.forEach((t) => { tfJd[t] = (tfJd[t] || 0) + 1; });
    resTokens.forEach((t) => { tfRes[t] = (tfRes[t] || 0) + 1; });

    // Joint vocabulary
    const vocab = new Set([...Object.keys(tfJd), ...Object.keys(tfRes)]);
    const N = 2; // Total documents in joint space: JD and Resume

    // Compute TF-IDF weights: sublinear TF (1 + ln(tf)) and smooth IDF (ln(N/df) + 1)
    const vecJd = {};
    const vecRes = {};
    let normJd = 0;
    let normRes = 0;

    vocab.forEach((term) => {
      const inJd = Boolean(tfJd[term]);
      const inRes = Boolean(tfRes[term]);
      const df = (inJd ? 1 : 0) + (inRes ? 1 : 0);
      const idf = Math.log(N / df) + 1.0;

      const subTfJd = inJd ? (1.0 + Math.log(tfJd[term])) : 0;
      const wJd = subTfJd * idf;
      vecJd[term] = wJd;
      normJd += wJd * wJd;

      const subTfRes = inRes ? (1.0 + Math.log(tfRes[term])) : 0;
      const wRes = subTfRes * idf;
      vecRes[term] = wRes;
      normRes += wRes * wRes;
    });

    normJd = Math.sqrt(normJd);
    normRes = Math.sqrt(normRes);

    if (normJd === 0 || normRes === 0) {
      return { tfidf_percentage: 0.0, top_shared_terms: [] };
    }

    // L2 normalized cosine similarity + shared term decomposition
    let dotProduct = 0;
    const sharedTerms = [];

    vocab.forEach((term) => {
      const normalizedJd = vecJd[term] / normJd;
      const normalizedRes = vecRes[term] / normRes;
      const product = normalizedJd * normalizedRes;

      if (product > 0) {
        dotProduct += product;
        sharedTerms.push({ term, score: product });
      }
    });

    // Bound similarity in [0.0, 1.0] and convert to percentage
    const boundedSim = Math.max(0.0, Math.min(1.0, dotProduct));
    const tfidfPercentage = Math.round(boundedSim * 10000) / 100; // 2 decimals

    // Top 5 shared contributors
    sharedTerms.sort((a, b) => b.score - a.score);
    const topShared = sharedTerms.slice(0, 5).map((item) => item.term);

    return {
      tfidf_percentage: tfidfPercentage,
      top_shared_terms: topShared
    };
  }

  /* ── Master Live ATS Analysis Handler ─────────────────────── */
  async function handleLiveAtsAnalysis() {
    clearAtsError();

    // Hide previous results immediately so invalid inputs never show a misleading score
    const prevResults = $('#ats-results');
    if (prevResults) prevResults.style.display = 'none';

    const company = ($('#ats-company').value || '').trim();
    const role = ($('#ats-role').value || '').trim();
    const jdText = ($('#ats-jd').value || '').trim();

    // 1. Validate Requisition Metadata
    if (!company) {
      const el = $('#ats-company');
      showAtsError('Please specify the Company Name (used for screening context).', el);
      el.focus();
      return;
    }

    if (!role) {
      const el = $('#ats-role');
      showAtsError('Please specify the Job Role (used for screening context).', el);
      el.focus();
      return;
    }

    // 2. Validate Job Description
    if (!jdText || jdText.length < 30) {
      const el = $('#ats-jd');
      showAtsError('Job Description is too short or empty. Please provide a complete JD (minimum 30 characters).', el);
      el.focus();
      return;
    }

    // 3. Extract & Validate Candidate Resume
    let rawResumeText = '';
    let resumeSourceLabel = '';

    const btnAnalyze = $('#ats-analyze-btn');
    const origBtnHtml = btnAnalyze.innerHTML;
    btnAnalyze.disabled = true;
    btnAnalyze.innerHTML = '<span class="btn-cta-icon">⏳</span> EXTRACTING &amp; ANALYZING…';

    try {
      if (resumeInputMode === 'upload') {
        if (!selectedFile) {
          showAtsError('Please select a resume file (.pdf, .docx, .txt) or switch to Paste Text mode.', $('#file-dropzone'));
          btnAnalyze.disabled = false;
          btnAnalyze.innerHTML = origBtnHtml;
          return;
        }

        if (selectedFile.size === 0) {
          showAtsError(`The selected file "${selectedFile.name}" is empty (0 bytes).`, $('#file-dropzone'));
          btnAnalyze.disabled = false;
          btnAnalyze.innerHTML = origBtnHtml;
          return;
        }

        resumeSourceLabel = selectedFile.name;
        rawResumeText = await extractTextFromFile(selectedFile);
      } else {
        rawResumeText = ($('#ats-resume-text').value || '').trim();
        resumeSourceLabel = 'Pasted Resume Text';
      }

      if (!rawResumeText || rawResumeText.length < 30) {
        const errTarget = resumeInputMode === 'upload' ? $('#file-dropzone') : $('#ats-resume-text');
        showAtsError('Candidate resume content is too short or could not be extracted (minimum 30 characters required).', errTarget);
        btnAnalyze.disabled = false;
        btnAnalyze.innerHTML = origBtnHtml;
        return;
      }

      // 4. Client-side NLP Pipeline Execution
      const cleanedJd = cleanText(jdText);
      const cleanedResume = cleanText(rawResumeText);

      // Skills Extraction
      const jdSkills = extractSkillsFromText(cleanedJd);
      const resumeSkills = extractSkillsFromText(cleanedResume);

      const reqTechSkills = jdSkills.technical_skills;
      const candTechSkills = new Set(resumeSkills.technical_skills);

      if (reqTechSkills.length === 0) {
        showAtsError('No technical skills from the taxonomy were detected in the Job Description. Please ensure the JD specifies required technical competencies (e.g., Python, SQL, Docker, etc.).');
        btnAnalyze.disabled = false;
        btnAnalyze.innerHTML = origBtnHtml;
        return;
      }

      const matchedSkills = reqTechSkills.filter((s) => candTechSkills.has(s));
      const missingSkills = reqTechSkills.filter((s) => !candTechSkills.has(s));

      const skillMatchRatio = matchedSkills.length / reqTechSkills.length;
      const skillMatchPercentage = Math.round(skillMatchRatio * 10000) / 100;

      // TF-IDF Textual Relevance
      const { tfidf_percentage, top_shared_terms } = computeTfidfSimilarity(cleanedJd, cleanedResume);

      // 5. Composite Scoring (40% TF-IDF + 60% Skill Match)
      // Company and Role are NOT included in the numerical formula!
      const compositeScore = Math.round(((0.40 * tfidf_percentage) + (0.60 * skillMatchPercentage)) * 100) / 100;

      // 6. Screening Signal Assignment
      let signal = 'LOW MATCH';
      let alignmentLabel = 'Low Match';
      let signalPillClass = 'hero-signal-pill--low';

      if (compositeScore >= 70.0) {
        signal = 'SHORTLIST';
        alignmentLabel = 'High Match';
        signalPillClass = 'hero-signal-pill--shortlist';
      } else if (compositeScore >= 50.0) {
        signal = 'REVIEW';
        alignmentLabel = 'Moderate Match';
        signalPillClass = 'hero-signal-pill--review';
      }

      // 7. Render Results
      renderLiveAtsResults({
        company,
        role,
        sourceLabel: resumeSourceLabel,
        compositeScore,
        signal,
        alignmentLabel,
        signalPillClass,
        skillMatchPercentage,
        tfidf_percentage,
        matchedSkills,
        missingSkills,
        softSkills: resumeSkills.soft_skills,
        top_shared_terms,
        reqTechSkillsCount: reqTechSkills.length
      });

    } catch (err) {
      console.error('[Live ATS Error]', err);
      const errTarget = resumeInputMode === 'upload' ? $('#file-dropzone') : $('#ats-resume-text');
      showAtsError(`Analysis Error: ${err.message || 'Failed to process candidate resume.'}`, errTarget);
    } finally {
      btnAnalyze.disabled = false;
      btnAnalyze.innerHTML = origBtnHtml;
    }
  }

  function renderLiveAtsResults(res) {
    // Context ribbon
    setText('#res-company', res.company);
    setText('#res-role', res.role);
    setText('#res-source', res.sourceLabel);

    // Hero score
    const scoreEl = $('#res-composite-score');
    scoreEl.textContent = `${res.compositeScore.toFixed(1)}%`;
    scoreEl.style.color = res.signal === 'SHORTLIST' ? 'var(--signal-shortlist)' :
                          res.signal === 'REVIEW'    ? 'var(--signal-review)' : 'var(--slate-500)';
    const pill = $('#res-signal-pill');
    pill.textContent = res.alignmentLabel;
    pill.className = `hero-signal-pill ${res.signalPillClass}`;
    setText('#res-signal-desc', `Signal: ${res.signal}`);

    // Set hero card accent border color
    const heroCard = document.querySelector('.ats-score-hero-card');
    if (heroCard) {
      const accentColor = res.signal === 'SHORTLIST' ? 'var(--signal-shortlist)' :
                          res.signal === 'REVIEW'    ? 'var(--signal-review)' : 'var(--slate-400)';
      heroCard.style.setProperty('--hero-accent', accentColor);
    }

    // Metric bars
    setBar('#res-skill-bar', res.skillMatchPercentage);
    setText('#res-skill-val', `${res.skillMatchPercentage.toFixed(1)}%`);
    setBar('#res-tfidf-bar', res.tfidf_percentage);
    setText('#res-tfidf-val', `${res.tfidf_percentage.toFixed(1)}%`);

    // Formula breakdown text
    setText(
      '#res-formula-tag',
      `Score = (0.40 × ${res.tfidf_percentage.toFixed(1)}%) + (0.60 × ${res.skillMatchPercentage.toFixed(1)}%) = ${res.compositeScore.toFixed(1)}%`
    );

    // Skills breakdown
    setText('#res-matched-count', `${res.matchedSkills.length}/${res.reqTechSkillsCount}`);
    renderChips('#res-matched-skills', res.matchedSkills, 'skill-chip--matched');

    setText('#res-missing-count', `${res.missingSkills.length}`);
    renderChips('#res-missing-skills', res.missingSkills, 'skill-chip--missing');

    renderChips('#res-soft-skills', res.softSkills, 'skill-chip--soft');
    renderChips('#res-shared-terms', res.top_shared_terms, 'skill-chip--term');

    // Unhide results container and smooth-scroll
    const resultsContainer = $('#ats-results');
    resultsContainer.style.display = 'flex';
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function showAtsError(msg, fieldEl) {
    const box = $('#ats-error-box');
    const msgEl = $('#ats-error-msg');
    if (box && msgEl) {
      msgEl.textContent = msg;
      box.style.display = 'flex';
      box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    // Apply field-level error styling
    if (fieldEl) {
      const cls = fieldEl.tagName === 'TEXTAREA' ? 'form-textarea--error' : 'form-input--error';
      fieldEl.classList.add(cls);
    }
  }

  function clearAtsError() {
    const box = $('#ats-error-box');
    if (box) box.style.display = 'none';
    // Clear all field-level error highlights
    $$('.form-input--error').forEach((el) => el.classList.remove('form-input--error'));
    $$('.form-textarea--error').forEach((el) => el.classList.remove('form-textarea--error'));
  }

  function resetAtsForm() {
    clearAtsError();
    $('#ats-company').value = '';
    $('#ats-role').value = '';
    $('#ats-jd').value = '';
    $('#ats-resume-text').value = '';
    const fileInput = $('#ats-resume-file');
    if (fileInput) fileInput.value = '';
    const fileLabel = $('#selected-file-name');
    if (fileLabel) fileLabel.textContent = '';
    selectedFile = null;
    // Hide results and reset hero card values to neutral state
    const results = $('#ats-results');
    if (results) results.style.display = 'none';
    const scoreEl = $('#res-composite-score');
    if (scoreEl) {
      scoreEl.textContent = '0.0%';
      scoreEl.style.color = '';
    }
    const pill = $('#res-signal-pill');
    if (pill) {
      pill.textContent = '—';
      pill.className = 'hero-signal-pill';
    }
    setText('#res-signal-desc', '—');
    const heroCard = document.querySelector('.ats-score-hero-card');
    if (heroCard) {
      heroCard.style.removeProperty('--hero-accent');
    }
  }

  /* ── General Utilities ────────────────────────────────────── */
  function setText(sel, text) {
    const el = $(sel);
    if (el) el.textContent = text;
  }

  function setBar(sel, pct) {
    const el = $(sel);
    if (el) el.style.width = `${Math.min(100, Math.max(0, pct))}%`;
  }

  function getSignalClass(signal) {
    switch (signal) {
      case 'SHORTLIST': return 'signal-badge--shortlist';
      case 'REVIEW':    return 'signal-badge--review';
      case 'LOW MATCH': return 'signal-badge--low';
      default:          return '';
    }
  }

  function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function esc(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

})();
