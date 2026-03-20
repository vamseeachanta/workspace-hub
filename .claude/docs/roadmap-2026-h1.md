# Repo Ecosystem Roadmap — 2026 H1
*WRK-235 | Established: 2026-02-20 | Last updated: 2026-03-19 | Cadence: monthly review (first Friday)*

## Ecosystem Vision — August 2026

An agent can run a complete engineering analysis (fatigue, FFS, wall thickness, drilling economics)
end-to-end with a single invocation. Session analysis runs nightly without intervention. Client-facing
content on aceengineer-website is generated from live data and module outputs. The work queue is
net-shrinking. Provider strategy is validated by cost data.

---

## Repo Assessment
*Pending WRK = items with `status: pending` targeting repo. Archived WRK = completed items.*
*Strategic value 1–5, Agentic readiness 1–5 (1=low, 5=high). Investment: high/medium/low/defer.*
*Updated: 2026-03-19 — counts from archive synthesis (410 archived, 363 pending, 381 migrated to GitHub Issues)*

| Repo | Strategic Value | Agentic Readiness | Pending WRK | Archived WRK | Priority | August 2026 Target |
|------|:-:|:-:|:-:|:-:|----------|---------------------|
| `workspace-hub` | 5 | **5** | 112 | 220 | **high** | Autonomous session lifecycle; self-improving loop live |
| `digitalmodel` | 5 | 3 | 114 | 76 | **high** | All major modules agent-callable; test coverage ≥80% |
| `worldenergydata` | 5 | 3 | 27 | 66 | **high** | All sources queryable by agents; refresh scheduled |
| `assethold` | 4 | **4** | 5 | 5 | **high** | Agents run daily strategy autonomously |
| `assetutilities` | 4 | **4** | 0 | 10 | **high** | Shared utilities stable; used by assethold and agents |
| `aceengineer-website` | 5 | 2 | 3 | 6 | **high** | Agents generate + publish content from module outputs |
| `aceengineer-admin` | 3 | 2 | 1 | 2 | medium | Admin workflows documented; agent-executable |
| `achantas-data` | 3 | 2 | 2 | 6 | medium | Data indexed; queryable by agents |
| `doris` | 3 | 3 | 21 | 0 | medium | Pipeline structure clean; agent-callable for data pull |
| `saipem` | 3 | 3 | 0 | 1 | medium | Installation modules stable; benchmarked |
| `acma-projects` | 3 | 2 | 1 | 2 | medium | Structural modules integrated with digitalmodel |
| `frontierdeepwater` | 2 | 2 | 6 | 4 | low | Vessel data extracted; minimal ongoing investment |
| `OGManufacturing` | 2 | 2 | 8 | 1 | low | Stable; no new investment unless client need arises |
| `rock-oil-field` | 2 | 2 | 0 | 2 | low | OrcaFlex models catalogued (WRK-121); then park |
| `pdf-large-reader` | 2 | 3 | 1 | 1 | low | Utility tool; maintain, no expansion |
| `pyproject-starter` | 2 | 4 | 0 | 0 | low | Template stable; update when ecosystem changes |
| `CAD-DEVELOPMENTS` | 2 | 1 | 0 | 1 | low | FEA pipeline scaffolded; park until needed |
| `sd-work` | 1 | 2 | 0 | 0 | defer | No pending items; check quarterly |
| `seanation` | 1 | 1 | 0 | 0 | defer | No active engineering use; park |
| `teamresumes` | 1 | 2 | 0 | 0 | defer | Manual process; agent automation low ROI |
| `hobbies` | 1 | 1 | 0 | 0 | defer | Personal; no compound value |
| `sabithaandkrishnaestates` | 1 | 2 | 3 | 1 | defer | Reactive only |

**Archive synthesis insight (2026-03-19):** Full categorization of 410 archived WRKs reveals effort
concentration: **harness 155 (38%)**, **engineering 100 (24%)**, **data 49 (12%)**, platform/tooling 23 (6%),
personal/maintenance 18 (4%). The harness dominance reflects Q1 infrastructure buildout; this investment
is now largely complete. Engineering subcategory breakdown: hydrodynamics (29), drilling (15), pipeline (9),
safety (9), cathodic protection (8) — these map directly to `digitalmodel` modules.

**Repo count corrections (March 2026):** Previous counts (2026-03-10) over-estimated archives for
`digitalmodel` (103→76) and `worldenergydata` (94→66) because many items lacked `target_repos` and
were counted by title heuristic. Corrected counts are from frontmatter `target_repos` field.
`workspace-hub` archive count grew substantially (131→220) as harness WRKs were properly attributed.

**Critical path repos**: `workspace-hub`, `digitalmodel`, `worldenergydata`, `assethold`, `assetutilities`,
`aceengineer-website` — these 6 receive all high-priority investment.

