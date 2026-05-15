# Business Brain — Ecosystem Shared Context

> Single-file ecosystem awareness for all AI agents.
> Load this before any work session. Keep under 200 lines.
> Source: #1425 (video-review/simon-scrapes-4-patterns, Pattern 2)

---

## Owner

Vamsee Achanta — solo engineering practitioner. All repos are single-owner.
No team members. AI agents are the workforce.

## Repositories (24 active, GitHub: vamseeachanta)

> Canonical per-repo mission/objective + routing rules → [`docs/REPO_MISSION_PORTFOLIO.md`](REPO_MISSION_PORTFOLIO.md) (source-of-truth at `data/document-index/repo-portfolio-inventory.yaml`).

### Tier-1 (actively developed, cross-repo dependencies)
| Repo | Domain | Language | Visibility |
|------|--------|----------|------------|
| workspace-hub | Engineering workspace, GSD framework, AI harness | Python | public |
| digitalmodel | Numerical models, calculation pipelines | Python | public |
| assetutilities | Shared engineering utilities | Python | public |
| aceengineer-website | Company website | HTML | public |

### Tier-2 (domain-specific, periodic work)
| Repo | Domain |
|------|--------|
| OGManufacturing | Manufacturing/domain project context; reusable code routes to `digitalmodel` |
| acma-projects | ACMA naval-architecture client project data/delivery |
| frontierdeepwater | Startup project data; AceEngineer has 5% stake |
| worldenergydata | Energy data analysis |
| sabithaandkrishnaestates | Corporate/investment admin: finance tracking, taxes, entity records |

### Tier-3 (low-frequency, reference, client archive, or retirement candidates)
aceengineer-admin, aceengineer-strategy, achantas-data, achantas-media,
assethold, client_projects, doris, hobbies, pdf-large-reader,
saipem, sd-work, teamresumes

### Archive / extraction candidates
| Repo | Disposition |
|------|-------------|
| investments | Private triage; migrate analysis/code to `assethold`, private records to `achantasdata`; retire within 3 months after no-loss migration |
| rock-oil-field | Sanity-check and migrate useful code/data/analysis to Tier-1 repos; archive/retire if possible |
| seanation | Client repo; extract useful data/information and archive |
| saipem | Engineering installation contractor repo; extract useful info and archive/retire over time |

## Machines (workstation inventory)

Hermes on `ace-linux-1` is the primary control plane for dispatching work to all machines. Full inventory — installed programs, licenses, AI-provider auth state, repo checkout locations, run/smoke commands, and dispatch readiness per machine — lives in [`docs/ops/machine-inventory.md`](ops/machine-inventory.md). Canonical capability/ssh/workspace data: `config/workstations/registry.yaml`.

## AI Provider Accounts

Spend assumptions must reflect real subscriptions and live usage headroom, not stale template inventory. AI credits are **not** the current bottleneck; harness throughput is.

| Provider | Plan | Cost/mo | Role |
|----------|------|---------|------|
| Claude (Anthropic) | Claude Max | $200 max | Primary planning/orchestration subscription; long-context synthesis, adversarial review, workflow control |
| Gemini (Google) | Google AI Pro | $20 | Research/recon, broad-context review, risk enumeration |
| Codex / OpenAI | Confirm active account before allocating load | Variable by authenticated account | Implementation, tests, fixes, cleanup when available; do not assume extra paid seats without machine/auth evidence |

**Provider auth policy:** Hermes is the primary driver. All AI providers should be authenticated on all worker machines where practical, but `ace-linux-1` remains the control plane for dispatch, GitHub mutation, and reconciliation.
**Current spend rule:** treat Claude Max ($200) and Gemini ($20) as the baseline confirmed subscriptions for planning; verify Codex/OpenAI account availability from live machine/auth evidence before promising parallel lanes. As of the latest user-provided quota screenshot, Claude Max still has substantial weekly headroom (All models 38% used, Sonnet only 7% used; current session 3% used) and Codex shows large remaining weekly capacity (89% overall remaining; GPT-5.3-Codex-Spark 100% remaining). Therefore plan preparation and executing approved work are primary; do not let weekly limits reset unused. The owner can tolerate up to ~2 days of depleted credits at the end of a reset window if that burn produced durable plans, reviews, tests, code, and GTM artifacts.

