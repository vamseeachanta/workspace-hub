# Plan for #3106: De-prescription sweep + content-quality standard & gate

> **Status:** blocked-draft (needs-decision — adversarial review returned MAJOR, premise invalidated)
> **Complexity:** T3
> **Date:** 2026-06-15
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3106
> **Client:** N/A
> **Project:** (n/a)
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-15-plan-3106-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/enforcement/check-model-id-sourcing.sh` — the **prior-art template**. RATCHET design: a baseline file (`model-id-baseline.txt`) grandfathers current occurrences; the guard flags only NEW ones; advisory by default, `--enforce` exits 1; per-file mode for pre-commit/tests; line-level exempt sentinel (`# model-id-ok`). The content-quality gate will mirror this shape.
- Found: `scripts/enforcement/tests/` — convention is `test_check_<name>.sh` + `fixtures/`. New gate gets `test_check_content_quality.sh`.
- Found: `.claude/state/skill-scores.yaml` (95 KB) + `.claude/state/skill-eval-results/*.jsonl` (daily) — **traffic/health telemetry** to rank which skills to rewrite first.
- Found: `scripts/enforcement/correction-to-skill-candidates.sh` — only content-adjacent script; it *adds* skills, does not gate quality. Confirms the quality-gate gap.
- Gap: **no enforcement script scores skill/command/markdown body quality** (`ls scripts/enforcement/ | grep -iE 'skill|command|prescri|quality|stale'` → only `correction-to-skill-candidates.sh`).

### Standards
Not applicable (harness/governance issue, no engineering standard).

### LLM Wiki pages consulted
No relevant wiki pages (harness content, not domain knowledge).

