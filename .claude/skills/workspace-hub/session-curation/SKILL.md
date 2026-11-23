---
name: session-curation
description: "Operate and reason about the 'session analysis & memory curation' line\
  \ item of the machine-equality matrix — the per-box engine that analyzes every\
  \ AI-provider session log + curates the memory delta, its daily-freshness verdict\
  \ (green ≤12h / orange >12h / red >24h), the dead-man's-switch rebuild, and\
  \ the cross-machine fingerprint transfer. Use to read, refresh, or debug the cell."
type: workflow
version: 1.0.0
category: workspace-hub
last_updated: 2026-06-26
source: internal
tags:
- equality
- curation
- memory
- session-analysis
- multi-machine
- freshness
- dead-mans-switch
related_skills:
- ecosystem-equivalence-reconcile
- repo-ecosystem-hygiene
freedom: low
---

# Session analysis & memory curation

This is the **`session_curation`** dimension of the machine-equality matrix
(`docs/reports/machine-equality-matrix.html`, GROUP heading *"Session analysis &amp;
memory curation — daily freshness"*). Unlike the other matrix dimensions — which grade a
machine **against its peers** (DIVERGES / NO-MAJORITY) or **against a baseline**
(BELOW-BASELINE) — this cell grades a machine **against real wall-clock now**: it answers
*"did this box analyze its session activity and curate its memory recently enough?"*

Each box, every 6h, does two things and stamps the time it finished:

1. **Analyze** all AI-provider session logs present on THIS box —
   Claude (`~/.claude/projects`), Codex (`~/.codex/sessions`), Gemini (`~/.gemini/tmp`),
   Hermes (`~/.hermes/sessions`) — into per-provider activity counts. Bounded,
   mtime-first, never reads gigabytes (Hermes' ~27 GB tree is capped at
   `MAX_FILES_PER_PROVIDER`, never fully walked).
2. **Curate** the workspace memory delta — basenames of `.claude/memory/*.md` changed
   since the last run — into a portable digest, and **publish a fingerprint** to a
   dedicated git ref so sibling machines can pull it.

Counts / enums / timestamps only — **never** prompt text, tokens, absolute paths, or
client identifiers (matches the `collect-equality` allowlist and repo legal rules).

## Daily-freshness semantics

`freshness_verdict(report, now=None)` in `scripts/readiness/build-equality-matrix.py`
(line 198) grades the cell by the age of `last_curated_at`:

| Age of `last_curated_at` | Verdict | Colour | CSS class |
|---|---|---|---|
| ≤ 12h | `CURATED-FRESH` | green | `curated-fresh` |
| > 12h, ≤ 24h | `CURATED-STALE` | orange | `curated-stale` |
| > 24h | `CURATED-EXPIRED` | red | `curated-expired` |
| no / garbled / **future** stamp | `MISSING-EVIDENCE` | grey | — |

Only `CURATED-FRESH` is in `OK_VERDICTS`. The verdict **fails closed**: a missing,
unparseable, or future-dated timestamp (clock skew) is graded `MISSING-EVIDENCE`, never
"fresh". The 6h cron cadence keeps a healthy box comfortably under the 12h green
threshold (two refreshes per window).

## Why the matrix MUST rebuild daily — the dead-man's-switch

The freshness cell only ages if **something re-renders it**. The collector
(`collect-equality.sh`) only **references** the state file — it never re-runs the engine.
So if the `session-curation` cron silently dies, the *last* curation run left a green cell
in the *last* rendered matrix, and nothing would ever recolour it: a dead cron would look
healthy forever.

The `equality-matrix-refresh` cron (control-plane, daily `50 5 * * *`) closes that hole.
It rebuilds the matrix **independent of the curation cron**, re-grading every cell against
a fresh `now`. With it, a dead curation cron's cell visibly ages green → orange (>12h) →
red (>24h) on its own. Per `schedule-tasks.yaml`: *"so a DEAD curation cron still ages its
freshness cell past green … Without this daily rebuild the weekly equality-report (#2801)
would freeze the last-green render and the dead-man's-switch would never fire."*

## Pieces (all repo-root relative)

| File | Role |
|---|---|
| `scripts/curation/curate_session_memory.py` | engine — analyze providers + memory delta, write state + digest, publish fingerprint. PEP-723 (`uv run --script`). |
| `scripts/curation/curate-session-memory.sh` | fail-loud cron wrapper: curate → `collect-equality.sh` → `build-equality-matrix.py`; any hard failure fires `scripts/notify.sh` and exits non-zero. Cross-platform (Linux/macOS/Git-Bash). |
| `scripts/readiness/collect-equality.sh` (line 154) | emits the `session_curation:` YAML block by reading `.claude/state/session-curation-<machine>.json`; missing/garbled file → `last_curated_at: null` → MISSING-EVIDENCE. |
| `scripts/readiness/build-equality-matrix.py` | `freshness_verdict`, the `session_curation` dimension, GROUP, CSS, `ROLLUP_SEVERITY`, `OK_VERDICTS`, `remediate`. |
| `.claude/state/session-curation-<machine>.json` | per-box state (`schema_version: 1`) — `last_curated_at`, per-provider counts, `sessions_24h`, `providers_active`, `memory_files_changed`, `digest_ref`. |
| `.claude/state/session-curation-digest-<machine>.md` | human-readable transferable digest. |

### Cron (`config/scheduled-tasks/schedule-tasks.yaml`)

- **`session-curation`** — `47 */6 * * *`, every box. Runs the wrapper; refreshes this
  box's equality column each cycle.
- **`equality-matrix-refresh`** — `50 5 * * *`, control-plane only. The daily
  dead-man's-switch rebuild described above.

## Cross-machine transfer

The engine publishes this box's fingerprint to the dedicated git ref
**`session-curation-state`** via `scripts/monitoring/equivalence_state.py` (the same
CAS-backed equivalence-state store the harness uses). Sibling machines pull every box's
fingerprint and render a merged fleet view (`session-curation-fleet.md`) with `--collect`.
The transfer carries the same leak-safe payload as the state file — counts, active-provider
enum, last-curated stamp, memory-delta count — nothing else.

## Operator commands

```bash
# Inspect this box's state WITHOUT writing or publishing (dry run)
uv run --script scripts/curation/curate_session_memory.py --stdout

# Curate this box now + publish the fingerprint (what the cron runs)
uv run --script scripts/curation/curate_session_memory.py
# …or the full wrapper (curate → collect → rebuild matrix, fail-loud):
bash scripts/curation/curate-session-memory.sh

# Curate locally but skip the git-ref publish
uv run --script scripts/curation/curate_session_memory.py --no-publish

# Fleet view — merge every box's fingerprint from the session-curation-state ref
uv run --script scripts/curation/curate_session_memory.py --collect

# Re-render the matrix to re-grade freshness against a fresh `now`
bash scripts/readiness/collect-equality.sh
uv run --no-project --with pyyaml python scripts/readiness/build-equality-matrix.py
```

(`uv` unavailable? the wrapper falls back to `python3`; the engine's only dependency is
pyyaml via the PEP-723 header.)

## Remediating a non-green cell

`remediate()` (`build-equality-matrix.py` line 446) maps the verdicts:

| Verdict | Cause | Fix |
|---|---|---|
| `CURATED-STALE` / `CURATED-EXPIRED` | curation is stale (>12h / >24h) | run `bash scripts/curation/curate-session-memory.sh` (Windows: `curate-session-memory.ps1`), or repair the every-6h `session-curation` cron on this box |
| `MISSING-EVIDENCE` | no / garbled / future-dated state file | run the engine here so the state file lands with a current `last_curated_at`; check clock skew if the stamp is future-dated |

A cell that stays orange/red after a successful manual curation means the **render** isn't
refreshing — check the `equality-matrix-refresh` cron, not the engine.

## Related

- `ecosystem-equivalence-reconcile` — drives THIS box back to full matrix equivalence;
  its verdict→action playbook is the parent of this cell's remediation.
- `repo-ecosystem-hygiene` — read-only detector for the repo-hygiene surface the reconcile
  skill complements.
