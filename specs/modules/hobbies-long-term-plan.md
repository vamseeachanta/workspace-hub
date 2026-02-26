---
title: "Hobbies Repo Long-Term Plan"
description: "Define the purpose, structure, and content roadmap for the Hobbies personal knowledge-management repository, and remove scaffolding bloat that drowns actual content."
version: "1.0"
module: "hobbies"

session:
  id: "wrk-041-hobbies-plan"
  agent: "claude-sonnet-4-6"
  started: "2026-02-24"
  last_active: "2026-02-24"
  conversation_id: ""

review:
  required_iterations: 3
  current_iteration: 1
  status: "approved"
  reviewers:
    openai_codex:
      status: "approved"
      iteration: 1
      last_reviewed: "2026-02-10"
      feedback: "Content inventory accurate; scaffolding bloat confirmed. sdev/ has 8 items vs plan 2-file claim (minor undercount)."
    google_gemini:
      status: "approved"
      iteration: 1
      last_reviewed: "2026-02-10"
      feedback: "Content inventory accurate, scaffolding bloat confirmed."
    legal_sanity:
      status: "passed"
      iteration: 1
      violations: 0
  approval_gate:
    min_iterations_met: true
    codex_approved: true
    gemini_approved: true
    legal_sanity_passed: true
    ready_for_next_step: true

status: "approved"
progress: 15
phase: 1
blocked_by: []

created: "2026-01-29"
updated: "2026-02-24"
target_completion: "2026-06-30"
timeline: "5 months (phased, low-priority)"
milestones:
  - name: "Plan document produced"
    target_date: "2026-02-24"
    status: "complete"
  - name: "Scaffolding cleanup"
    target_date: "2026-03-31"
    status: "pending"
  - name: "README and CLAUDE.md simplified"
    target_date: "2026-03-31"
    status: "pending"
  - name: "Active-category content expanded"
    target_date: "2026-05-31"
    status: "pending"
  - name: "Static-site evaluation"
    target_date: "2026-06-30"
    status: "pending"

author: "claude-sonnet-4-6 (WRK-041)"
reviewers:
  - "claude-opus-4-6"
  - "gemini-cli"
assignees:
  - "ace-linux-1"

technical:
  language: "markdown"
  python_version: "N/A"
  dependencies: []
  test_coverage: 0
  platforms: ["linux"]

priority: "low"
complexity: "medium"
risk: "low"
tags: ["hobbies", "documentation", "pkm", "cleanup", "roadmap"]

links:
  spec: "specs/modules/hobbies-long-term-plan.md"
  branch: ""
  pr: ""
  issues: []
  docs:
    - "hobbies/docs/repo-audit.md"
    - "hobbies/docs/roadmap.md"
    - "hobbies/README.md"
    - "hobbies/CLAUDE.md"

history:
  - date: "2026-01-29"
    action: "created"
    by: "WRK-041"
    notes: "Initial WRK item created."
  - date: "2026-02-10"
    action: "cross-reviewed"
    by: "claude-opus-4-6 + gemini-cli"
    notes: "Both approved. Codex produced no output."
  - date: "2026-02-24"
    action: "plan-document-produced"
    by: "claude-sonnet-4-6"
    notes: "Full content audit completed; spec, audit, and roadmap written."
---

# Hobbies Repo Long-Term Plan

> **Module**: hobbies | **Status**: approved | **Priority**: low
> **Created**: 2026-01-29 | **Target**: 2026-06-30

---

## Executive Summary

The `hobbies` repository is a personal and family knowledge-management (PKM) system covering gardening, sports, arts, cultural activities, autism support resources, and personal-development content. Its primary users are the owner and immediate family members.

The repo's central problem is **signal-to-noise ratio**: approximately 90% of the files on disk are scaffolding boilerplate deposited by various AI agent frameworks (`.agent-os/`, `.claude-flow/`, `.hive-mind/`, `.swarm/`, `agents/`, `coordination/`, and root-level Python scripts). The actual hobby content amounts to roughly 25 markdown files and a handful of PDFs, yet it is buried under hundreds of agent-framework files that add zero value to a documentation-only repo.

This plan defines the repo's purpose, maps its current state accurately, prescribes a cleanup sequence, and sets content-growth goals per category for the next six months.

