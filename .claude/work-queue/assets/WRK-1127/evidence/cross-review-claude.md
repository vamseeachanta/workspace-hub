# Claude Cross-Review — WRK-1127 Feature-First Planning

**Reviewer:** Claude (Sonnet 4.6)
**Date:** 2026-03-11
**Stage:** 6 — Cross-Review
**Artifact reviewed:** `specs/wrk/WRK-1127/wrk-1127-feature-first-planning.md`

---

## Review Scope

Plan completeness, TDD coverage, backward compatibility, adopt-existing-WRK logic
correctness, and stage contract impacts.

---

## 1. Plan Completeness

**Strengths:**

- All six risks identified in resource-intelligence.yaml (Stage 2) have explicit
  mitigations documented in the plan. Each plan task references the exact line numbers
  in `generate-index.py` where dual-site fixes are required. This is above-average
  risk specificity for a Route C plan.
- The three-child decomposition (child-a → child-b/child-c in parallel) is correctly
  structured. The dependency table is machine-parseable by `new-feature.sh`.
- The feature lifecycle flowchart at the top of the spec covers all status transitions
  (`pending` → planning → `coordinating` → `archived`) with clear triggers.
- `feature-template.md` includes every mandatory frontmatter field and the
  `## Decomposition` section that `new-feature.sh` parses.

**Gaps and findings:**

**MINOR-1: No TDD tests specified for generate-index.py changes (Task 5)**
Tasks 1–3 have `uv run --no-project python -c` YAML-validity checks. Tasks 6–8 have
integration smoke tests. Task 5 (generate-index.py normalize() and status filter
changes) has only a manual `grep` verification and a `generate-index.py` run. A
dedicated pytest test module (e.g. `tests/work_queue/test_generate_index_feature.py`)
asserting the `type`/`phases` defaults and the `coordinating` filter inclusion should
be added — consistent with the TDD hard gate in CLAUDE.md.

**MINOR-2: Stage 19 close gate not wired to feature-close-check.sh**
Task 12 documents that `feature-close-check.sh` must appear in Stage 19's
`blocking_condition`, but no task modifies `stage-19-close.yaml`. The plan leaves
the wiring to prose in SKILL.md, which is documentation, not enforcement. A child-c
task to add `blocking_condition: "feature-close-check.sh WRK-NNN (exit 0)"` to
`stage-19-close.yaml` should be added, or the plan should explicitly accept this
limitation.

**MINOR-3: Chunk-sizing heuristic cross-reference in CLAUDE.md not planned**
The plan adds `.claude/rules/feature-planning.md` and updates two SKILL.md files.
However, CLAUDE.md (Quick Reference section) currently has no pointer to the new
feature-planning rule. The 20-line limit on CLAUDE.md means adding a line may
require trimming another — this should be an explicit decision in child-a, not a
discovery during execution.

---

## 2. TDD Coverage Assessment

| Task | Test specified | Type | Verdict |
|------|---------------|------|---------|
| Task 1 — chunk-sizing.yaml | YAML parse check | sanity | OK |
| Task 2 — feature-planning.md | `wc -l` | format | OK |
| Task 3 — feature-template.md | none specified | — | WEAK |
| Task 4 — SKILL.md update | `wc -l` | format | OK |
| Task 5 — generate-index.py | grep + run only | integration | WEAK (see MINOR-1) |
| Task 6 — new-feature.sh | integration smoke test | integration | OK |
| Task 7 — feature-status.sh | smoke test (bash) | integration | OK |
| Task 8 — feature-close-check.sh | smoke test (bash) | integration | OK |
| Task 9 — dep_graph.py | smoke test (uv run) | integration | OK |
| Task 10 — INDEX.md By Feature | grep output check | integration | OK |
| Task 11 — stage-09-routing.yaml | YAML parse check | sanity | OK |
| Task 12 — work-queue-workflow SKILL.md | `wc -l` | format | OK |
| Task 13 — whats-next.sh | smoke test (bash) | integration | OK |
| Task 14 — WRK-1127.md | none | — | WEAK |

No unit-test files are in scope; all tests are integration-level shell or Python
one-liners. This is acceptable for harness tooling given the existing pattern in the
repo. The WEAK ratings on Tasks 3, 5, and 14 are acceptable at MINOR severity.

---

## 3. Backward Compatibility

**generate-index.py:** Adding `type` and `phases` to `FRONTMATTER_FIELDS` and using
`setdefault()` in `normalize()` is fully backward-compatible — existing WRK items
without these fields default to `task` and `[]` respectively. The `[feature]` badge
appears only when `type == "feature"`, so existing rows are unchanged.