## Workflow Framework: GSD (Get Shit Done)

GSD is the control plane. Do not replace it. Do not build parallel frameworks.

## Autonomous Hard-Gate Evolution

The current hard gates remain authoritative until replaced by measured evidence, but they must not become a permanent throughput ceiling. As AI-agent rigor, repeatability, and cross-review quality mature, the operating model should evolve from user-managed gates toward confidence-threshold gates.

Target direction:
- The owner should focus primarily on **idea origination, GTM throughput, customer/prospect artifacts, and strategic approvals**.
- AI agents should self-cycle the rest: issue decomposition, plan drafting, adversarial review, legal/provenance checks, test design, implementation, verification, closeout evidence, and queue feeding.
- Do **not** remove hard gates by assertion. Establish threshold metrics over time, then relax specific user approvals only when evidence shows the automated loop is consistently safe.

Candidate threshold metrics for future self-cycling:
- repeated APPROVE/MINOR adversarial-review outcomes across Claude/Codex/Gemini with no unresolved MAJOR findings,
- legal sanity scans passing for public-facing data/wiki/artifact promotion,
- TDD evidence present before implementation and tests passing after implementation,
- plan/implementation/closeout artifacts matching issue acceptance criteria,
- low rework rate after user review,
- no unauthorized GitHub label/status mutations,
- no secrets/client-identifying content leakage,
- reproducible logs/artifacts sufficient for later audit.

Until these metrics are formalized and proven, keep the explicit Issue → Plan → Review → User Approval → Plan-Approved → TDD Implementation → Review → Close gate. The long-term Business Brain goal is to make that gate increasingly evidence-driven so user time is spent on GTM and new ideas, not routine orchestration.

- Tasks tracked as **GitHub issues** with `[WRK]` prefix
- Issue template: `.github/ISSUE_TEMPLATE/wrk-item.yml`
- Skills directory: `.claude/skills/` (568 active, 2734 total)
- Commands: `/gsd:help`, `/gsd:new-project`, `/gsd:do`, etc.

## Interactive Weekly GTM Targets

Weekly targets should be established interactively with the owner, then decomposed into agent-executable issue/plan/review/execution packets. The weekly target should be concrete enough to produce GTM artifacts, not just internal engineering progress.

Current/next weekly target seed: **for the week of April 1, produce vessel capability charts and send a good brochure to all researched vessel contractors**. Required agent support includes contractor research, vessel-contractor list hygiene, capability chart generation, brochure/collateral preparation, evidence-backed claims, and outbound/send tracking.

This week should also include a review of the owner's full work pattern to identify productivity hacks that make work flow faster. Agents should audit recent sessions, GitHub throughput, GTM artifacts, context handoffs, repeated friction points, and tool/provider bottlenecks, then propose practical changes that reduce owner time spent on orchestration and increase GTM/artifact throughput.

## GTM-to-Code Readiness Loop

1. **GTM signal intake:** Keep GTM messages, prospect needs, weekly targets, market signals, and repo evidence in view. Convert each useful signal into one of: update an existing GitHub issue, reopen an existing issue, or open a new bounded issue.
2. **Knowledge promotion:** Promote raw data and public data sources into `llm-wiki` / knowledge artifacts only through explicit source, provenance, license, and legal sanity gates. Raw inputs may provide data, codes/standards references, methodology notes, and reusable context, but public-facing artifacts must be sanitized and evidence-bounded.
3. **Engineering hardening:** Convert knowledge into code-readiness by strengthening methodology, tests, fixtures, acceptance criteria, and implementation plans before execution.
4. **Execution throughput:** Once a plan is approved, dispatch bounded implementation/test work aggressively to available providers/machines. The harness should feed work continuously rather than let weekly AI usage reset unused.
5. **Evidence boundary:** No public/client-facing GTM claim should exceed repo evidence, validation output, or an explicit engineering caveat.