---

## Current State Assessment (Audit)

### Content Inventory (actual hobby content only)

| Category | Markdown Files | PDFs / Images | Notes |
|----------|---------------|---------------|-------|
| gardening/ | 4 (mango, watermelon, dosakai, drumstick) | 0 | Picking guides; drumstick growing stub |
| sports/swimming/ | 4 (freestyle, healthy_practices, training, village_piranhas) | 1 PDF, 1 JPG | Plus 3 per-swimmer logs (bar, dpt, kanna) |
| sports/soccer/ | 1 (soccer.md) | 3 PDFs (FIFA laws x2, Football-Stories), 1 PDF (Videographer) | soccer.md contains credentials — needs sanitisation |
| sports/cycling/ | 0 | 1 PDF (Stumpjumper manual) | No markdown content |
| sports/tennis/ | 0 | 2 PDFs (Aceing Autism visual schedule, virtual training) | No markdown content |
| sports/volleyball/ | 0 | Multiple logo images + 2 xlsx team-member lists | mission_impassibles team assets; no narrative content |
| sports/waterpolo/ | 0 | 0 | Empty |
| arts-music/ | 0 | 3 PDFs (2 carnatic theory, 1 tuition) | No markdown content |
| autism/ | 0 | 1 PDF (Medicaid resources) | No markdown content |
| cultural/ | 1 (bala_vihar.md — 2 lines) | 0 | Stub only |
| sdev/ | 2 (50_golden_rules.md, visualization.md) | 4 PDFs, 2 images | Mixed life-advice and sport-visualization content |
| sports.md (root) | 1 | 0 | Activities overview for one family member |

**Total actual content**: ~25 markdown files (many are stubs), ~15 PDFs, ~25 images/xlsx files.

### Scaffolding Bloat

The following directories contain zero hobby content and should be removed or heavily trimmed:

| Directory / File | Nature | Recommendation |
|-----------------|--------|----------------|
| `.agent-os/` | Agent-OS framework (50+ Python files, templates) | Remove entirely |
| `.claude/agents/` | 60+ agent definition markdown files | Remove entirely; AGENTS.md adapter is sufficient |
| `.claude/commands/` | Slash-command definitions for agent frameworks | Remove entirely |
| `agents/` | Sample agent markdown files | Remove entirely |
| `coordination/` | Agent coordination boilerplate | Remove entirely |
| `modules/` | Automation scripts | Remove entirely |
| `scripts/` | Automation scripts | Remove entirely |
| `src/`, `tests/`, `htmlcov/` | Python project skeleton | Remove entirely |
| `.benchmarks/`, `.drcode/`, `memory/`, `data/`, `reports/` | Agent framework data dirs | Remove entirely |
| `slash/`, `agos` | Agent-OS symlink / helper | Remove |
| Root `.py` files | `create-spec*.py`, `execute-tasks.py`, `slash_commands.py`, `create-module-agent.py` | Remove |
| Root config | `pyproject.toml`, `uv.toml`, `Makefile` | Remove (no Python code in repo) |
| Root docs | `AGENT_OS_COMMANDS.md`, `MANDATORY_SLASH_COMMAND_ECOSYSTEM.md`, `COMMANDS.md`, `AGENTS.md` | Replace with clean README |
| `hobbies/docs/` | `AI_AGENT_ORCHESTRATION.md`, `HTML_REPORTING_STANDARDS.md`, `api/`, `guides/`, `modules/` | Remove; replace with content docs |
| `.claude/CLAUDE.md` | 500-line software-engineering/orchestration ruleset | Replace with 20-line hobby-PKM context |

### Security Note

`sports/soccer/soccer.md` contains plaintext credentials (username, password, player ID, volunteer ID, email address). These must be removed or redacted before any public exposure of the repo. See Phase 1 tasks.

---

## Purpose and Scope

**Purpose**: A private, family-facing knowledge base that captures practical information, training logs, and reference material for the family's active hobbies and life interests. It is not a software project.

**In scope**:
- Gardening guides (growing, picking, seasonal notes)
- Sports training logs and reference guides (swimming, soccer, volleyball, tennis, cycling, water polo)
- Arts and music references (carnatic music, tuition notes)
- Cultural activities (Bala Vihar, Hindu Society)
- Autism-related resources (therapy, IEP, community services, Medicaid)
- Personal development (life rules, visualization, books)

