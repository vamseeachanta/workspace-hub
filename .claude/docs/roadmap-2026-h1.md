# Repo Ecosystem Roadmap — 2026 H1
*WRK-235 | Established: 2026-02-20 | Last updated: 2026-03-09 | Cadence: monthly review (first Friday)*

## Ecosystem Vision — August 2026

An agent can run a complete engineering analysis (fatigue, FFS, wall thickness, drilling economics)
end-to-end with a single invocation. Session analysis runs nightly without intervention. Client-facing
content on aceengineer-website is generated from live data and module outputs. The work queue is
net-shrinking. Provider strategy is validated by cost data.

---

## Repo Assessment
*Pending WRK = items with `status: pending` targeting repo. Archived WRK = completed items.*
*Strategic value 1–5, Agentic readiness 1–5 (1=low, 5=high). Investment: high/medium/low/defer.*
*Updated: 2026-03-09*

| Repo | Strategic Value | Agentic Readiness | Pending WRK | Archived WRK | Priority | August 2026 Target |
|------|:-:|:-:|:-:|:-:|----------|---------------------|
| `workspace-hub` | 5 | **5** | 73 | 121 | **high** | Autonomous session lifecycle; self-improving loop live |
| `digitalmodel` | 5 | 3 | 99 | 103 | **high** | All major modules agent-callable; test coverage ≥80% |
| `worldenergydata` | 5 | 3 | 30 | 94 | **high** | All sources queryable by agents; refresh scheduled |
| `assethold` | 4 | **4** | 5 | 14 | **high** | Agents run daily strategy autonomously |
| `assetutilities` | 4 | **4** | 11 | 34 | **high** | Shared utilities stable; used by assethold and agents |
| `aceengineer-website` | 5 | 2 | 6 | 15 | **high** | Agents generate + publish content from module outputs |
| `aceengineer-admin` | 3 | 2 | 2 | 5 | medium | Admin workflows documented; agent-executable |
| `achantas-data` | 3 | 2 | 4 | 6 | medium | Data indexed; queryable by agents |
| `doris` | 3 | 3 | 22 | 0 | medium | Pipeline structure clean; agent-callable for data pull |
| `saipem` | 3 | 3 | 1 | 5 | medium | Installation modules stable; benchmarked |
| `acma-projects` | 3 | 2 | 4 | 8 | medium | Structural modules integrated with digitalmodel |
| `frontierdeepwater` | 2 | 2 | 8 | 6 | low | Vessel data extracted; minimal ongoing investment |
| `OGManufacturing` | 2 | 2 | 11 | 3 | low | Stable; no new investment unless client need arises |
| `rock-oil-field` | 2 | 2 | 3 | 1 | low | OrcaFlex models catalogued (WRK-121); then park |
| `pdf-large-reader` | 2 | 3 | 1 | 1 | low | Utility tool; maintain, no expansion |
| `pyproject-starter` | 2 | 4 | 0 | 0 | low | Template stable; update when ecosystem changes |
| `sd-work` | 1 | 2 | 0 | 0 | defer | No pending items; check quarterly |
| `seanation` | 1 | 1 | 0 | 0 | defer | No active engineering use; park |
| `teamresumes` | 1 | 2 | 0 | 0 | defer | Manual process; agent automation low ROI |
| `hobbies` | 1 | 1 | 0 | 0 | defer | Personal; no compound value |
| `sabithaandkrishnaestates` | 1 | 2 | 0 | 0 | defer | No pending items; reactive only |

**Agentic readiness note (March 2026):** `workspace-hub` upgraded 4→5: pre-push CI gate, coverage
ratchet, secrets scan, cross-repo symbol index, MkDocs pipeline, PEP 561 types, static analysis
harness, onboarding maps all landed (WRK-1062–1085). `assethold`/`assetutilities` upgraded 3→4:
deterministic fixtures, PEP 561 types, bandit baseline, ruff/mypy hooks in place.

**Critical path repos**: `workspace-hub`, `digitalmodel`, `worldenergydata`, `assethold`, `assetutilities`,
`aceengineer-website` — these 6 receive all high-priority investment.

---

## AI Provider Strategy

### Current State (March 2026)
*Tool versions: Claude 2.1.72, Codex CLI 0.112.0, Gemini 0.32.1 (ace-linux-1, verified 2026-03-09)*

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

1. **Self-improving session loop** (WRK-234) — sessions → analysis → skills → better sessions.
   Everything else compounds off this. Status: pending. Block nothing for this.

2. **Engineering module agent-callability** — `digitalmodel` has 99 pending WRK items, 103 archived.
   Fatigue, FFS, wall thickness, OrcaFlex reporting are built but not wrapped as agent-callable skills.
   Highest ROI per hour: wrapping existing code, not new features.

3. **Data queryability** (`worldenergydata`) — BSEE, EIA, drilling cost, GIS data exists.
   Agents cannot query it autonomously. WRK-171, WRK-219, WRK-254, WRK-417 are the path.

4. **Agentic workflow infrastructure** — ✅ substantial progress in Q1 2026: pre-push CI gate,
   coverage ratchet, secrets scan, cross-repo symbol index, MkDocs API docs, static analysis harness
   (WRK-1062–1085). Remaining: plan-mode integration (WRK-1083), skills.sh adoption (WRK-1084).

5. **Client-facing content automation** (`aceengineer-website`, WRK-148, WRK-259, WRK-261, WRK-382) —
   agents should generate portfolio content and case studies from module outputs, not manual writing.

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
| WRK-297 | SSHFS mounts — bidirectional file access ace-linux-1/2 | Infra | workspace-hub |
| WRK-309 | Document intelligence — index and plan all stored docs | Infra | workspace-hub |
| WRK-386 | Automated Gap-to-WRK Generator | Infra | workspace-hub |
| WRK-343 | OpenFOAM technical debt audit | Infra | workspace-hub |

**Deprioritise**: WRK-005 (email cleanup), WRK-008 (photo upload), WRK-167 (calendar appointment),
WRK-050 (hardware consolidation), WRK-370/371 (home repairs) — these do not advance the
August 2026 engineering-AI vision. Park explicitly.

---

## Monthly Review Cadence
*First Friday of each month.*

1. Which critical-path repos advanced? Any blockers?
2. Provider utility: is Codex/Gemini cross-review output quality holding? (WRK-237 data)
3. Work queue velocity: net-shrinking (archived > created)?
4. New model releases since last review — any standing decisions affected?
5. Horizon skill output: any `park` items now `do now`? Any `do now` items now obsolete?
6. Update this document's `Last updated` date and Investment Themes if landscape has shifted.

*Last reviewed: 2026-03-09 — Next review: 2026-04-03 (first Friday of April)*

---

## Done Definition (August 2026)

- An agent runs a complete fatigue or wall thickness assessment end-to-end with one invocation
- Session analysis runs nightly (3AM cron) without intervention; signals reach next session
- aceengineer-website content is generated by agents from live data and module outputs
- Work queue is net-shrinking: more items archived per month than created
- Provider strategy is validated by cost data from WRK-237, not assumption
- All 6 critical-path repos have test coverage ≥80%
- Self-improving loop (WRK-234) is live and producing skills without manual curation
