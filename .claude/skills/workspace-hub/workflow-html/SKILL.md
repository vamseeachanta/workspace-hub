---
name: workflow-html
description: >
  Canonical HTML template system for all WRK review artifacts. Defines the warm-parchment
  design system, complete section catalog, interactivity layer, and rendering rules so every
  draft-plan, final-plan, implementation-review, and close-review HTML looks and behaves
  identically regardless of which agent or session generated it.
version: 1.2.0
updated: 2026-03-05
category: workspace-hub
type: skill
trigger: manual
auto_execute: false
capabilities:
  - html_template_system
  - wrk_review_rendering
  - section_catalog
  - design_system
related_skills:
  - workspace-hub/workflow-gatepass
  - workspace-hub/work-queue-workflow
  - workspace-hub/wrk-lifecycle-testpack
  - coordination/workspace/work-queue
tools: [Read, Write, Bash]
see_also:
  - .claude/work-queue/assets/WRK-624/workflow-governance-review.html
  - scripts/work-queue/generate-html-review.py
---

# Workflow HTML Skill

> Canonical HTML template and design system for all WRK review artifacts.
> **Mandatory** at stages 5 (plan draft), 7 (plan final), 11 (artifact gen), 17 (close review), 19 (close).

---

## 1. Design System

All WRK HTML artifacts share one design system. Never deviate; never mix styles.

### 1.1 CSS Custom Properties

```css
:root {
  --bg:       #f3efe6;   /* warm parchment page background */
  --panel:    #fffdf8;   /* card / panel fill */
  --ink:      #172126;   /* primary text */
  --muted:    #55636b;   /* secondary text, table cells */
  --accent:   #0f766e;   /* teal — links, eyebrow, exec-summary border */
  --accent-2: #8a5a2b;   /* amber — h2 headings */
  --line:     #d9d0c0;   /* borders, table rules */
  --shadow:   0 16px 40px rgba(20, 33, 38, 0.08);
  /* status badge colors */
  --good:     #166534;   /* PASS / done */
  --warn:     #b45309;   /* WARN / in-progress */
  --bad:      #b91c1c;   /* FAIL / blocked */
}
```

### 1.2 Typography

```css
body {
  font-family: Georgia, "Times New Roman", serif;
  background: radial-gradient(circle at top, #fffaf0 0, var(--bg) 48%, #ebe5d7 100%);
  color: var(--ink);
  line-height: 1.5;
  margin: 0;
}
code {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  background: rgba(27,31,35,0.05);
  padding: 0.2em 0.4em;
  border-radius: 3px;
}
```

### 1.3 Layout Primitives