**Out of scope**:
- Software code
- Agent framework configuration
- Automated CI/CD pipelines
- HTML reports or dashboards
- Any content that belongs in a dedicated dev-learning repo (consider migrating `sdev/` to `pyproject-starter` or similar)

**Audience**: Owner and immediate family. Private repository; no public publishing intended at this stage.

---

## Phases

### Phase 1: Security and Scaffolding Cleanup

**Objective**: Remove credentials exposure and eliminate scaffolding that obscures the actual content.

**Tasks**:
- [ ] 1.1: Redact credentials from `sports/soccer/soccer.md` — replace with placeholder comments pointing to a password manager.
- [ ] 1.2: Remove `.agent-os/` directory tree entirely.
- [ ] 1.3: Remove `.claude/agents/` and `.claude/commands/` subdirectories (keep `.claude/CLAUDE.md` as a stub and `hobbies/.claude/` workspace-hub adapter).
- [ ] 1.4: Remove `agents/`, `coordination/`, `modules/`, `scripts/`, `src/`, `tests/`, `htmlcov/` directories.
- [ ] 1.5: Remove root Python scripts and config files (`create-spec*.py`, `execute-tasks.py`, `slash_commands.py`, `create-module-agent.py`, `pyproject.toml`, `uv.toml`, `Makefile`).
- [ ] 1.6: Remove `data/`, `reports/`, `memory/`, `.benchmarks/`, `.drcode/`, `agos` symlink, `slash/`.
- [ ] 1.7: Remove `docs/AI_AGENT_ORCHESTRATION.md`, `docs/HTML_REPORTING_STANDARDS.md`, `docs/api/`, `docs/guides/`, `docs/modules/`.
- [ ] 1.8: Remove root `AGENT_OS_COMMANDS.md`, `MANDATORY_SLASH_COMMAND_ECOSYSTEM.md`, `COMMANDS.md`, `AGENTS.md` (keep workspace-hub-generated `CLAUDE.md` adapter).
- [ ] 1.9: Remove `.claude/CLAUDE.md` 500-line ruleset; replace with a minimal 20-line hobby-PKM context (see Phase 2).
- [ ] 1.10: Commit cleanup with message `chore(hobbies): remove scaffolding bloat (WRK-041)`.

**Deliverables**:
- [ ] Cleaned repo where `git ls-files` shows only actual content plus `.claude/` workspace-hub adapter

**Exit Criteria**:
- [ ] No Python source files remain in repo root or `src/`
- [ ] Credential strings removed from `soccer.md`
- [ ] File count reduced by at least 80%

---

### Phase 2: README, CLAUDE.md, and Structure

**Objective**: Give the repo a clear identity and simplify its configuration surface.

**Tasks**:
- [ ] 2.1: Rewrite `README.md` with a clear purpose statement, category index, and contributing guidance.
- [ ] 2.2: Replace `.claude/CLAUDE.md` with a 20-line hobby-PKM context (repo purpose, content categories, no-code rule, note style guide).
- [ ] 2.3: Decide fate of dormant categories:
  - **Remove** empty stubs for `waterpolo/` (no content, no active participation evidence).
  - **Keep as stubs** `cycling/` and `tennis/` — they have PDFs and clear family interest.
  - **Keep** `volleyball/` — mission_impassibles team assets are active.
  - **Keep** `arts-music/` — PDFs exist; curriculum notes planned.
- [ ] 2.4: Create `docs/repo-audit.md` capturing this audit snapshot (date, file counts, category health).
- [ ] 2.5: Create `docs/roadmap.md` (see Phase 4 deliverable below).
- [ ] 2.6: Commit with message `docs(hobbies): add README, audit, roadmap (WRK-041)`.

**Deliverables**:
- [ ] `README.md` — purpose statement and category index
- [ ] `.claude/CLAUDE.md` — 20-line PKM context
- [ ] `docs/repo-audit.md` — snapshot of current content state
- [ ] `docs/roadmap.md` — content goals per category

**Exit Criteria**:
- [ ] README accurately describes the repo to a new family member
- [ ] CLAUDE.md fits the 20-line rule from workspace-hub coding-style rules

---