---

## AI Provider Strategy

### Current State (March 2026)
*Tool versions: Claude 2.1.72, Codex CLI 0.112.0, Gemini 0.32.1 (dev-primary, verified 2026-03-09)*

| Provider | Role Today | Unique Capability | Gap vs Claude |
|----------|-----------|-------------------|---------------|
| **Claude** (Sonnet 4.6 / Opus 4.6) | Orchestrator, primary executor, cross-review | Long-context reasoning, multi-file architecture, orchestration | — baseline |
| **Codex CLI** (o4-mini) | Cross-review hard gate, focused code changes | Independent second opinion; budget cost tier | Weaker at multi-file context; no orchestration |
| **Gemini** (2.5 Pro / Flash) | Research, large-doc processing, summarisation | 1M token context; strong synthesis | Weaker at code execution and test writing |

### Recommendation: Maintain Multi-Provider (Option A)

**Rationale:**
- Codex cross-review provides genuine independence from authoring context — a single-provider review
  misses the same blind spots as the author. The overhead is one CLI install + routing config.
- Gemini's 1M context window remains ahead of Claude's 200K for large document processing tasks.
  Gap may close by August 2026 — reassess at June review.
- Cost data (WRK-237) will validate or refute this by Q2 2026.

**Review trigger**: if Claude reaches 1M context and Codex output quality drops below Claude Sonnet in
cross-review verdicts (tracked via WRK-237), consolidate to Claude + selective Codex only.

**Skills canonical location**: `.claude/skills/` only. `.codex/skills` and `.gemini/skills` are symlinks.

---

## Top 5 Investment Themes (Ranked by Compound Value)

1. **Engineering module agent-callability** — `digitalmodel` has 114 pending WRK items, 76 archived.
   Archive shows 100 engineering WRKs completed: hydro(29), drilling(15), pipeline(9), safety(9), CP(8).
   Modules are built but not all wrapped as agent-callable skills. **Highest ROI per hour: wrapping
   existing code, not new features.** Promoted from #2 — harness infrastructure is done, shift to
   domain output.

2. **Data queryability** (`worldenergydata` + cross-repo) — 49 data WRKs archived: BSEE(14),
   ingestion(11), safety(7), production(6), fleet(6). Data exists but agents cannot query it
   autonomously. WRK-171, WRK-219, WRK-254, WRK-417 are the path. Production data modules
   (NCS, UKCS, ANP, EIA) all archived — now need unified query interface (WRK-260).

3. **Self-improving session loop** (WRK-234) — sessions → analysis → skills → better sessions.
   Demoted from #1: the harness infrastructure this depends on is now mature (155 harness WRKs
   archived). Focus should shift to activating the loop, not building more infrastructure.

4. **Client-facing content automation** (`aceengineer-website`, WRK-148, WRK-259, WRK-261, WRK-382) —
   agents should generate portfolio content and case studies from module outputs, not manual writing.
   Promoted from #5 — with engineering modules and data in place, content generation is unblocked.

5. **Agentic workflow infrastructure** — ✅ **COMPLETE for practical purposes.** 155 harness WRKs
   archived (38% of all work). Archive synthesis confirms: skills(41), work-queue(32), session(15),
   AI-orchestration(7), maintenance(11). WRK-1330 deleted 295K lines by replacing HTML with GitHub
   Issues. 381 WRKs migrated to GitHub Issues across 5 repos. Remaining items are incremental.
   **Repeat spawner warning:** harness WRKs generate follow-ons at the highest rate (WRK-234: 6,
   WRK-1035/1055: 6 each). **Target: cap harness at 20% of new work. Shift to 60% engineering.**

---

## Critical Path WRK Items (Top 20)

Items that directly advance the August 2026 vision. All others are secondary.

| WRK | Title | Theme | Repo |
|-----|-------|-------|------|
| WRK-234 | Self-improving agent ecosystem | Loop | workspace-hub |
| WRK-126 | Benchmark all example models — time + frequency domain | Eng modules | digitalmodel |
| WRK-149 | digitalmodel test coverage ≥80% | Eng modules | digitalmodel |
| WRK-376 | Casing/tubing triaxial stress design envelope | Eng modules | digitalmodel |
| WRK-378 | Full wellbore hydraulics module | Eng modules | digitalmodel |
| WRK-311 | QTF benchmarking case 3.1 — charts and validation | Eng modules | digitalmodel |
| WRK-380 | Multi-physics chain: Gmsh → OpenFOAM → OrcaFlex | Eng modules | workspace-hub |
| WRK-171 | Cost data calibration — sanctioned project benchmarking | Data | worldenergydata |
| WRK-219 | Batch drilling economics — campaign scheduling | Data | worldenergydata |
| WRK-254 | Heavy vessel GIS integration | Data | worldenergydata |
| WRK-417 | The Well — planetswe dataset integration | Data | worldenergydata |
| WRK-418 | The Well — acoustic_scattering datasets for NDE | Data | digitalmodel |
| WRK-419 | The Well — shear_flow dataset for hydrodynamics ML | Data | digitalmodel |
| WRK-148 | ACE-GTM: go-to-market strategy stream | Client-facing | aceengineer-website |
| WRK-259 | BSEE field economics case study | Client-facing | aceengineer-website |
| WRK-382 | Marketing follow-up — brochure + website from WRK-373/375 | Client-facing | digitalmodel |
| WRK-297 | SSHFS mounts — bidirectional file access dev-primary/2 | Infra | workspace-hub |
| WRK-309 | Document intelligence — index and plan all stored docs | Infra | workspace-hub |
| WRK-386 | Automated Gap-to-WRK Generator | Infra | workspace-hub |
| WRK-343 | OpenFOAM technical debt audit | Infra | workspace-hub |

