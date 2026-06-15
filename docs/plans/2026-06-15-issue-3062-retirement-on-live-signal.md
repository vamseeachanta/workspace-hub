# Plan for #3062: skill retirement on the LIVE measured signal (supersedes the blocked draft)

> **Status:** blocked-draft (adversarial review MAJOR — signal is blind to @-include/path/prose usage; gates risk archiving a load-bearing skill. NOT approval-ready.)
> **Complexity:** T3
> **Date:** 2026-06-15
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3062
> **Client:** N/A
> **Lane:** lane:claude
> **Supersedes:** docs/plans/2026-06-15-issue-3062-skill-sprawl-safe-retirement.md (blocked-draft — MAJOR'd because the usage signal didn't exist; it now does)

---

## What changed — the blocker is cleared
The earlier #3062 plan FAILED adversarial review because its safety model rested on an invocation signal that didn't exist. That signal now exists and is LIVE: #3112 (chain) + #3139 (universe) + #3137 (Skill-tool) + #3138 (backfill) are merged, and a backfill-driven report just **demoted 214 skills by one tier on real 90-day usage**. Retirement can now run on *measured* zero-usage, not centrality.

## Resource Intelligence Summary (live, verified 2026-06-15)
- **Live tiers (post real-usage demotion):** HOT 41 / WARM 99 / COLD 106 / **DEAD 580** (universe 827, #3139 exclusions live). 133 skills carry real sessions (protected).
- **DEAD-580 composition (path-based, not name-substring — the prior MAJOR fix):** 90 are in **active domains** (`engineering/`, `email/`, `data/`, `business/sales/`) → protect/manual-review; 46 still show `calls_in_period>0` (reference signal) → not truly unused. Genuinely-safe candidate pool ≈ **444** before related_skills + spot-check filters.
- **Tooling that already exists (reuse, don't rebuild):** `scripts/skills/skill_archive_audit.py` (non-destructive archive-tree audit/consolidation); `scripts/skills/_skill_identity.py` (`discover_skills`/`derive_short_name`); `.claude/state/skill-invocations/*.json` (the live signal). Two archive trees to unify: `.claude/skills/_archive/` (~2,166) + `_archive/skills/` (88, 87 unique per #3062 audit).
- Coverage gate: `apply_invocation_demotion` needs `coverage_days >= 14`; live coverage is **90d** ✓.

## Deliverable
A reversible, measured-signal-gated archival: `scripts/skills/archive_retired_skills.py` moves only skills passing ALL safety gates (DEAD-tier post-demotion AND zero invocation sessions over the coverage window AND not in an active domain AND no `related_skills` back-ref), via `git mv` to one unified `_archive`, in small batches with manual spot-check — plus the `_archive/skills`→`.claude/skills/_archive` consolidation via the existing audit tool.

## Safety gates (ALL must pass per candidate)
1. **Measured zero-usage:** `session_count == 0` in `.claude/state/skill-invocations/` over `coverage_days >= 14` (live 90d). *This is the gate that didn't exist before.*
2. **DEAD tier** post real-usage demotion (not centrality-only).
3. **Not in an active domain** (path-prefix whitelist: engineering/email/data/business-sales + any HOT-domain neighbour) — the 90 protected.
4. **No `related_skills` back-reference** from a non-retiring skill (else rewrite that ref or skip the candidate — no dangling refs).
5. **Manual spot-check** of each batch (≤25) before `git mv`.

## Pseudocode
```
inv = load(".claude/state/skill-invocations/<latest>.json")   # the live signal
scores = load("skill-scores.yaml")
backrefs = build_related_skills_index(discover_skills(.claude/skills))
candidates = []
for skill, s in scores.items():
    if s.tier != "dead": continue
    if inv.coverage_days < 14 or inv[skill].session_count > 0: continue   # gate 1+2
    if path_in_active_domain(s.path): continue                            # gate 3
    if skill in backrefs and backref_source not retiring: continue        # gate 4
    candidates.append(skill)
batch = candidates[:BATCH_SIZE]            # ≤25, manual spot-check (gate 5)
for c in batch: git mv <c.path> -> .claude/skills/_archive/<category>/    # reversible
# + consolidate _archive/skills -> .claude/skills/_archive via skill_archive_audit.py
```

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Create | scripts/skills/archive_retired_skills.py | measured-signal-gated reversible archiver (dry-run default) |
| Create | scripts/skills/tests/test_archive_retired_skills.py | TDD: each gate, dry-run, git-mv reversibility, batch cap |
| Use | scripts/skills/skill_archive_audit.py | the `_archive/skills`→unified consolidation (don't rebuild) |
| Create | docs/standards/SKILL_RETENTION_RULE.md | retention policy (thresholds, whitelist, measured-usage requirement) |
| Update | docs/plans/README.md | index (at impl time) |

## TDD Test List
| Test | Verifies |
|---|---|
| test_dry_run_default | no moves without --apply |
| test_gate_measured_usage | session_count>0 → never retired (even if DEAD tier) |
| test_gate_coverage_floor | coverage<14d → no retirements at all |
| test_gate_active_domain_protected | engineering/email/data skill never selected |
| test_gate_related_skills_backref | candidate referenced by a live skill → skipped (no dangling ref) |
| test_git_mv_reversible | archived skill restorable |
| test_batch_capped | ≤BATCH_SIZE per run |

## Acceptance Criteria
- [ ] Tests pass; existing skill tests unaffected.
- [ ] `--apply` archives only candidates passing all 5 gates; dry-run default; reversible git mv.
- [ ] First batch (≤25) hand-verified; archived list recorded; `_archive/skills` consolidated.
- [ ] `SKILL_RETENTION_RULE.md` documents the measured-usage policy.
- [ ] NO active-domain or measured-used skill archived (spot-check + the 90-protected confirmed).

## Adversarial Review Summary
| Provider | Verdict | Findings |
|---|---|---|
| Claude (adversarial) | **MAJOR** | (1) **Signal blind to non-Read usage** — backfill is Read-of-SKILL.md ONLY (Skill-tool skipped); skills loaded via `@`-include / referenced by path in CLAUDE.md/SOUL/rules / prose links produce 0 Read events → can be DEAD+zero-session yet load-bearing. Archiving one breaks the include (reviewer's example: an `@`-included DEAD skill passing all 5 gates — example unconfirmed by my grep, but the risk class is verified). (2) domain whitelist misses 86 HOT/WARM skills outside the 4 prefixes + `business/sales` arbitrary. (3) related_skills index is name-keyed + frontmatter-only → misses prose/rule refs + breaks on 11 basename collisions. (4) `git mv`→_archive may not change Skill-tool loadability (real surface is `~/.claude`), but DOES break path/@-include refs. (5) tier(DEAD) vs session_count disagree on ~51 skills — 3 unreconciled retirement signals. (6) pseudocode schema wrong (`rows` LIST + `session_count_available_days`, not skill-keyed `session_count`) — CONFIRMED. |
| Codex/Gemini | NOT RUN | |

**Overall:** FAIL — do NOT approve. Required before re-review: **add a reference-scanning gate** (@-includes + path/prose refs in CLAUDE.md/SOUL/rules/skill-bodies, keyed by rel-path); reconcile the 3 retirement signals + the 51 DEAD-but-used contradictions; fix the schema pseudocode; derive or drop the domain whitelist. Retirement stays STOPPED — the review prevented archiving load-bearing skills.

## Risks
- **Measured-usage is a 90-day window, not all-time** — `backfill` NOTE: absence of an event ≠ never-used pre-window. Mitigation: archive-not-delete (reversible); start with skills DEAD by BOTH centrality AND measured zero-usage.
- **The 46 ref-signal DEAD skills** — DEAD tier but `calls_in_period>0`: exclude from the first batch (conflicting signals → manual review).
- **Genuine basename collisions** (`session-corpus-audit`) — out of scope; do not retire a colliding skill without disambiguation.
- **Auto-committer** on the shared checkout — implement via dedicated branch; orchestrator serializes commits.

## Complexity: T3 — archival of shared skill content + new gated tool; reversible but ecosystem-wide. Adversarial review then user approval before any move.