## Legal Sanity Gates for Public Artifacts

Legal/IP sanity checks are mandatory before raw data, client-derived context, standards extracts, document intelligence, or code-porting insights become public-facing `llm-wiki` pages, GTM artifacts, GitHub issues, PRs, or demo reports. Use `scripts/legal/legal-sanity-scan.sh --diff-only` for changed files, repo/full scans where relevant, and block promotion until violations are redacted/sanitized and the scan passes.

Minimum public-promotion sanity gate:
- source provenance recorded,
- public-vs-private inputs identified,
- methodology and standards citations attached,
- tests/review state known,
- legal scan/review run when applicable,
- no confidential/client-identifying content promoted.

## Portfolio Refresh Obligation

Because substantial work is happening across repos, periodically assess completed repo work and update this Brain accordingly. At minimum reconcile: repo missions/objectives, archive/retirement candidates, Tier-1 routing, machine/software inventory, provider accounts/auth, and evidence from recent GitHub issues/PRs. Do not let stale repo classifications or provider/machine assumptions remain authoritative.


## Review Routing (settled policy)

```
Claude plans → Codex reviews (default two-provider)
Claude plans → Codex + Gemini review (triggered three-provider)
```

Triggers for Gemini: architecture-heavy, research-heavy, ambiguous requirements,
high-stakes delivery, or context saturation.

Full policy: `docs/standards/AI_REVIEW_ROUTING_POLICY.md`

## Hard Rules (non-negotiable)

1. **Plan before acting** — explicit plan + approval before implementation
2. **TDD mandatory** — tests before implementation, no exceptions
3. **`uv run` always** — never bare `python3` or `pip`
4. **Commit to `main`** — branch only for multi-session work
5. **No hardcoded secrets** — environment variables only
6. **Review verdicts:** APPROVE | MINOR | MAJOR — resolve MAJOR before completion
7. **Harness throughput primary** — provider credits are not the bottleneck; keep plan preparation, review, approved execution, and reconciliation lanes fed so weekly usage does not reset unused

## Key Standards Documents

| Document | Path |
|----------|------|
| AGENTS.md (root contract) | `AGENTS.md` |
| AI Review Routing | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` |
| Control Plane Contract | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| File Structure Taxonomy | `docs/standards/FILE_STRUCTURE_TAXONOMY.md` |
| Data Placement | `docs/standards/DATA_PLACEMENT.md` |
| Harness Architecture | `docs/modules/ai/MINIMAL_HARNESS_ARCHITECTURE_2026-03.md` |
| Harness Operating Model | `docs/modules/ai/MINIMAL_HARNESS_OPERATING_MODEL_2026-03.md` |

## Domain Knowledge

The owner is a **subsea/offshore engineer** working in oil & gas, renewable energy,
and maritime engineering. Key technical domains:

- Hydrodynamics (OrcaFlex, OrcaWave, AQWA, Capytaine)
- Structural analysis (DNV, NORSOK, ISO, ASTM standards)
- Finite element analysis
- Mooring and riser design
- Floating wind energy systems (WEIS)
- Pipeline engineering

## Legacy Surfaces (do not extend)

| Path | Status |
|------|--------|
| `.hive-mind/` | Legacy — do not extend |
| `.swarm/` | Legacy — do not extend |
| `AI_ECOSYSTEM.md` | Outdated (Sep 2025) — superseded by Minimal Harness docs |

## Session Signals

Session telemetry at `.claude/state/session-signals/` (389 files, 208K+ records).
Schema includes `correction_events` but capture is **not yet wired** (#1426).

---

*This file is the ecosystem's single source of truth for agent onboarding.
Update it when machines, repos, providers, or policies change.*