**Deprioritise**: WRK-005 (email cleanup), WRK-008 (photo upload), WRK-167 (calendar appointment),
WRK-050 (hardware consolidation), WRK-370/371 (home repairs) — these do not advance the
August 2026 engineering-AI vision. Park explicitly.

---

## Archive Synthesis Findings (2026-03-19)

**Source:** `docs/archive-synthesis-report.yaml` — 410 archived WRKs fully categorized.

### Throughput & Capacity
- **Archived:** 410 WRKs | **Pending:** 363 | **Working:** 8 | **Blocked:** 10
- **Priority mix (pending):** 133 high, 149 medium, 48 low, 51 unset
- **Largest pending bucket:** engineering/pipeline (73 items) — biggest single backlog

### Investment Shift: 60/20/20 Target
Historical allocation was harness-heavy (38%). Infrastructure is now mature.

| Category | Archived (actual) | % of total | H1 target % |
|----------|:-:|:-:|:-:|
| Engineering | 100 | 24% | **60%** |
| Harness/infra | 155 | 38% | **20%** |
| Data + other | 155 | 38% | **20%** |

### Top 3 Engineering Bets
1. **Pipeline** — 9 archived + 73 pending. Largest growth opportunity. Priority: wrapping existing code as agent-callable skills, then clearing the backlog.
2. **Hydrodynamics** — 29 archived (most mature module). Focus: benchmark validation and agent-callability, not new features.
3. **Drilling** — 15 archived. Wellbore hydraulics (WRK-378) and dysfunction detector (WRK-379) are the critical path items.

Supporting modules: cathodic protection (8 archived + 4 pending), safety (9 archived).

### Harness Simplification Wins
- WRK-1330: replaced HTML generation with GitHub Issues, removing **295,437 lines**
- Backfilled 409 archived WRKs to knowledge base
- Migrated 381 active WRKs to GitHub Issues across 5 repos
- Issue distribution: workspace-hub (191), digitalmodel (153), worldenergydata (31), OGManufacturing (4), assethold (2)

### Repeat Spawner Warning
These items each generated 6 follow-ons — signals of over-complexity needing simplification:
- **WRK-1055, WRK-234** (skills system) — simplify, don't add features
- **WRK-1035** (work queue) — already addressed by WRK-1330 simplification
- **WRK-1178** (skills/reporting) — stabilize before extending

### Active GitHub Issues by Repo
| Repo | Open Issues | Primary category |
|------|:-:|---|
| workspace-hub | 197 | harness + misc |
| digitalmodel | 192 | engineering core |
| worldenergydata | 40 | data + energy |
| assethold | 7 | finance |
| OGManufacturing | 4 | drilling |

---

## Monthly Review Cadence
*First Friday of each month.*

1. Which critical-path repos advanced? Any blockers?
2. Provider utility: is Codex/Gemini cross-review output quality holding? (WRK-237 data)
3. Work queue velocity: net-shrinking (archived > created)?
4. New model releases since last review — any standing decisions affected?
5. Horizon skill output: any `park` items now `do now`? Any `do now` items now obsolete?
6. Update this document's `Last updated` date and Investment Themes if landscape has shifted.

*Last reviewed: 2026-03-19 (archive synthesis findings + 60/20/20 investment shift) — Next monthly review: 2026-04-03 (first Friday of April)*

---

## Done Definition (August 2026)

- An agent runs a complete fatigue or wall thickness assessment end-to-end with one invocation
- Session analysis runs nightly (3AM cron) without intervention; signals reach next session
- aceengineer-website content is generated by agents from live data and module outputs
- Work queue is net-shrinking: more items archived per month than created
- Provider strategy is validated by cost data from WRK-237, not assumption
- All 6 critical-path repos have test coverage ≥80%
- Self-improving loop (WRK-234) is live and producing skills without manual curation