```css
/* Hero header */
.hero          { padding: 48px 24px 28px; border-bottom: 1px solid rgba(23,33,38,0.08);
                 background: linear-gradient(135deg,rgba(15,118,110,0.08),rgba(138,90,43,0.10)); }
.hero-inner,
.content       { max-width: 1180px; margin: 0 auto; }

/* Eyebrow (WRK-ID + artifact type above H1) */
.eyebrow       { text-transform: uppercase; letter-spacing: 0.12em; font-size: 0.72rem;
                 color: var(--accent); font-weight: 700; }

/* H1 */
h1             { margin: 10px 0 12px; font-size: clamp(2rem,4vw,3.8rem);
                 line-height: 0.95; }

/* Lede (subtitle below H1) */
.lede          { max-width: 78ch; color: var(--muted); font-size: 1.05rem; }

/* Content wrapper */
.content       { padding: 28px 24px 56px; }

/* Card — main container for each major section */
.card          { background: var(--panel); padding: 26px; border-radius: 18px;
                 box-shadow: var(--shadow); border: 1px solid var(--line);
                 margin-bottom: 20px; }

/* Section headings inside cards */
h2             { border-bottom: 1px solid var(--line); padding-bottom: 0.3em;
                 margin-top: 24px; color: var(--accent-2); letter-spacing: 0.02em; }
h3             { color: var(--ink); margin-top: 18px; }

/* Exec-summary callout */
.exec-summary  { background: linear-gradient(180deg,#fff,#fcf8ef);
                 border-left: 6px solid var(--accent); padding: 20px;
                 margin-bottom: 30px; border-radius: 10px; }
.exec-summary h2 { margin-top: 0; border: none; color: var(--accent); }

/* Artifact / asset link box */
.artifact-box  { background: #fff; padding: 16px; border-radius: 10px;
                 border: 1px solid var(--line); }

/* Tables */
table          { border-collapse: collapse; width: 100%; margin: 16px 0; font-size: 0.95rem; }
th, td         { border-top: 1px solid var(--line); padding: 10px 8px;
                 text-align: left; vertical-align: top; }
th             { font-weight: 700; text-transform: uppercase;
                 letter-spacing: 0.06em; font-size: 0.86rem; color: var(--ink); }

/* Muted text inside cards */
.card p, .card li, .card td, .card th { color: var(--muted); }
.card strong, .card code              { color: var(--ink); }

/* Two-column responsive split */
.split         { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }
@media (max-width: 900px) { .split { grid-template-columns: 1fr; } }

/* Collapsible h2 — collapsed state */
h2[data-collapsed="true"]  { margin-bottom: 4px; }

/* Print */
@media print {
  body  { background: #fff; }
  .card { box-shadow: none; border: 1px solid #ccc; }
  tr, td, th { page-break-inside: avoid; }
}
```

### 1.4 Metadata Pills Grid

```css
.meta          { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px,1fr));
                 gap: 10px; margin: 14px 0 20px; }
.pill          { background: var(--panel); border: 1px solid var(--line);
                 border-radius: 10px; padding: 10px 14px; font-size: 0.9rem; }
.pill strong   { display: block; font-size: 0.72rem; text-transform: uppercase;
                 letter-spacing: 0.08em; color: var(--accent-2); margin-bottom: 2px; }
```

### 1.5 Status Badges

```css
.badge         { display: inline-block; padding: 2px 8px; border-radius: 999px;
                 font-size: 0.78rem; font-weight: 700; text-transform: uppercase;
                 letter-spacing: 0.06em; }
.badge-pass    { background: #dcfce7; color: var(--good); }
.badge-warn    { background: #fef3c7; color: var(--warn); }
.badge-fail    { background: #fee2e2; color: var(--bad); }
.badge-info    { background: #dbeafe; color: #1d4ed8; }
```

---

## 2. Interactivity Layer

Every artifact must include this JavaScript block before `</body>` to make the page free-flowing:

```html
<script>
/* ── Smooth scroll for TOC anchors ── */
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) { e.preventDefault(); target.scrollIntoView({behavior:'smooth',block:'start'}); }
  });
});

/* ── Collapsible cards (click h2 to toggle; shows summary when collapsed) ── */
document.querySelectorAll('.card h2').forEach(h2 => {
  h2.style.cursor = 'pointer';
  h2.title = 'Click to collapse/expand';

  /* Build a summary preview to show while collapsed */
  function buildSummary(siblings) {
    const badges = [];
    siblings.forEach(s => s.querySelectorAll('.badge').forEach(b => badges.push(b.outerHTML)));
    const badgeHtml = badges.slice(0, 4).join(' ');

    /* Try first meaningful text: list item count or first <p> snippet */
    let text = '';
    for (const s of siblings) {
      if (s.tagName === 'UL' || s.tagName === 'OL') {
        const n = s.querySelectorAll('li').length;
        text = n + ' item' + (n !== 1 ? 's' : '');
        break;
      }
      if (s.tagName === 'TABLE') {
        const n = s.querySelectorAll('tbody tr').length;
        text = n + ' row' + (n !== 1 ? 's' : '');
        break;
      }
      if (s.tagName === 'P' && s.textContent.trim()) {
        text = s.textContent.trim().slice(0, 80) + (s.textContent.length > 80 ? '…' : '');
        break;
      }
    }
    const parts = [badgeHtml, text].filter(Boolean).join(' &nbsp;·&nbsp; ');
    return parts || '&nbsp;';
  }

  const siblings = [];
  let el = h2.nextElementSibling;
  while (el) { siblings.push(el); el = el.nextElementSibling; }

  /* Summary chip — hidden while expanded */
  const chip = document.createElement('span');
  chip.style.cssText =
    'display:none;margin-left:12px;font-size:0.8rem;font-weight:400;' +
    'color:#55636b;vertical-align:middle;pointer-events:none;';
  chip.innerHTML = buildSummary(siblings);
  h2.appendChild(chip);

  /* Toggle indicator */
  const arrow = document.createElement('span');
  arrow.style.cssText =
    'float:right;font-size:0.8rem;color:#0f766e;user-select:none;margin-top:2px;';
  arrow.textContent = '▾';
  h2.appendChild(arrow);

  h2.addEventListener('click', () => {
    const collapsed = h2.dataset.collapsed === 'true';
    siblings.forEach(s => s.style.display = collapsed ? '' : 'none');
    h2.dataset.collapsed = collapsed ? 'false' : 'true';
    h2.style.borderBottomColor = collapsed ? '' : 'transparent';
    chip.style.display = collapsed ? 'none' : 'inline';
    arrow.textContent = collapsed ? '▾' : '▸';
  });
});

/* ── Sticky top-of-page TOC (auto-generated from h2s) ── */
(function buildTOC() {
  const headings = [...document.querySelectorAll('.content .card h2')];
  if (headings.length < 4) return;
  const nav = document.createElement('nav');
  nav.id = 'toc';
  nav.style.cssText =
    'position:sticky;top:0;z-index:100;background:rgba(255,253,248,0.95);' +
    'border-bottom:1px solid #d9d0c0;padding:8px 24px;font-size:0.82rem;' +
    'display:flex;flex-wrap:wrap;gap:6px 18px;';
  headings.forEach((h, i) => {
    if (!h.id) h.id = 'sec-' + i;
    const a = document.createElement('a');
    a.href = '#' + h.id;
    a.textContent = h.textContent;
    a.style.cssText = 'color:#0f766e;text-decoration:none;white-space:nowrap;';
    a.onmouseenter = () => a.style.textDecoration = 'underline';
    a.onmouseleave = () => a.style.textDecoration = 'none';
    nav.appendChild(a);
  });
  document.body.insertBefore(nav, document.querySelector('.content'));
})();

/* ── Back-to-top button ── */
const btn = document.createElement('button');
btn.textContent = '↑ Top';
btn.style.cssText =
  'position:fixed;bottom:28px;right:28px;padding:8px 14px;background:#0f766e;' +
  'color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:0.85rem;' +
  'opacity:0;transition:opacity 0.2s;z-index:200;';
document.body.appendChild(btn);
window.addEventListener('scroll', () => btn.style.opacity = scrollY > 300 ? '1' : '0');
btn.addEventListener('click', () => window.scrollTo({top:0,behavior:'smooth'}));
</script>
```

---

## 3. Section Catalog

### 3.1 Required by all artifact types

#### HERO

```html
<header class="hero">
  <div class="hero-inner">
    <div class="eyebrow">WRK-NNN · {{artifact_type}}</div>
    <h1>{{title}}</h1>
    <p class="lede">{{lede}}</p>
  </div>
</header>
```

`artifact_type` values: `Plan Draft Review` | `Plan Final Review` |
`Implementation Review` | `Close Review` | `Governance Artifact`

`lede` = one sentence summarising the artifact's key finding or decision.

---

#### METADATA GRID

Immediately after `<main class="content">`, before the first card:

