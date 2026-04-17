# Plan for #2322: Promote binary-checkable .claude/rules/*.md prose to Level 2 scripts per enforcement gradient

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2322
> **Review artifacts:** scripts/review/results/2026-04-17-plan-2322-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.claude/rules/patterns.md` — defines 4-level enforcement gradient (prose → micro-skill → script → hook) with explicit migration path.
- Found: `.claude/rules/coding-style.md` — contains the three prose rules targeted for promotion: no-hardcoded-absolute-paths, harness-file-size-≤20, queue-git-tracked.
- Found: `scripts/enforcement/` — 18 existing enforcement scripts (`check-config-protection.sh`, `require-plan-approval.sh`, `require-cross-review.sh`, etc.) plus a `tests/` subdir. Pattern: exit 0/1 shell semantics; many already wired to pre-commit or pre-push.
- Found: `.pre-commit-config.yaml` — has working pattern for local hooks (`validate-work-queue-state` calls `scripts/work-queue/validate-queue-state.sh`).
- Found: `scripts/enforcement/install-hooks.sh` — canonical install point for pre-commit/pre-push wiring.
- Gap: no script enforces absolute-path ban, harness-size cap, or queue-git-tracked.

### Standards
| Standard | Status | Source |
|---|---|---|
| n/a — harness/enforcement work | n/a | — |

### LLM Wiki pages consulted
- Not applicable.

### Documents consulted
- Issue #2018 — agent bypass resistance — technical gates (parent umbrella; this plan is one concrete slice).
- Issue #2028 — review gate strict mode + GitHub Actions CI enforcement workflow (sibling).
- Issue #1876 — enforce engineering workflow via Hermes prefill + Claude Code hooks (sibling).
- Memory: `feedback_queue_git_tracked.md` — the source of the queue-git-tracked rule.
- `.claude/rules/README.md` — explicit statement: "Universal constraints only. Stage-specific rules live in micro-skills."
- `CLAUDE.md` at repo root — currently 9 lines (passes harness cap).

### Gaps identified
- Three Level-0 prose rules that are binary-checkable have no enforcement script.
- No regression test fixtures demonstrating pass/fail for these checks.
- The rules files themselves don't cite scripts (so rule readers don't know a check exists).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-17-issue-2322-rule-promotion.md` |
| Script 1 | `scripts/enforcement/check-no-abs-paths.sh` |
| Script 2 | `scripts/enforcement/check-harness-file-size.sh` |
| Script 3 | `scripts/enforcement/check-queue-git-tracked.sh` |
| Tests | `scripts/enforcement/tests/test_check_no_abs_paths.bats` (or `test_*.sh`) |
| Tests | `scripts/enforcement/tests/test_check_harness_file_size.bats` |
| Tests | `scripts/enforcement/tests/test_check_queue_git_tracked.bats` |
| Fixtures | `scripts/enforcement/tests/fixtures/` |
| Pre-commit wire | `.pre-commit-config.yaml` (modify) |
| Hook installer | `scripts/enforcement/install-hooks.sh` (modify if pre-push needed) |
| Rule pointers | `.claude/rules/coding-style.md`, `.claude/rules/patterns.md` (modify to cite scripts) |
| Plan review — Claude | `scripts/review/results/2026-04-17-plan-2322-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-17-plan-2322-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-17-plan-2322-gemini.md` |

---

## Deliverable

Three `scripts/enforcement/check-*.sh` scripts with exit-0/1 semantics, each with a regression test fixture; harness-file-size check wired to pre-commit; rules files updated to reference the scripts.

---

## Pseudocode