**dep_graph.py:** The plan specifies a separate `FeatureTreeItem` dataclass and a new
`--feature` argparse flag. This is the correct approach. Existing `compute_graph()`,
`--critical-path`, `--dot`, and `--summary` code paths are not touched. Risk is low.

**whats-next.sh:** Adding a "Features in progress" section that calls
`feature-status.sh` only when coordinating items exist is additive. No existing
output sections are removed. Backward-compatible.

**stage-09-routing.yaml:** Adding a new top-level `feature_routing:` key to a
metadata-only YAML file that (per resource-intelligence) no script currently parses
as strict schema is safe. The plan correctly requires a `grep` check for consumers
before editing.

**WRK items:** `parent:`, `children:`, `blocked_by:` fields are additive to
frontmatter. All existing scripts use `get_field()` patterns that return empty strings
for missing fields. No existing WRK file is modified unless it appears in a
`wrk_ref:` column of a future feature's decomposition table.

---

## 4. Adopt-Existing-WRK Logic Correctness

The `new-feature.sh` adopt path (Task 6) uses `sed -i` to insert `parent:` into an
existing WRK's frontmatter immediately after the `id:` line:

```bash
sed -i "s/^id: ${wrk_ref}/id: ${wrk_ref}\nparent: ${WRK_ID}/" "$EXISTING"
```

**Issue (MINOR-4):** The `sed -i` `\n` newline escape is not portable across all
`sed` implementations (BSD `sed` on macOS requires `$'\n'` or a literal newline
within the substitution). The workspace target is Linux (`dev-primary`), so GNU sed
is guaranteed. Still, the plan should note this as a Linux-only assumption in the
script header comment to prevent future porting confusion.

**Issue (MINOR-5):** The adopt path updates `blocked_by:` only if `BLOCKED_BY != "[]"`.
If a decomposition table sets `deps: —` (dash) for an adopted item, the adopted WRK's
existing `blocked_by:` value is left unchanged. This is the correct behaviour when an
adopted item already has its own dependency chain. The plan text should make this
explicit ("adoption does not clear existing blocked_by").

**Correctness of parent insertion:** The `sed` pattern matches `^id: ${wrk_ref}` —
this correctly targets the frontmatter `id:` line. It does not match `# id:` in
comments or `child-id:` keys. The pattern is safe.

**Empty wrk_ref handling:** The condition `[[ -n "$wrk_ref" && "$wrk_ref" =~ ^WRK- ]]`
correctly skips blank `wrk_ref` columns and routes to the CREATE path. Non-WRK-
prefixed values in the `wrk_ref` column are also skipped (treated as blank).

---

## 5. Stage Contract Impacts

**Stage 7 exit:** The plan adds a new action at Stage 7 exit (run `new-feature.sh`).
This is documented in the stage contract via the work-queue-workflow SKILL.md update
(Task 12). No change to `stage-07-user-review-plan-final.yaml` is planned. This is
a documentation-only approach — acceptable for a planning WRK, but child-c should
consider whether the stage YAML's `exit_artifacts` list should include
`feature-decomposition.yaml`.

**Stage 9 routing:** The `feature_routing:` block is a new semantic key not present
in other stage YAML files. Its `condition` field is expressed as pseudo-code
(`frontmatter.type == 'feature' and stage7_complete`), which is fine for a human-
readable decision table but would need translation to actual script logic if a parser
is ever added. The plan appropriately defers the consumer-grep check to execution.

**Stage 19 close:** See MINOR-2. This is the most significant contract gap — a
Feature WRK with `status: coordinating` needs a concrete mechanism to prevent
Stage 19 from running until all children are `archived`. Prose documentation in
SKILL.md is not sufficient; the `blocking_condition` in `stage-19-close.yaml` should
be updated, or a wrapper script (e.g. `close-item.sh`) should call
`feature-close-check.sh` before allowing the close action.

---

## 6. Summary of Findings

| ID | Severity | Finding |
|----|----------|---------|
| MINOR-1 | MINOR | generate-index.py changes lack a pytest unit test |
| MINOR-2 | MINOR | Stage 19 blocking_condition not wired to feature-close-check.sh |
| MINOR-3 | MINOR | CLAUDE.md pointer to feature-planning.md not planned |
| MINOR-4 | MINOR | sed \n portability note missing from new-feature.sh script header |
| MINOR-5 | MINOR | adopt-path blocked_by non-overwrite behaviour not documented in plan prose |

No MAJOR findings. The plan is structurally sound, all Stage 2 risks have mitigations,
decomposition is correctly expressed, and backward compatibility is preserved throughout.

---

## Verdict: APPROVE

The plan is complete and implementable. The five MINOR findings can be resolved during
child WRK execution without requiring a re-review of the feature plan. No blockers to
Stage 7.