```html
<div class="meta">
  <div class="pill"><strong>WRK ID</strong>WRK-NNN</div>
  <div class="pill"><strong>Status</strong>{{status}}</div>
  <div class="pill"><strong>Route</strong>{{route}} — {{complexity}}</div>
  <div class="pill"><strong>Orchestrator</strong>{{orchestrator}}</div>
  <div class="pill"><strong>Computer</strong>{{computer}}</div>
  <div class="pill"><strong>Created</strong>{{created_at|date}}</div>
  <div class="pill"><strong>Commit</strong><code>{{commit|truncate:7}}</code></div>
  <div class="pill"><strong>% Done</strong>{{percent_complete}}%</div>
</div>
```

---

#### EXECUTIVE SUMMARY

Always the first section inside the first card:

```html
<div class="exec-summary">
  <h2>Executive Summary</h2>
  <ul>
    <li>{{outcome_1}}</li>
    <li>{{outcome_2}}</li>
    ...
  </ul>
</div>
```

---

### 3.2 Plan artifacts (stages 5 + 7)

**Sections in order:**

| # | Section | Stage | Notes |
|---|---------|-------|-------|
| 4 | Prompt Start Context | 5 + 7 | Verbatim original request; `<div class="panel">` |
| 5 | Why | 5 + 7 | Rationale bullet list |
| 6 | Acceptance Criteria | 5 + 7 | `[ ]` / `[x]` checkboxes; convert `- [ ]` → `☐`, `- [x]` → `☑` |
| 7 | Agentic AI Horizon | 5 + 7 | AI-horizon analysis paragraph |
| 8 | Plan | 5 + 7 | Phases as `<h3>` sub-sections |
| 9 | Resource Intelligence | 5 + 7 | Key files, constraints, scope context |
| 9a | Gate-Pass Stage Status | 5 + 7 | Stage-by-stage table + summary; review before user-facing recommendation |
| 10 | Open Questions | 5 only | Unresolved items; omit if none |
| 11 | Changes from Draft | 7 only | What changed after cross-review |
| 12 | Cross-Review Summary | 7 only | Provider verdict table (see §3.4) |
| 13 | User Approval | 7 only | Explicit `plan_approved: true` record |

---

### 3.3 Implementation artifacts (stages 11 + 13)

**Sections in order:**

| # | Section | Notes |
|---|---------|-------|
| 14 | Execution Brief | Narrative of what was built |
| 15 | Files Changed | Table: File, Action (new/edit/delete), Lines ±, Commit |
| 16 | Cross-Review Summary | Provider verdicts post-implementation (see §3.4) |
| 17 | Test Summary | Table: #, Name, Scope, Result, Command, Artifact |
| 18 | Gate Evidence Summary | `verify-gate-evidence.py` output — PASS/WARN/FAIL per gate |
| 19 | Stage Evidence Ledger | All 20 stages: order, stage, status badge, evidence path |
| 20 | Skill Manifest | Skills invoked; table: skill, version, trigger |

---

### 3.4 Close artifacts (stages 17 + 19)

**Sections in order (all implementation sections, then):**

| # | Section | Notes |
|---|---------|-------|
| 21 | Future Work | Table: WRK-ID, title, disposition, status |
| 22 | Resource Intelligence Update | Post-work addenda; new files/tools discovered |
| 23 | Lifecycle Enforcement Progress | Table: workstream, status, evidence, notes |
| 24 | Next Work | Disposition table for deferred items |
| 25 | Asset Index | `.artifact-box` — bullet list of all evidence file paths |
| 25a | Gate-Pass Stage Status | Stage-by-stage table + summary; mandatory review in stage 17 |

---

### 3.5 Cross-Review Summary (re-used in §3.2 + §3.3)

