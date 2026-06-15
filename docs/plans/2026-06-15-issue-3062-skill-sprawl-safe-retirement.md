# Plan for #3062: Skill-sprawl cleanup — safe retirement + archive consolidation

> **Status:** blocked-draft (adversarial review MAJOR — safety model relies on a non-existent invocation signal; see review summary)
> **Complexity:** T3
> **Date:** 2026-06-15
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3062
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-15-plan-3062-{claude,codex,gemini}.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/skills/check_retirement_candidates.py` — **non-destructive** candidate flagger (#1725). Threshold `baseline_usage_rate < 0.05 AND calls_in_period < 10`; SKIPs null fields; writes JSON to `.claude/state/skill-retirement-candidates/`; never deletes/moves. **This is the detection layer — already exists and is gated.**
- Found: `scripts/skills/skill-usage-report.py` — produces `skill-scores.yaml` (the tier/score source).
- Gap: **no archival executor.** Nothing acts on the candidate JSON. #3062's core task ("run the retirement loop for real") = the missing safe *move-to-archive* step + retention rule, NOT detection.
- Found: two archive conventions — `.claude/skills/_archive/` (2,166 SKILL.md) and `_archive/skills/` (88). #3062 wants them unified.

### Documents consulted
- `docs/reports/2026-06-15-skill-sprawl-refresh-3062.md` — sprawl picture + safe methodology (this plan operationalizes it).
- Related: #1725 (retirement gating, merged), #1742 (gsd-aware usage tracking), #3058 (harden epic parent). #3106 (de-prescription) — separate axis, blocked.
- Memory: `feedback_narrow_grep_false_dead_before_deletion`, `feedback_subagent_acceptance_metric_drives_signal_deletion` — both warn against acting on a centrality/grep metric without independent confirmation.

### Evidence (embedded verification)
**File existence** (`ls`/`git show origin/main`, 2026-06-15):
- EXISTS: `scripts/skills/check_retirement_candidates.py`, `.claude/skills/_archive/` (2,166), `_archive/skills/` (88)
- Canonical telemetry CURRENT: `git show origin/main:.claude/state/skill-scores.yaml` → 830 skills, generated 2026-06-14 (NOT stale; cadence healthy — see report correction).
- MISSING (this plan creates): `scripts/skills/archive_retired_skills.py`, retention-rule doc, unified-archive convention.

**Reproduction proofs** (Step 1.5 — the "sprawl" claim):
```
$ uv run --no-project python scripts/skills/check_retirement_candidates.py   # against fresh 831 scores
534 flagged skill(s) from 831 checked
$ <count candidates in active HOT domains>
44
```
- 534 retirement candidates; **≥44 sit in active HOT domains** (orcaflex/aqwa/mooring/fatigue/hydro/structural/wave/well/energy/pandas/email/gmail) → unsafe to auto-retire. Reproduced 2026-06-15. Matches issue claim (sprawl real) AND confirms the false-positive risk.
- Source count: 5 distinct. ✓

### Gaps identified
- No safe archival executor + retention rule.
- `calls_in_period` is **derived from cross-refs/git, not true invocation** — so the 534 set needs an independent invocation signal before any move.
- Two archive trees unconsolidated.

---

## Deliverable
A reversible, gated archival workflow (`archive_retired_skills.py`, git-mv to ONE unified archive) plus a documented retention rule, applied to a **small, independently-verified first batch** of genuinely-dead non-domain skills — not a mass 534-archival.

---

## Pseudocode
```
# archive_retired_skills.py  (reversible, dry-run default)
candidates = load(skill-retirement-candidates/<date>.json)   # from existing gated detector
for c in candidates:
    if c.domain in HOT_DOMAIN_WHITELIST: skip  # the 44 — never auto-retire
    if c.calls_in_period > 0: skip
    if invoked_in_session_corpus(c.name): skip  # INDEPENDENT signal: grep ~/.claude/projects/**/*.jsonl
    if referenced_in_any_SKILL_or_command_body(c.name): skip  # wide grep, whole repo (feedback_narrow_grep)
    batch.append(c)