```
# check-no-abs-paths.sh
# Scope: tracked .sh and .py files under scripts/, .claude/, and root
# Allowlist: explicit constants, test fixtures, file-path arg parsing
violations=[]
for file in $(git ls-files 'scripts/**/*.sh' 'scripts/**/*.py' '*.sh'):
    for line_no, line in enumerate(file):
        if match(line, r'/home/|/mnt/|/Users/|D:\\|C:\\') and not in_allowlist(file, line_no):
            violations.append("$file:$line_no: $line")
if violations: print all; exit 1
exit 0

# check-harness-file-size.sh
# Caps: CLAUDE.md, MEMORY.md, AGENTS.md, GEMINI.md ≤ 20 lines each
# Scope: repo root + anywhere these files appear (not skill frontmatter)
over_cap=[]
for file in find_harness_files():
    lines = wc -l
    if lines > 20: over_cap.append("$file: $lines lines (>20)")
if over_cap: print all; exit 1
exit 0

# check-queue-git-tracked.sh
# Reads .claude/work-queue/*.{yaml,json} entries
# For each entry with a file path, confirms `git ls-files` matches
missing=[]
for queue_file in .claude/work-queue/*.yaml:
    entries = yaml.safe_load(queue_file)
    for entry in entries:
        for path_field in ("path", "file", "target"):
            p = entry.get(path_field)
            if p and not git_ls_files(p): missing.append(...)
if missing: print all; exit 1
exit 0
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/enforcement/check-no-abs-paths.sh` | implementation |
| Create | `scripts/enforcement/check-harness-file-size.sh` | implementation |
| Create | `scripts/enforcement/check-queue-git-tracked.sh` | implementation |
| Create | `scripts/enforcement/tests/test_check_no_abs_paths.bats` | tests |
| Create | `scripts/enforcement/tests/test_check_harness_file_size.bats` | tests |
| Create | `scripts/enforcement/tests/test_check_queue_git_tracked.bats` | tests |
| Create | `scripts/enforcement/tests/fixtures/{ok,violating}/` | fixtures |
| Modify | `.pre-commit-config.yaml` | wire harness-file-size hook |
| Modify | `.claude/rules/coding-style.md` | cite new scripts at rule sites |
| Modify | `.claude/rules/patterns.md` | cite new scripts as Level-2 examples |
| Update | `docs/plans/README.md` | add row for this plan |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_abs_paths_fail_on_home | detects `/home/...` in a script | fixture file containing `/home/vamsee/x` | exit 1, message cites file:line |
| test_abs_paths_fail_on_mnt | detects `/mnt/...` | fixture with `/mnt/local-analysis/...` | exit 1 |
| test_abs_paths_pass_on_relative | no violation for relative paths | fixture using `$(git rev-parse --show-toplevel)` | exit 0 |
| test_abs_paths_allowlist | allowlisted file ignored | fixture marked as test-fixture | exit 0 |
| test_harness_pass_under_20 | 10-line CLAUDE.md passes | fixture | exit 0 |
| test_harness_fail_over_20 | 25-line MEMORY.md fails | fixture | exit 1 |
| test_harness_ignores_skill_frontmatter | SKILL.md not checked | SKILL.md in fixture | exit 0 |
| test_queue_pass_tracked_path | entry with tracked path passes | fixture queue + real git file | exit 0 |
| test_queue_fail_missing_path | entry referencing untracked file | fixture with nonexistent path | exit 1, names missing path |
| regression_precommit_harness_blocks_over_cap | pre-commit hook blocks commit that inflates MEMORY.md >20 | `pre-commit run` | non-zero exit |

---

## Acceptance Criteria

- [ ] All 3 scripts created under `scripts/enforcement/` with `exit 0`/`exit 1` semantics.
- [ ] Each script has ≥3 regression tests covering pass + fail + edge case.
- [ ] `pre-commit run check-harness-file-size --all-files` works.
- [ ] An intentionally-inflated MEMORY.md (>20 lines) is blocked by the hook.
- [ ] `.claude/rules/coding-style.md` and `patterns.md` cite each new script at the relevant prose rule.
- [ ] No false positives when run against current clean repo (`bash scripts/enforcement/check-no-abs-paths.sh` exits 0).
- [ ] `scripts/enforcement/install-hooks.sh` wires any additional hooks if added.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR | `.bats` test style not repo-native (use `test_*.sh`); allowlist design for abs-path check is vague; queue schema unverified; pre-commit vs pre-push timing |
| Codex | MAJOR | (see scripts/review/results/2026-04-17-plan-2322-codex.md — correctness + scope issues) |
| Gemini | MAJOR | (see scripts/review/results/2026-04-17-plan-2322-gemini.md — correctness + scope issues) |

**Overall result:** FAIL — MAJOR from Codex+Gemini. Plan requires revision before user approval.

**Blockers to resolve before approval:** see per-provider review artifacts under `scripts/review/results/2026-04-17-plan-2322-*.md`.

---

## Risks and Open Questions

- **Risk:** False-positive on absolute-path check blocks legitimate file_path parameters in tool calls. Mitigation: allowlist file patterns (e.g., `tests/**/fixtures/**`).
- **Risk:** Harness-size check flags the temporary addition of a line during editing. Mitigation: hook runs on commit only, not on save.
- **Risk:** Queue-git-tracked check's schema assumption may not match all queue formats. Mitigation: start narrow (one schema), widen incrementally.
- **Open:** Should `check-no-abs-paths.sh` also apply to `.md` files? Recommend no for v1 — docs routinely cite paths.
- **Open:** Pre-push vs pre-commit for absolute-path check? Recommend pre-commit (faster feedback).

---

## Complexity: T2

**T2** — three scripts, tests, pre-commit wiring, rule-doc updates. Bounded scope; no external dependencies.