```html
<h2>Cross-Review Summary</h2>
<table>
  <thead>
    <tr><th>Provider</th><th>Verdict</th><th>Findings</th><th>Fixed</th><th>Notes</th></tr>
  </thead>
  <tbody>
    <tr>
      <td>Claude</td>
      <td><span class="badge badge-pass">APPROVE</span></td>
      <td>3 minor</td><td>3/3</td><td>...</td>
    </tr>
    <tr>
      <td>Codex</td>
      <td><span class="badge badge-warn">MINOR</span></td>
      <td>2 minor</td><td>2/2</td><td>NO_OUTPUT acceptable</td>
    </tr>
    <tr>
      <td>Gemini</td>
      <td><span class="badge badge-pass">APPROVE</span></td>
      <td>1 minor</td><td>1/1</td><td>...</td>
    </tr>
  </tbody>
</table>
```

Verdict badge mapping: `APPROVE` → `badge-pass` | `MINOR` → `badge-warn` | `MAJOR` → `badge-fail` | `NO_OUTPUT` → `badge-info`

---

### 3.6 Stage Evidence Ledger

```html
<h2>Stage Evidence Ledger</h2>
<table>
  <thead>
    <tr><th>#</th><th>Stage</th><th>Status</th><th>Evidence</th></tr>
  </thead>
  <tbody>
    <!-- repeat for all 20 stages -->
    <tr>
      <td>1</td><td>Capture</td>
      <td><span class="badge badge-pass">done</span></td>
      <td><code>.claude/work-queue/working/WRK-NNN.md</code></td>
    </tr>
    ...
  </tbody>
</table>
```

Stage status → badge: `done` → `badge-pass` | `in-progress` → `badge-warn` | `pending` → `badge-info` | `skipped` → *(no badge)* | `missing` → `badge-fail`

---

### 3.7 Optional sections

Include when the WRK evidence contains these; omit otherwise:

| Section | When to include |
|---------|----------------|
| Validation Evidence | Additional validation beyond tests |
| Scope & Strategy | Complex Route C items with phased scope |
| Scripts & Validators | Script inventory for technical WRKs |
| Deviation Table | When plan deviated from implementation |
| Domain Notes / Assumptions / Constraints | Engineering domain context |
| Rerun History | When a stage was repeated |
| Reclaim Notes | When `reclaim.yaml` is present in evidence |

---

## 4. Full Document Structure

```
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{artifact_type}}: WRK-NNN — {{title_short}}</title>
  <style>
    /* § 1 Design System — paste verbatim */
  </style>
</head>
<body>

  <!-- § 3.1 Hero -->
  <header class="hero">...</header>

  <!-- § 3.1 Metadata Grid -->
  <!-- Auto-TOC injected here by JS if ≥4 sections -->

  <main class="content">
    <div class="meta">...</div>

    <div class="card">
      <!-- § 3.1 Executive Summary (always first in card) -->
      <div class="exec-summary">...</div>

      <!-- § 3.2 / 3.3 / 3.4 sections per artifact type, in catalog order -->
      <h2>...</h2>
      ...
    </div>

    <!-- Additional cards for long artifacts (split after ~5 h2 sections) -->
  </main>

  <!-- § 2 Interactivity Layer -->
  <script>...</script>
</body>
</html>
```

**Card splitting rule:** create a new `<div class="card">` every 5–6 `<h2>` sections to
keep scroll areas manageable and box-shadow grouping logical.

---

## 5. Generator Script Integration

`scripts/work-queue/generate-html-review.py` must use this skill's design system.

### 5.1 Template function signature

```python
def render_wrk_html(
    wrk_meta: dict,           # frontmatter fields
    artifact_type: str,       # "plan-draft" | "plan-final" | "implementation" | "close"
    sections: dict[str, str], # section-name → HTML/markdown content
    evidence: dict | None = None,  # stage-evidence YAML
) -> str:
    """Return complete HTML string conforming to workflow-html SKILL v1.0.0."""
```

### 5.2 Artifact type → section set

| `artifact_type` | Required sections (§ numbers) |
|-----------------|-------------------------------|
| `plan-draft`    | 1–3, 4–10 |
| `plan-final`    | 1–3, 4–13 |
| `implementation`| 1–3, 14–20 |
| `close`         | 1–3, 14–25 |

