# #3097 — Generated-artifact client-PII remediation (counts only)

Part of epic [#3095](https://github.com/vamseeachanta/workspace-hub/issues/3095). **Counts only — no client identifiers** (the named inventory + codename map live in the private `aceengineer-strategy` repo, per the deny-list paradox).

## Scope

- **Surface:** generated artifacts only. Hand-authored docs are handed off to [#3098](https://github.com/vamseeachanta/workspace-hub/issues/3098).
- **Identifiers:** the full client/project set from the canonical registry `config/client-wikis.yml` (9 clients + 2 projects). The earlier 3-identifier scoping was incomplete — corrected after verifying against the registry.
- **Treatment:** per-client neutral **codenames** (map is private); `/mnt/ace/<client>/` bucket paths renamed too. Regenerable dumps / giant generated inventories are **stop-committed** (removed from public tracking, preserved privately).
- **Out of scope:** git-history scrub (HEAD-only, accepted).

## What changed

| Action | Files | Notes |
|---|---:|---|
| **Stop-committed** (removed from public tracking, preserved private) | **2609** | regenerable dumps + giant generated inventories |
| — `scripts/review/results/` | 2083 | provider review-output dumps |
| — `.agents/skills/session-logs/` | 243 | raw session-logger dumps |
| — `logs/orchestrator/` (hermes + codex session logs) | 206 | raw command/tool exports |
| — `.planning/intel/elements-*` data (`.jsonl/.tsv/.json/.csv`) | 77 | full client-document inventories (42 MB+) |
| **Codename-redacted in place** | **~316** | curated generated state |
| — `.claude/state/` (patterns, corrections, trends, …) | 106 | learning state |
| — `config/agents/*/…snapshots` | 68 | memory/state snapshots |
| — `.planning/intel/` (narrative, non-data) | 38 | reports/plans kept, identifiers codenamed |
| — `.claude/memory/`, `docs/reports/kanban/` | 35 / 34 | mirrored memory + kanban |
| — `analysis/cross-agent-audit-*`, `data/document-index/` | 19 / 16 | generated audits + manifests |
| **New tooling** | 2 | `scripts/legal/redact-client-pii.py` (name-agnostic engine) + tests |

Total replacements applied across tracked generated files (codename + bucket rename): several thousand (plus ~79k in a 655 MB **gitignored, untracked** local index that never enters the repo).

## Verification

- **Generated-scope residual real client identifiers: 0** (verified against staged blobs).
- Only tracked `.gz` archive in scope decompressed clean (no compressed leak).
- All originally-valid JSON/YAML still parse (3 pre-existing-invalid reflect-history JSON were invalid before redaction too).

## Recurrence prevention (fix-forward)

- Dumps/orchestrator logs: `.gitignore` stop-commit → cannot re-enter the public repo.
- Learning cron (`scripts/cron/commit-learning-artifacts.sh`): added a codename-redaction step that reads a **private local map** (`config/agents/.client-codename-map.local.yaml`, gitignored; provision per host from the private archive). Warns + skips if absent.
- Hard backstop = [#3099](https://github.com/vamseeachanta/workspace-hub/issues/3099) CI/pre-commit legal guard (must read the full client list, not the incomplete deny-list that let this through).

## Handoff to #3098 (hand-authored)

**538** tracked files still carry client identifiers — all hand-authored (`docs/plans` 101, `.claude/skills` 42, `docs/modules` 32, `docs/session-handoffs` 28, …). **Critically includes `config/client-wikis.yml`** — the client registry itself is a public file listing every client name + `/mnt/ace/<client>/` bucket; relocating/codenaming it has architectural ripple (rules + `check-wiki-sibling-frontmatter.py`) and must be coordinated in #3098.