### Phase 3: Content Enrichment — High-Priority Categories

**Objective**: Expand content depth in the categories with the most active use.

**Gardening** (active; 4 files, all picking guides):
- [ ] 3.1: Add growing sections to `fruit_mango.md` (soil, watering, container vs ground, Houston climate zone).
- [ ] 3.2: Complete `veg_drumstick.md` growing section (stem propagation, spacing, water requirements).
- [ ] 3.3: Create `gardening/seasonal-calendar.md` — monthly task checklist for Houston climate (Zone 9a).
- [ ] 3.4: Create `gardening/veg_bittergourd.md` and `gardening/veg_tindora.md` if grown.

**Swimming** (active; 4 files + 3 swimmer logs):
- [ ] 3.5: Update each swimmer log (`bar.md`, `dpt.md`, `kanna.md`) with 2025 season data if available.
- [ ] 3.6: Create `swimming/competition-schedule.md` — Village Piranhas meet calendar format.
- [ ] 3.7: Expand `freestyle.md` with technique notes beyond links (body position, rotation, breathing pattern).
- [ ] 3.8: Create `swimming/stroke-reference.md` covering backstroke, breaststroke, butterfly basics.
- [ ] 3.9: Expand `training.md` from a URL stub to a structured training progression guide.

**Autism** (1 PDF; no markdown):
- [ ] 3.10: Create `autism/README.md` — index of resources by type (Medicaid, IEP, therapy, community).
- [ ] 3.11: Create `autism/iep-tracker.md` — template for IEP goal tracking by school year.
- [ ] 3.12: Create `autism/community-resources.md` — Houston-area therapy and community programs.
- [ ] 3.13: Create `autism/sports-inclusion.md` — aggregating the Aceing Autism / autism sports links currently scattered in `sports.md` and tennis directory.

**Exit Criteria**:
- [ ] Each active category has at least one substantive markdown file (not a URL stub)
- [ ] Swimmer logs reflect current season if data exists

---

### Phase 4: Content Enrichment — Secondary Categories

**Objective**: Establish minimum viable content in lower-activity categories.

**Soccer**:
- [ ] 4.1: Sanitise `soccer.md` — remove all credentials (done in Phase 1); replace with general team/league reference.
- [ ] 4.2: Create `soccer/training-drills.md` — age-appropriate drills reference for youth players.
- [ ] 4.3: Create `soccer/league-guide.md` — FFPS league structure, season calendar, volunteering roles.

**Cultural**:
- [ ] 4.4: Expand `bala_vihar.md` from a 2-line stub to include curriculum overview, event calendar format, and contact info.
- [ ] 4.5: Create `cultural/arya-samaj.md` for Houston Arya Samaj Sunday Satsang details.
- [ ] 4.6: Create `cultural/festivals.md` — family-relevant Hindu festival calendar with brief descriptions.

**Arts/Music**:
- [ ] 4.7: Create `arts-music/carnatic-basics.md` — summarise key concepts from the theory PDFs for quick reference.
- [ ] 4.8: Create `arts-music/tuition-log.md` — log of lessons, progress, and practice assignments.

**Volleyball**:
- [ ] 4.9: Create `volleyball/mission_impassibles/README.md` — team overview, season schedule, roster format.
- [ ] 4.10: Create `volleyball/rules-reference.md` — core volleyball rules for recreational play.

**sdev/ (Personal Development)**:
- [ ] 4.11: Decision point — evaluate whether `sdev/` belongs in `hobbies/` or in a dedicated `life-learning/` repo. If kept, rename to `personal-dev/` for clarity.
- [ ] 4.12: Create `personal-dev/reading-list.md` — books referenced in PDFs (12 Lessons from Japan, Stop Apologizing, etc.) with brief notes.
- [ ] 4.13: Create `personal-dev/practices.md` — aggregating visualization, golden rules, and growth mindset notes into one navigable document.

**Exit Criteria**:
- [ ] Every category directory has at least one markdown file
- [ ] No category is represented only by PDFs with no accompanying text

---

### Phase 5: Long-Term Options (Deferred)

**Objective**: Evaluate if the repo warrants further investment as a platform.

