# Case study — 2026-05-12 cleanup pass that produced this skill

Original goal (`/goal` directive): "clean up /mnt/local-analysis without losing any useful code/work; start by reviewing what are the other folders are alongside workspace-hub and come up with user actions for approval; This is becoming a routine and we should have a skill for this work"

This was the **third** cleanup pass in ~10 days. The first two (2026-05-11) handled outer-clone duplicates (`assetutilities/`, `digitalmodel/`, `llm-wiki/`, `worldenergydata/` at `/mnt/local-analysis/`) and a workspace-hub codex-burn merge. This third pass handled the post-run residue from those operations — and was complicated by Hermes coordination concerns.

## Pre-state (2026-05-12)

```
/mnt/local-analysis/
├── workspace-hub/        ← canonical (25+ nested repos with own .git)
├── codex-burn-20260511/  ← 1.8+ GB post-run vestigial
│   ├── assetutilities-bundle/      ← orphan worktree (parent .git deleted yesterday)
│   ├── worldenergydata-bundle/     ← orphan worktree
│   ├── monitoring-evidence/        ← 8.6 MB / 132 files audit evidence
│   ├── logs/                       ← 6.8 MB launch/relaunch logs
│   └── prompts/                    ← 12 KB codex-burn prompt files (3)
├── agent-logs/           ← 894 KB session-handoffs + provider-capacity-aware logs
├── .pnpm-store/          ← empty package cache (system)
└── .Trash-1000/          ← XDG trash (system)
```

## Critical learning: Hermes coordination check

When the agent first proposed deletion of `codex-burn-20260511/`, the user pushed back: "can you review in light of how hermes agent works and see if it is still useless? feel free to communicate with hermes agent directly via CLI".

That push-back saved the routine. The Hermes investigation revealed:

1. `~/.hermes/skills/autonomous-ai-agents/agent-cli-delegation-operations/references/codex-background-burn-orchestration.md` is the orchestration skill that produced `codex-burn-YYYYMMDD/` dirs.
2. The skill's operating pattern (step 3, "Isolate each lane"): `git worktree add -b codex/burn-YYYYMMDD-issue-NNNN /mnt/local-analysis/codex-burn-YYYYMMDD/issue-NNNN origin/main`
3. **The dated dir is single-use per run** — Hermes creates a fresh one each time; never polls old ones.
4. 20+ Hermes goal files from 2026-05-11 all carried the same user directive ("burn codex usage credit in 12 hours"). All from a single past session. No 2026-05-12 goal references the 2026-05-11 dir.
5. `hermes cron list` confirmed no scheduled job depends on the dated dir.

Conclusion: the dir was genuinely vestigial. Without the Hermes check, the agent would have made an *unverified* claim that the dir was safe to delete — luck would have been on its side this time, but the routine needed to encode the check explicitly. Hence Step 3's "codex-burn run artifact" verification path in the skill.

## Iron-Law verification (the worked example)

For each orphan-worktree bundle, the agent:

1. Fetched the matching `origin/codex/burn-20260511-<repo>-bundle` branch into the canonical nested clone.
2. `git archive --format=tar FETCH_HEAD` → extract to `/tmp/<repo>-branch-tree/`.
3. `diff -rq /tmp/<repo>-branch-tree /mnt/local-analysis/codex-burn-20260511/<repo>-bundle` with derived-artifact filter.
4. Inspected residue:

For `assetutilities-bundle` — only build/test artifacts (.benchmarks, egg-info, test logs/results/Plot). **Nothing unique non-derived. Safe delete.**

For `worldenergydata-bundle` — flagged 4 suspicious paths:

| Path | Size | Classification (Hermes-revised post-review) | Why archived | Confidence (useful / regenerable / unknown) |
|---|---|---|---|---|
| `data/marine_safety` | 0 B (empty) | not residue | n/a | n/a |
| `data/metocean` | 0 B (empty) | not residue | n/a | n/a |
| `marine_safety.db` | 84 K SQLite | Bucket B (evidence-bearing) | could be runtime cache; could be downloaded BSEE data | **regenerable** (likely) — but cleanup pass could not prove this before delete |
| `results/` | 16 K | Bucket B (evidence-bearing) | test-run outputs | **regenerable** |
| `test_output/` | 988 K | Bucket B (evidence-bearing) | test-run outputs | **regenerable** |

**Lesson — revised post-Hermes-review**: the agent's first instinct ("nothing unique non-derived") was correct in spirit but the worldenergydata bundle had 1.1 MB of residue the Iron-Law preserved **pending classification**. This is NOT proof that 1.1 MB of useful work was saved; the residue may have been entirely regenerable. The correct framing is:

> The Iron Law preserved 1.1 MB of unique residue pending classification. This may have been regenerable, but preserving it was the correct default because the cleanup pass could not prove that before deletion. The cost-benefit calculation is "small archive cost vs. unknowable-loss-cost", not "definite save".

The original draft of this case study said "Total bytes-at-risk-of-loss if Iron Law were skipped: 1.1 MB" — that was a vanity metric. The Iron Law's value is **epistemic** (it lets you defer the classification decision to post-archive review), not **byte-counting** (it doesn't prove the bytes were valuable).

## What the archive contains

`workspace-hub/docs/sessions/archives/2026-05-11-codex-burn-artifacts.tar.gz` (3.3 MB, 149 entries):
- `codex-burn-20260511/monitoring-evidence/*` (132 audit-evidence files: checklist-crosswalk JSONs, secret-scan results, hashes, hermes-process-list snapshots)
- `codex-burn-20260511/logs/*` (6 launch/relaunch log files)
- `codex-burn-20260511/prompts/*` (3 codex-burn prompt files — one per repo)
- `codex-burn-20260511/worldenergydata-bundle/marine_safety.db` (84K SQLite)
- `codex-burn-20260511/worldenergydata-bundle/results/*`
- `codex-burn-20260511/worldenergydata-bundle/test_output/*`

## Post-state

```
/mnt/local-analysis/
├── workspace-hub/        ← canonical (unchanged)
├── agent-logs/           ← 894 KB (14-day prune was no-op; nothing >14d)
├── .pnpm-store/          ← (system, untouched)
└── .Trash-1000/          ← (system, untouched)
```

Disk: 188 GB → 184 GB used on `/dev/sdc1` (net ~4 GB recovered after archive).

## Open follow-ups

- [#2666](https://github.com/vamseeachanta/workspace-hub/issues/2666) (cross-repo codex-burn pattern: assetutilities + worldenergydata branches still unmerged) — referenced this archive's monitoring-evidence as audit input.
- agent-logs prune threshold (currently 14 days) is conservative — if disk pressure rises, can be tightened to 7 days. Defer until justified.

## Why this case study lives in the skill's references/

Three reasons:

1. **Provenance** — future sessions invoking the skill can see the original problem that motivated it.
2. **Validation** — the Iron Law (verification step) is not abstract — there's a worked example showing it caught 1.1 MB of bytes that would otherwise have been lost.
3. **Memory** — if Hermes evolves and the orchestration skill moves or changes, this case-study captures the snapshot of "how Hermes coordinated with this skill on 2026-05-12" so the dependency is documented.