### Documents consulted
- `analysis/2026-06-13-fable5-opus-parity-learning.md` (#3056) — deltas D1 (verbosity), D4 (loop-exit), D5 (defensive re-reads): the behaviors over-prescriptive scaffolding fights.
- `analysis/2026-06-15-fable5-external-corpus-validation.md` (#3109) — out-of-sample confirmation that terse/autonomous behavior is a model property, raising confidence in the de-prescription bet.
- Related issues: #3062 (skill *sprawl/retrieval* — distinct axis: count not content), #3054 (learning loops), #3060 (`check-model-id-sourcing.sh` — the ratchet template), #3107 (fable-mode adapter — consumes this standard).
- External method: video *Make ANY Model Think Like Fable in Minutes* + AlphaSignal/Mythos guides → the 4-Deletions/5-Additions recipe.

### Gaps identified
- No content-quality standard doc exists.
- No gate flags over-prescriptive scaffolding, missing/weak `description:` frontmatter, or dead cross-links in skill/command/markdown bodies.
- The 164-command surface and markdown bodies have zero quality coverage.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-15 via `gh issue view`):
- `#3106` — OPEN — De-prescription sweep (this issue)
- `#3062` — OPEN, status:plan-approved — skill sprawl/retrieval (adjacent, not overlapping)
- `#3060` — OPEN — config/model regression guard (ratchet template source)

**File existence** (`ls` 2026-06-15):
- EXISTS: `scripts/enforcement/check-model-id-sourcing.sh`, `scripts/enforcement/tests/`, `.claude/state/skill-scores.yaml`
- MISSING (this plan creates): `scripts/enforcement/check-content-quality.sh`, `scripts/enforcement/content-quality-baseline.txt`, `docs/standards/CONTENT_QUALITY_STANDARD.md`, `scripts/enforcement/tests/test_check_content_quality.sh`

**Reproduction proofs** (verify-against-repo-state, Step 1.5):
```
$ grep -rliE 'step [0-9]+:|show your reasoning|context budget' .claude/skills | grep -vE '/_archive/|/_internal/|/session-logs/' | wc -l
110
```
- Reproduced at: 2026-06-15T13:1x UTC. Failure mode matches issue claim: YES — 110 active skill files carry over-prescriptive scaffolding.
- Source count: 6 distinct sources (issue body + 5 above). ✓ ≥3.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-15-issue-3106-content-quality-gate.md |
| Standard | docs/standards/CONTENT_QUALITY_STANDARD.md |
| Gate script | scripts/enforcement/check-content-quality.sh |
| Ratchet baseline | scripts/enforcement/content-quality-baseline.txt |
| Tests | scripts/enforcement/tests/test_check_content_quality.sh (+ fixtures/) |
| Rewrites | .claude/skills/**/SKILL.md (top-traffic batch) |
| Plan reviews | scripts/review/results/2026-06-15-plan-3106-{claude,codex,gemini}.md |

---

## Deliverable

A content-quality standard + a Level-2 ratchet gate (`check-content-quality.sh`) that flags newly-introduced over-prescriptive scaffolding / weak descriptions / dead links across skills, commands, and markdown, plus a first burn-down of the 110 grandfathered skill files starting with the highest-traffic ones ranked from `skill-scores.yaml`.

---

## Pseudocode

```
# check-content-quality.sh  (mirrors check-model-id-sourcing.sh ratchet)
scope = files passed as args, else tracked .claude/skills/**/SKILL.md +
        .claude/commands/** + .claude/rules/*.md + docs/**  (excl _archive/_internal/session-logs)
for each file:
    findings = []
    # 4 Deletions (over-prescription markers)
    findings += grep over-prescriptive: 'step \d+:' recipes, 'show your reasoning',
                'context budget/countdown', enumerated edge-case blocks
    # frontmatter quality (skills/commands)
    if SKILL.md and (no description: OR description < 10 words): findings += weak-description
    # staleness — delegate model-IDs to existing guard; here flag dead cross-links
    findings += broken_relative_links(file)  # [..](path) targets that don't exist
    occ_key = "file::marker_type" for each finding
    if occ_key not in baseline: NEW_violations += occ_key
report NEW_violations
advisory: print; --enforce: exit 1 if NEW_violations; --update-baseline: rewrite baseline
line-level exempt sentinel: "# content-quality-ok" (path-restricted; the standard doc + tests + fixtures self-exempt)
```

Burn-down (separate from gate): rank grandfathered files by `skill-scores.yaml` hot/warm score → rewrite top batch per the 5-Additions recipe → `--update-baseline` to remove rewritten occurrence keys → baseline count monotonically decreases.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | docs/standards/CONTENT_QUALITY_STANDARD.md | the 4D/5A standard the gate enforces |
| Create | scripts/enforcement/check-content-quality.sh | Level-2 ratchet gate |
| Create | scripts/enforcement/content-quality-baseline.txt | grandfather the 110 existing occurrences |
| Create | scripts/enforcement/tests/test_check_content_quality.sh (+ fixtures) | TDD for the gate |
| Modify | scripts/enforcement/install-hooks.sh | wire gate as pre-commit (advisory first) |
| Modify | .claude/skills/**/SKILL.md (top-traffic batch) | de-prescription rewrites |
| Update | docs/plans/README.md | index row |

---

## TDD Test List

| Test name | Verifies | Input | Output |
|---|---|---|---|
| test_flags_new_overprescription | new `step 1:` recipe in a non-baselined file flagged | fixture w/ step-recipe | exit 1 under --enforce |
| test_grandfathered_not_flagged | baselined occurrence key passes | fixture in baseline | exit 0 |
| test_weak_description_flagged | SKILL.md w/ <10-word description | fixture | flagged |
| test_missing_description_flagged | SKILL.md w/ no description: | fixture | flagged |
| test_dead_link_flagged | `[x](./nope.md)` to missing target | fixture | flagged |
| test_exempt_sentinel_respected | line w/ `# content-quality-ok` | fixture | not flagged |
| test_per_file_mode | only scans passed files (pre-commit) | one file arg | scopes correctly |
| test_update_baseline_monotonic | --update-baseline only removes fixed keys | rewritten fixture | baseline shrinks |

---

## Acceptance Criteria

- [ ] `bash scripts/enforcement/tests/test_check_content_quality.sh` passes (all cases above).
- [ ] Gate advisory-clean on a fresh checkout (baseline grandfathers the 110); `--enforce` exits 1 only on newly-introduced violations.
- [ ] `CONTENT_QUALITY_STANDARD.md` documents the 4D/5A recipe + each marker + the exempt sentinel.
- [ ] Top-traffic skill batch rewritten; baseline count drops by the number rewritten (monotonic burn-down evidence).
- [ ] No regression: existing enforcement tests still pass.
- [ ] Review artifacts posted to scripts/review/results/.
- [ ] Measured: tokens/turn on an affected task profile does not regress vs the #3061 / parity-baseline.json metric.

---

## Adversarial Review Summary

<!-- Populated after Step 3. Plan NOT surfaced as approval-ready until filled and no-MAJOR. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (adversarial subagent) | **MAJOR** | (1) Reproduction signal ~98% false-positive: `show your reasoning`=0 hits, `context budget`=3, `step N:`=108 mostly legitimate ordered procedures + ≥16 TOC links into decomposed sub-skill dirs. (2) Premise unmeasured for this repo; AC7 depends on a per-profile metric that doesn't exist (#3061 still open; parity-baseline.json is a single aggregate). (3) Burn-down unenforceable; no negative test for the dominant false-positive class. (4) Factual: #3060 is CLOSED not OPEN; skill-scores.yaml stale (2026-04-03, total_skills 402). |
| Codex | NOT RUN | T3 warrants it; deferred pending re-scope decision |
| Gemini | NOT RUN | deferred pending re-scope decision |

**Overall result:** FAIL — re-draft required. Premise (de-prescription debt) not supported by repo content; do NOT advance to plan-review. Decision required from user on direction (see issue checkpoint comment).

---

## Risks and Open Questions

- **Risk — false positives on legitimate `step N:`**: some skills legitimately enumerate procedural steps where order is load-bearing (e.g. install sequences). Mitigation: the marker is "frozen recipe that forbids replanning", not any numbered list. The gate flags advisory; the standard defines the distinction; the exempt sentinel covers genuine cases. **Open: validate the false-positive rate on the 110 before `--enforce`.**
- **Risk — ratchet baseline becomes a dumping ground**: same critique as model-id-baseline. Mitigation: burn-down is an acceptance criterion (count must drop), not optional.
- **Risk — scope creep to all 1,014 skills**: this issue rewrites only the top-traffic batch; the gate prevents *new* debt; remaining burn-down is a cadence (ties to #3062). Do not block this issue on rewriting all 110.
- **Risk — commands/markdown heuristics differ from skills**: frontmatter checks apply to SKILL.md/commands; markdown gets link + staleness checks only. Keep per-surface rule sets explicit.
- **Open:** should `--enforce` be wired now (pre-commit hard-block) or stay advisory for a probation window? Recommend advisory first (matches model-id-sourcing rollout), promote to `--enforce` after false-positive rate is measured. **User decision at approval.**

---

## Complexity: T3

**T3** — touches the enforcement layer (systemic), creates a new standing gate + standard, and rewrites shared skill content consumed by all agents. Warrants 3-provider adversarial review (Claude + Codex + Gemini) per the SOUL review-scale rule.