**Tasks** (revisit only if daily-use patterns justify it):
- [ ] 5.1: Evaluate Jekyll or Hugo static site generation for browsable family reference site.
- [ ] 5.2: Evaluate whether a GitHub Pages deployment would serve the family better than a local git repo.
- [ ] 5.3: Evaluate splitting `autism/` into a dedicated `autism-resources/` repo if content volume justifies it.
- [ ] 5.4: Add a simple `index.md` aggregating all category landing pages.

**Exit Criteria**:
- [ ] Decision documented in `docs/roadmap.md` with rationale

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Scaffolding removal breaks workspace-hub hooks | Low | Low | Only delete content unrelated to `.claude/` workspace adapter; test `git status` after each deletion batch |
| soccer.md credentials already in git history | High | High | After Phase 1 sanitisation, evaluate `git filter-repo` to scrub history; note repo is private |
| Content stagnates after initial cleanup | Medium | Medium | Tie content updates to seasonal events (swim season, garden season) rather than calendar deadlines |
| sdev/ content overlap with other repos | Low | Low | Phase 4.11 decision point explicitly handles this |
| Volleyball assets (xlsx, images) grow large | Low | Low | Monitor with `git lfs` if binary size becomes an issue |

---

## Routing and Priority

Per WRK-041 disposition note: this is **low strategic value** and deprioritised. Phases 1 and 2 (cleanup and restructure) are the minimum viable deliverable. Phases 3 and 4 are opportunistic — execute during quiet periods or when a specific family member has a near-term need. Phase 5 is deferred indefinitely.

Recommended execution order:
1. Phase 1 (security + cleanup) — execute as soon as approved; one session
2. Phase 2 (README, CLAUDE.md, docs) — immediately after Phase 1; one session
3. Phase 3 items triggered by season (e.g., swim-season start triggers 3.5–3.9)
4. Phase 4 items on an as-needed basis

---

## Cross-Review Process

### Review Status

| Gate | Requirement | Status |
|------|-------------|--------|
| Minimum Iterations | >= 1 iteration completed (low-priority repo) | Met (2026-02-10) |
| Legal Sanity | No block violations | Passed |
| Claude Opus 4.6 | Approved | Approved (2026-02-10) |
| Gemini CLI | Approved | Approved (2026-02-10) |
| Codex CLI | Approved | No output (treated as non-blocking for low-priority) |
| **Ready for Next Step** | All gates passed | **APPROVED** |

### Review Iteration Log

| Iteration | Date | Reviewer | Status | Key Feedback |
|-----------|------|----------|--------|--------------|
| 1 | 2026-02-10 | Claude Opus 4.6 | Approved | Content inventory accurate; scaffolding bloat confirmed |
| 1 | 2026-02-10 | Gemini CLI | Approved | Content inventory accurate; sdev/ has 8 items not 2 |
| 1 | 2026-02-10 | Codex CLI | No output | Non-blocking for low-priority WRK |

---

## Appendix

### A. File Count Summary (pre-cleanup)

| Type | Count |
|------|-------|
| Actual hobby markdown files | ~25 |
| Actual PDFs / images / xlsx | ~42 |
| Scaffolding Python files | ~60 |
| Scaffolding markdown files (agents, commands) | ~80 |
| Scaffolding yaml / config files | ~15 |
| **Total (estimated)** | **~222** |

Post-cleanup target: fewer than 80 files total.

### B. Category Health at Plan Date (2026-02-24)

| Category | Health | Reason |
|----------|--------|--------|
| gardening | Fair | 4 files but thin; picking-only, no growing guides |
| swimming | Good | Multiple files + active swimmer logs (2025 data present) |
| soccer | Poor | 1 file with credentials; PDFs unlinked |
| cycling | Poor | 1 PDF, zero markdown |
| tennis | Poor | 2 PDFs, zero markdown; autism-sports links scattered |
| volleyball | Fair | Active team assets; no narrative content |
| waterpolo | Poor | Empty |
| arts-music | Poor | 3 PDFs, zero markdown |
| autism | Poor | 1 PDF, zero markdown |
| cultural | Poor | 2-line stub |
| sdev/personal-dev | Fair | 2 markdown files, several PDFs; needs decision on repo placement |

### C. Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-24 | claude-sonnet-4-6 | Initial plan produced from WRK-041 audit |

---

*Plan produced for WRK-041 — workspace-hub plan template v1.0*
