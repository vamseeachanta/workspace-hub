---
date: 2026-05-12
session: /mnt/local-analysis/ post-codex-burn cleanup + skill creation
status: COMPLETE — ~4 GB recovered, archive captured, skill shipped, handoff committed
session_kind: directive-driven cleanup → Hermes coordination check → tiered execution → skill capture
---

# `/mnt/local-analysis/` cleanup + routinization skill — 2026-05-12

## TL;DR

User goal (`/goal`): "clean up /mnt/local-analysis without losing any useful code/work; start by reviewing what are the other folders are alongside workspace-hub and come up with user actions for approval; This is becoming a routine and we should have a skill for this work".

Third cleanup pass in ~10 days. Differentiator: user push-back forced a Hermes-coordination check before any deletes, which revealed the `codex-burn-20260511/` dir was post-run vestigial (Hermes creates a fresh dated dir per run, doesn't poll old ones). Iron-Law verification step caught 1.1 MB of non-derived unique content in `worldenergydata-bundle` that would have been lost in an unverified delete. Final: ~4 GB recovered, 3.3 MB archive captured to `docs/sessions/archives/`, reusable skill shipped at `.claude/skills/operations/mnt-analysis-cleanup/`.

## Pre-state survey

```
/mnt/local-analysis/
├── workspace-hub/          ← canonical (25+ nested repos)
├── codex-burn-20260511/    ← 1.8+ GB Hermes post-run residue
│   ├── assetutilities-bundle/      ← orphan worktree, parent .git gone
│   ├── worldenergydata-bundle/     ← orphan worktree, parent .git gone
│   ├── monitoring-evidence/        ← 8.6 MB / 132 audit-evidence files
│   ├── logs/                       ← 6.8 MB launch/relaunch logs
│   └── prompts/                    ← 12 KB codex-burn prompts (3 repos)
├── agent-logs/             ← 894 KB session handoffs + provider-capacity logs
├── .pnpm-store/            ← empty package cache (system)
└── .Trash-1000/            ← XDG trash (system)
```

Disk usage at start: 188 GB used on `/dev/sdc1`.

## The Hermes detour (the most important step)

When the agent first proposed deleting `codex-burn-20260511/`, the user asked: "can you review in light of how hermes agent works and see if it is still useless? feel free to communicate with hermes agent directly via CLI".

The investigation revealed:

| Evidence | Source | Verdict |
|---|---|---|
| Hermes has an active skill `agent-cli-delegation-operations/references/codex-background-burn-orchestration.md` | `~/.hermes/skills/...` | Skill produces `codex-burn-YYYYMMDD/` dirs |
| Skill's operating pattern uses `/mnt/local-analysis/codex-burn-YYYYMMDD/issue-NNNN` as lane root | Lines 38-46 of the skill | The dated dir is the convention |
| Skill creates fresh dated dir per run | Pattern is per-day per-run | Old dirs are post-run vestigial |
| 20+ Hermes goal files from 2026-05-11 all carry same directive ("burn codex usage credit in 12 hours") | `~/.hermes/goals/*.json` | Single past session, not in-flight |
| `hermes cron list` shows no scheduled job depending on dated dir | `hermes cron list` output | No automated reference |
| `hermes status` confirmed Hermes is running but on different work | Current process state | No active claim on the dir |

Conclusion: the dir was genuinely vestigial. The user's push-back is now codified as **Step 3 ("Per-class verification: codex-burn run artifact")** in the new skill.

## Iron-Law verification (saved 1.1 MB)

For each orphan-worktree bundle, fetched matching `origin/codex/burn-20260511-<repo>-bundle` branch into canonical nested clone, archived branch tip, diffed against bundle dir with derived-artifact filter.

| Bundle | Unique non-derived content | Action |
|---|---|---|
| `assetutilities-bundle/` | None (only .benchmarks, egg-info, test logs/results/Plot — all derived) | Delete |
| `worldenergydata-bundle/` | `marine_safety.db` (84K SQLite), `results/` (16K), `test_output/` (988K) | **Archive** all 3, then delete |

Without the Iron Law: 1.1 MB of unique content silently lost. With it: archived to the cleanup tarball at trivial cost.

## Actions executed

| Step | Operation | Result |
|---|---|---|
| 1 | `git fetch origin codex/burn-20260511-{assetutilities,worldenergydata}-bundle` into inner clones | Branches fetched for diff verification |
| 2 | `git archive` branch tip → `diff -rq` vs bundle dir | Confirmed only derived artifacts unique to assetutilities; identified 1.1 MB unique non-derived in worldenergydata |
| 3 | `tar czf workspace-hub/docs/sessions/archives/2026-05-11-codex-burn-artifacts.tar.gz ...` | 3.3 MB archive, 149 entries (monitoring-evidence + logs + prompts + worldenergydata test artifacts) |
| 4 | `rm -rf /mnt/local-analysis/codex-burn-20260511` | ~4 GB freed (188 GB → 184 GB) |
| 5 | `find /mnt/local-analysis/agent-logs -mtime +14 -delete` | No-op (nothing >14 days) |
| 6 | Created `workspace-hub/.claude/skills/operations/mnt-analysis-cleanup/SKILL.md` + `references/case-study-2026-05-12.md` | Skill ready for future use |

## Post-state

```
/mnt/local-analysis/
├── workspace-hub/    ← canonical (unchanged)
├── agent-logs/       ← 894 KB (14-day threshold preserved everything)
├── .pnpm-store/      ← (system, untouched)
└── .Trash-1000/      ← (system, untouched)
```

Disk: **188 GB → 184 GB used** (~4 GB recovered net of archive).

## Skill delivered

**Location**: `workspace-hub/.claude/skills/operations/mnt-analysis-cleanup/`

**Structure**:
- `SKILL.md` — 7-step routine (Survey → Classify → Verify → Risk-tier → Ask → Execute → Handoff), Iron-Law verification step, Hermes coordination notes, disk-pressure trigger
- `references/case-study-2026-05-12.md` — worked example showing the Iron Law catching 1.1 MB and the Hermes detour saving the routine from a false-confident delete

**Designed-in safeguards**:
1. Iron Law: never delete a repo-shaped dir without origin-diff verification
2. Hermes coordination check before touching any `codex-burn-YYYYMMDD/` dir
3. Per-tier user approval (no auto-execution past Tier 0 without explicit yes)
4. Archive-then-delete pattern for anything ambiguous
5. Handoff doc commit as exit criterion (the skill considers itself incomplete until docs/sessions/ has the run log)

## Open follow-ups

- [#2666](https://github.com/vamseeachanta/workspace-hub/issues/2666) — cross-repo codex-burn pattern (assetutilities + worldenergydata still have unmerged `codex/burn-20260511-*-bundle` branches on origin). This cleanup's archive includes the audit-evidence from that batch as plan-phase input.
- The skill explicitly notes that committing 3.3 MB archives to `docs/sessions/archives/` may grow problematic. If `archives/` exceeds ~50 MB total over future runs, propose gitignoring the dir and routing archives to a non-git location (or LFS).

## Memory candidates

This run surfaced two patterns worth capturing as auto-memory:

1. **`feedback_hermes_coordination_before_local_analysis_delete.md`** — before deleting anything dated `codex-burn-YYYYMMDD/`, check `~/.hermes/skills/...codex-background-burn-orchestration.md` operating pattern + `hermes status/cron list/goals/` to confirm no in-flight reference.
2. **`project_local_analysis_cleanup_routine.md`** — codifies that `/mnt/local-analysis/` cleanup has skill `operations/mnt-analysis-cleanup/` available; routine pattern is "survey → Hermes check → Iron-Law verify → tiered approval → execute → handoff".

(Not writing these auto-memory files in this commit — that's a separate decision; the case-study reference in the skill already captures the same content for skill-internal use.)

## Cross-references

- Skill: `.claude/skills/operations/mnt-analysis-cleanup/SKILL.md`
- Case study: `.claude/skills/operations/mnt-analysis-cleanup/references/case-study-2026-05-12.md`
- Hermes skill referenced: `~/.hermes/skills/autonomous-ai-agents/agent-cli-delegation-operations/references/codex-background-burn-orchestration.md`
- Yesterday's cleanup handoff: `docs/sessions/2026-05-11-gtm-artifact-layout-audit.md`
- Open follow-up: [#2666](https://github.com/vamseeachanta/workspace-hub/issues/2666)
- Archive captured: `docs/sessions/archives/2026-05-11-codex-burn-artifacts.tar.gz` (3.3 MB, 149 entries)
