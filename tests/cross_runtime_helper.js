/**
 * Cross-runtime verification helper.
 * Reads JSON payload from stdin to avoid Windows CLI quote escaping.
 * Executes JavaScript NLP and scoring engine from docs/app.js under Node.js
 * to verify parity with Python calculations.
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const rootDir = path.resolve(__dirname, '..');
const appCode = fs.readFileSync(path.join(rootDir, 'docs', 'app.js'), 'utf8');
const taxonomy = JSON.parse(fs.readFileSync(path.join(rootDir, 'docs', 'data', 'skills_taxonomy.json'), 'utf8'));

// Extract escapeRegex and NLP functions directly from app.js source
const sandbox = {
  window: {},
  document: {
    querySelectorAll: () => [],
    querySelector: () => null,
    getElementById: () => null
  },
  console: console,
  TAXONOMY: taxonomy
};

vm.createContext(sandbox);

// Execute from PROTECTED_TOKENS through the end of the IIFE
const startTokens = appCode.indexOf('const PROTECTED_TOKENS =');
const endTokens = appCode.lastIndexOf('})();');
const codeToRun = appCode.substring(startTokens, endTokens);
vm.runInContext(codeToRun, sandbox);

// Read entire payload from stdin (fd 0)
const inputData = fs.readFileSync(0, 'utf8');
if (!inputData.trim()) {
  process.exit(0);
}

const payload = JSON.parse(inputData);
const mode = payload.mode;

if (mode === 'extract_skills') {
  const outputs = payload.inputs.map(text => {
    const cleaned = sandbox.cleanText(text);
    return sandbox.extractSkillsFromText(cleaned);
  });
  process.stdout.write(JSON.stringify(outputs));
} else if (mode === 'score_candidates') {
  const jdRaw = payload.jd;
  const resumes = payload.resumes;

  const cleanedJd = sandbox.cleanText(jdRaw);
  const jdSkills = sandbox.extractSkillsFromText(cleanedJd).technical_skills;

  const results = resumes.map(resText => {
    const cleanedRes = sandbox.cleanText(resText);
    const candSkills = new Set(sandbox.extractSkillsFromText(cleanedRes).technical_skills);
    const matched = jdSkills.filter(s => candSkills.has(s));
    const skillPct = jdSkills.length > 0 ? (matched.length / jdSkills.length) * 100 : 0.0;
    const tfidfPct = sandbox.computeTfidfSimilarity(cleanedJd, cleanedRes).tfidf_percentage;
    const composite = Math.round(((0.40 * tfidfPct) + (0.60 * skillPct)) * 100) / 100;
    const signal = composite >= 70 ? 'SHORTLIST' : (composite >= 50 ? 'REVIEW' : 'LOW MATCH');
    const label = composite >= 70 ? 'High Match' : (composite >= 50 ? 'Moderate Match' : 'Low Match');

    return {
      matched_skills: matched,
      matched_count: matched.length,
      total_jd_skills: jdSkills.length,
      skill_match_percentage: skillPct,
      tfidf_percentage: tfidfPct,
      composite_score: composite,
      signal: signal,
      alignment_label: label
    };
  });

  process.stdout.write(JSON.stringify(results));
}