batch = batch[:BATCH_SIZE]          # small first increment, e.g. 25
for c in batch: git mv c.path  -> .claude/skills/_archive/<category>/   # reversible
write_retention_rule(); update unified-archive convention; record archived list
# --apply required; default dry-run prints the batch + every skip reason
```

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Create | scripts/skills/archive_retired_skills.py | reversible gated archival executor |
| Create | scripts/skills/tests/test_archive_retired_skills.py | TDD |
| Create | docs/standards/SKILL_RETENTION_RULE.md | documented retention/retirement policy |
| Move | .claude/skills/<dead-batch>/ → .claude/skills/_archive/ | first verified batch (git mv) |
| Consolidate | `_archive/skills/` (88) → `.claude/skills/_archive/` | one archive convention |
| Update | docs/plans/README.md | index row |

## TDD Test List
| Test | Verifies |
|---|---|
| test_dry_run_default | no moves without --apply |
| test_hot_domain_whitelisted | the 44 domain candidates never selected |
| test_skip_when_calls_nonzero | calls_in_period>0 excluded |
| test_skip_when_invoked_in_corpus | session-transcript invocation excludes a candidate |
| test_skip_when_referenced_widely | whole-repo reference excludes a candidate |
| test_git_mv_reversible | archived skill restorable from _archive |
| test_batch_size_capped | only BATCH_SIZE moved per run |

## Acceptance Criteria
- [ ] `archive_retired_skills.py --apply` moves only candidates passing ALL four safety gates; dry-run is default.
- [ ] First batch (≤25) archived via `git mv` (reversible); archived list recorded.
- [ ] `_archive/skills/` consolidated into `.claude/skills/_archive/`; one convention documented.
- [ ] `SKILL_RETENTION_RULE.md` defines thresholds, whitelist, and the independent-invocation requirement.
- [ ] No HOT/WARM/active-domain skill archived; spot-check the batch by hand.
- [ ] Tests pass; existing skill-pipeline tests still pass.

## Adversarial Review Summary
| Provider | Verdict | Findings |
|---|---|---|
| Claude (adversarial subagent) | **MAJOR** | (2) "44 hot-domain" is a name-substring artifact (14 are planning "wave" skills, "email"⊂"gmail"); derive domain from `path:` not names. (3) The load-bearing `invoked_in_session_corpus` gate matches **0 candidates** — the Skill tool records plugin-namespaced IDs (`superpowers:…`), not workspace-hub dir names; workspace-hub skills are retrieval/reference, not Skill-tool-invoked → no invocation signal exists. (4) ~half of candidates are referenced in OTHER skills' `related_skills`; archiving leaves dangling refs (unaddressed). (5) `scripts/skills/skill_archive_audit.py` already does the consolidation half (missed); detector misattributed to #1725 (it's WRK-1009). |
| Codex | NOT RUN | |
| Gemini | NOT RUN | |

**Overall result:** FAIL — re-draft required. The premise (sprawl real, executor missing, reversibility sound) holds, but the four-gate "defense-in-depth" is theater: 2 gates non-functional/non-independent. Honest safe case = reversibility (git mv; scoring excludes `_archive/`) + manual spot-check ONLY, for a tiny batch — AND the real blocker is that **no true skill-invocation signal exists** to make retirement safe at scale.

## Risks and Open Questions
- **Risk — DEAD ≠ unused (quantified):** ≥44 of 534 candidates are active-domain; `calls_in_period` is not true invocation. Mitigation: four independent safety gates + HOT-domain whitelist + manual spot-check + reversible git mv. **This is the load-bearing safeguard.**
- **Risk — archive bloat:** `.claude/skills/_archive/` already 2,166; archiving adds more. Open: should deep-archive (>1yr) be deleted, or is archive-forever acceptable? **User decision.**
- **Risk — retrieval hit-rate measurement** (a #3062 task) is deferred to a follow-on; this plan does retirement + consolidation only. Flagged, not silently dropped.
- **Open — batch size & cadence:** start at 25/run manual, or wire a gated cron? Recommend manual until the safety gates are proven. **User decision at approval.**
- **Open — approval drift:** issue is mislabeled `plan-approved` with no prior plan. This plan + review should precede re-approval; treat current label as drift, not authorization.

## Complexity: T3
Systemic (bulk file moves across the shared skills tree, new standing executor + policy). 3-provider adversarial review warranted.
