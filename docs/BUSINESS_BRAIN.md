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
| OGManufacturing | Oil & gas manufacturing |
| acma-projects | ACMA engineering projects |
| frontierdeepwater | Deepwater engineering |
| seanation | Maritime/naval architecture |
| worldenergydata | Energy data analysis |
| investments | Investment analysis |
| rock-oil-field | Oil field engineering |

### Tier-3 (low-frequency, reference, or archival)
aceengineer-admin, aceengineer-strategy, achantas-data, achantas-media,
assethold, client_projects, doris, hobbies, pdf-large-reader,
sabithaandkrishnaestates, saipem, sd-work, teamresumes

## Machines (workstation inventory)

| Machine | Role | OS | Primary Use |
|---------|------|----|-------------|
| ace-linux-1 | Primary dev | Linux | Daily AI work, Claude/Codex sessions |
| ace-linux-2 | Secondary dev | Linux | Parallel AI work, overflow |
| licensed-win-1 | Licensed software | Windows | OrcaFlex, licensed engineering tools |
| licensed-win-2 | Licensed software | Windows | OrcaFlex, licensed engineering tools |
| macbook-portable | Portable dev | macOS | Travel, mobile sessions |
| home-win | Home workstation | Windows | Off-hours work |
| acma-ws014 | Office workstation | Windows | On-site ACMA work |
| multi | — | — | Issues spanning all machines |

## AI Provider Accounts

| Provider | Plan | Cost/mo | Role |
|----------|------|---------|------|
| Claude (Anthropic) | Max | $200 | **Default orchestrator** — deepest context, richest surface |
| Codex (OpenAI) #1 | Plus | $20 | Coding worker, adversarial reviewer |
| Codex (OpenAI) #2 | Plus | $20 | Parallel coding, overflow |
| Gemini (Google) | AI Pro | $20 | Narrow third-lane: large-context research, architecture review |

**Volume hierarchy:** Claude >> Codex > Gemini

## Workflow Framework: GSD (Get Shit Done)

GSD is the control plane. Do not replace it. Do not build parallel frameworks.

- Tasks tracked as **GitHub issues** with `[WRK]` prefix
- Issue template: `.github/ISSUE_TEMPLATE/wrk-item.yml`
- Skills directory: `.claude/skills/` (568 active, 2734 total)
- Commands: `/gsd:help`, `/gsd:new-project`, `/gsd:do`, etc.

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

- Hydrodynamics (OrcaFlex, OrcaWave, Capytaine)
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