### 5.3 Calling convention

```bash
# Generate plan-draft HTML for WRK-1011
uv run --no-project python scripts/work-queue/generate-html-review.py \
  --wrk WRK-1011 \
  --type plan-draft \
  --output .claude/work-queue/assets/WRK-1011/plan-draft-review.html

# Generate close HTML
uv run --no-project python scripts/work-queue/generate-html-review.py \
  --wrk WRK-1011 \
  --type close \
  --output .claude/work-queue/assets/WRK-1011/workflow-final-review.html
```

---

## 6. Mandatory Usage (Workflow Harness Integration)

This skill is **mandatory** at the following stages. An agent must not proceed to the next
stage without producing a conforming HTML artifact and opening it in the default browser.

At user-review checkpoints (stages 5, 7, and 17), agents must review the
`Gate-Pass Stage Status` section with the user before presenting recommendations.

| Stage | Artifact type | Trigger |
|-------|--------------|---------|
| 5 — User Review Plan (Draft) | `plan-draft` | Before presenting draft to user |
| 7 — User Review Plan (Final) | `plan-final` | After cross-review, before user approval |
| 11 — Artifact Generation | `implementation` | After execution phase completes |
| 17 — User Review Implementation | `close` | Before user close review |
| 19 — Close | `close` | Auto-generated by `close-item.sh` |

### Browser open (mandatory evidence)

```bash
xdg-open .claude/work-queue/assets/WRK-NNN/<artifact>.html
# log: html_open_default_browser signal via scripts/work-queue/log-user-review-browser-open.sh
```

---

## 7. Compliance Checklist (per artifact)

Before handing an HTML artifact to the user, verify:

```
[ ] Design system: uses warm-parchment CSS variables (--bg #f3efe6, --accent #0f766e)
[ ] Hero: eyebrow contains WRK-ID + artifact type; H1 is the WRK title
[ ] Metadata grid: all 8 pill fields present (or "n/a" if not yet available)
[ ] Executive Summary: first element in first card; teal left border
[ ] Sections: in catalog order for this artifact type
[ ] Status badges: PASS/WARN/FAIL colored correctly
[ ] Interactivity: collapsible cards, sticky TOC (if ≥4 sections), back-to-top button
[ ] Print media query: present in <style>
[ ] No inline styles on individual elements (all via CSS classes)
[ ] File opened in default browser and signal logged
```

---

## Version History

- **1.2.0** (2026-03-05): Gate-pass section integration
  - Added `Gate-Pass Stage Status` as a required user-review section for stages 5/7/17 artifacts
  - Requires table + summary view and explicit review before user-facing recommendation
  - Synced generator behavior to include stage/gate table from `evidence/stage-evidence.yaml`

- **1.1.0** (2026-03-04): Generator enhancements (WRK-1011)
  - `_suppress_duplicate_generated_sections()`: avoids double Skill Manifest / Test Summary / Cross-Review when body already contains them
  - `_append_missing_key_sections()`: stubs missing canonical sections as "Not applicable."
  - `_normalize_close_section_names()`: maps "Future Work" → "Next Work" in close artifacts
  - `KEY_SECTIONS_BY_ARTIFACT` map with 4 artifact types
  - Archive subdirectory search (`archive/**/*.md`)
  - Chip opacity toggle (always visible, dims when expanded; `.section-summary-chip` CSS class)
  - 29 unit tests pass

- **1.0.0** (2026-03-04): Initial release (WRK-1011)
  - Warm-parchment design system from WRK-624/WRK-690 reference
  - 25-section catalog across 4 artifact types
  - Interactivity: collapsible cards with summary/status chips, auto-TOC, back-to-top, smooth scroll
  - Status badge system (PASS/WARN/FAIL/INFO)
  - Generator script integration spec (`render_wrk_html()`)
  - Mandatory stage wiring (5, 7, 11, 17, 19)
