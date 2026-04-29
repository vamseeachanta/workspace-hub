# Business Brain — Ecosystem Shared Context

> Single-file ecosystem awareness for all AI agents.
> Load this before any work session. Keep under 200 lines.
> Source: #1425 (video-review/simon-scrapes-4-patterns, Pattern 2)

---

## Owner

Vamsee Achanta — solo engineering practitioner. All repos are single-owner.
No team members. AI agents are the workforce.

## Repositories (24 active, GitHub: vamseeachanta)

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

Hermes on `ace-linux-1` is the primary control plane for dispatching work to all machines. Maintain an inventory of installed programs, licenses, AI-provider auth, repo readiness, and dispatch capability so work can flow continuously from `ace-linux-1` to worker machines.

| Machine | Role | OS | Primary Use |
|---------|------|----|-------------|
| ace-linux-1 | Primary control plane | Linux | Hermes driver, GitHub mutation, provider routing, dispatch ledgers |
| ace-linux-2 | Overflow worker | Linux | Parallel AI execution after repo/tool/auth readiness checks |
| licensed-win-1 | Licensed engineering worker | Windows | OrcaFlex and AQWA runs to start; dispatched from `ace-linux-1` |
| licensed-win-2 | Licensed engineering worker | Windows | Future/overflow licensed engineering tools |
| macbook-portable | Portable dev | macOS | Travel, mobile sessions |
| home-win | Home workstation | Windows | Off-hours work |
| acma-ws014 | Office workstation | Windows | On-site ACMA work |
| multi | — | — | Issues spanning all machines |

Machine inventory must answer: installed programs, license availability, AI-provider auth state, repo checkout locations, run/smoke-test commands, and what work may be dispatched safely.

## AI Provider Accounts

Only one paid Codex account is currently active.

| Provider | Plan | Cost/mo | Role |
|----------|------|---------|------|
| Codex (OpenAI) | $200 account | $200 | Primary paid coding/execution worker; preserve for implementation, tests, fixes, cleanup |
| Claude (Anthropic) | As available/authenticated | TBD | Planning, orchestration, adversarial review, long-context synthesis |
| Gemini (Google) | As available/authenticated | TBD | Research/recon, large-context review, risk enumeration |

**Provider auth policy:** Hermes is the primary driver. All AI providers should be authenticated on all worker machines where practical, but `ace-linux-1` remains the control plane for dispatch, GitHub mutation, and reconciliation.
**Current volume hierarchy:** Hermes-led orchestration; Codex is the only confirmed paid $200 provider account.

## Workflow Framework: GSD (Get Shit Done)

GSD is the control plane. Do not replace it. Do not build parallel frameworks.

- Tasks tracked as **GitHub issues** with `[WRK]` prefix
- Issue template: `.github/ISSUE_TEMPLATE/wrk-item.yml`
- Skills directory: `.claude/skills/` (568 active, 2734 total)
- Commands: `/gsd:help`, `/gsd:new-project`, `/gsd:do`, etc.

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
