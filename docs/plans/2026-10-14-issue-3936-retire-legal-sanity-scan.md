# Plan for #3936: Retire legal-sanity-scan and move identifier verification to final reports

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-10-14
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3936
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-10-14-plan-3936-claude.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/legal/` — does NOT contain `legal-sanity-scan.sh` in the main-tree checkout (confirmed by `ls -la` 2026-10-14T). The script exists only in stale worktrees (`.worktrees/issue-3549-connection-plan/`, `.worktrees/issue-3549-implementation/`, `.worktrees/issue-3522-private-rule-map-plan/`).
- Found: `.claude/skills/coordination/legal-sanity-scan/SKILL.md` v3.0.0 — already a compatibility pointer with retirement notice: `type: reference`, body reads "Retired: legal-sanity-scan".
- Found: `docs/standards/FINAL_REPORT_VERIFICATION.md` — policy doc already exists; documents the owner decision (2026-10-03) and the manual review checklist replacing the scanner. Section "Migration limits" explicitly states live instructions demanding the retired scanner are superseded.
- Found: `config/agents/*SOUL.runtime.md` (5 files: claude, codex, hermes, gemini, agy) — each carries the retirement notice at line 105 verbatim: *"legal-sanity-scan and automatic repository identifier gates are retired"*.
- Found: `config/agents/skill-index-full.yaml:391–393` — entry already updated to `when_to_use: legal-sanity-scan Retired scanner compatibility notice; route legacy requests to manual final-report verification.`
- Found: `.pre-commit-config.yaml` — no entry invoking legal-sanity-scan (confirmed by `grep` 2026-10-14T).
- Found: `.github/workflows/` — no workflow invokes legal-sanity-scan (confirmed by `grep` 2026-10-14T).
- Found: related open issues — #3804, #3871, #3933, #3935 — all OPEN; all describe scanner bugs now moot by retirement decision.
- Gap: no regression test asserts the scanner is absent from the main checkout.
- Gap: related issues #3804, #3871, #3933, #3935 not yet closed as superseded.
- Gap: `docs/standards/FINAL_REPORT_VERIFICATION.md` lacks a "migration verified complete" checklist entry naming each component.

### Standards

Not applicable — governance/tooling retirement, not an engineering calculation.

### LLM Wiki pages consulted

No relevant wiki pages found for scanner retirement procedures.

### Documents consulted

- Issue body #3936 — owner directive: "retire legal-sanity-scan; allow material to flow through repositories and verify at final report". Migration surface: "active callers, CI/pre-commit/readiness, generated guidance and final-report evidence".
- Related issue #3804 — OPEN: `legal-sanity-scan.sh --repo=<name> scans NOTHING and exits 0` (fail-open bug). Moot by retirement.
- Related issue #3871 — OPEN: `fix(legal): reject empty resolved scan targets and reconcile duplicate resolver definitions`. Moot by retirement.
- Related issue #3933 — OPEN: `fix: legal scanner duplicate resolver allows empty-path false PASS`. Moot by retirement.
- Related issue #3935 — OPEN: `Legal scanner resolver contract drift can report PASS for an empty scan path`. Moot by retirement (body is the named retirement trigger per #3936 body).
- `config/agents/SHARED_SOUL.md:102` — must-fire rule confirming retirement. Historical instructions are superseded.
- `docs/standards/FINAL_REPORT_VERIFICATION.md` — policy doc. Confirms retirement 2026-10-03.

### Gaps identified

- No regression test currently prevents the scanner from being reinstated (no test that asserts `scripts/legal/legal-sanity-scan.sh` is absent and no CI/pre-commit hook for it exists).
- Four related bug issues remain open and consume intake slots unnecessarily.
- `FINAL_REPORT_VERIFICATION.md` does not include a timestamped migration-complete checklist; its "Migration limits" section says "track per-repository deployed revisions" without recording which ones are confirmed done.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-10-14T via `gh issue view`):
- `#3936` — OPEN — Retire legal-sanity-scan and move identifier verification to final reports
- `#3804` — OPEN — legal-sanity-scan.sh scans NOTHING and exits 0 (fail-open gate bug)
- `#3871` — OPEN — fix(legal): reject empty resolved scan targets
- `#3933` — OPEN — legal scanner duplicate resolver allows empty-path false PASS
- `#3935` — OPEN — Legal scanner resolver contract drift can report PASS for empty scan path

**File existence** (`ls` 2026-10-14T in workspace-hub main-tree checkout):
- MISSING: `scripts/legal/legal-sanity-scan.sh` (removed from main; only in stale worktrees)
- EXISTS: `.claude/skills/coordination/legal-sanity-scan/SKILL.md`
- EXISTS: `docs/standards/FINAL_REPORT_VERIFICATION.md`
- MISSING (new — this plan creates): `scripts/enforcement/tests/test_legal_sanity_scan_retired.py`

**Gap proofs**:
```
$ grep -rn "legal.sanity" /mnt/local-analysis/workspace-hub/.pre-commit-config.yaml
(no output) → confirmed no pre-commit hook
$ grep -rn "legal.sanity" /mnt/local-analysis/workspace-hub/.github/workflows/
(no output) → confirmed no CI invocation
$ ls /mnt/local-analysis/workspace-hub/scripts/legal/legal-sanity-scan.sh
ls: cannot access ...: No such file or directory → scanner absent from main
```

**Reproduction proof:**
N/A — this plan addresses governance/cleanup work, not a runtime failure. Retirement decision is documented in `FINAL_REPORT_VERIFICATION.md` and the SOUL runtimes; the issue class is evidence/ops.

<!-- Source count: 8 distinct sources (issue body, 4 related issues, FINAL_REPORT_VERIFICATION.md, SOUL.runtime.md, .pre-commit-config.yaml grep). Minimum 3 required. ✓ -->

---

## Artifact Map

| Artifact | Path | Status |
|---|---|---|
| Regression test suite | `scripts/enforcement/tests/test_legal_sanity_scan_retired.py` | NEW |
| Migration checklist update | `docs/standards/FINAL_REPORT_VERIFICATION.md` | MODIFY (add migration-complete checklist) |
| Related issue closure | Issues #3804, #3871, #3933, #3935 | CLOSE (issue management via `gh issue close`) |

---

## Deliverable

Three deliverables:

1. **Regression test** `scripts/enforcement/tests/test_legal_sanity_scan_retired.py` — 5 tests that collectively assert the scanner is absent from every active enforcement surface in the main checkout. These tests function as a living smoke-test; any future attempt to reinstate the scanner causes one of them to fail.

2. **Migration-complete checklist** appended to `docs/standards/FINAL_REPORT_VERIFICATION.md` — a `## Migration verification (2026-10-14)` section naming each component confirmed retired, with the verification timestamp and method. This closes the "track per-repository deployed revisions" instruction in the existing "Migration limits" section.

3. **Issue closure** — close #3804, #3871, #3933, and #3935 with a comment citing #3936: *"Closing as superseded by the retirement decision in #3936 (owner decision 2026-10-03). The scanner bugs described here are moot; the scanner has been removed from main and its gates retired."*

---

## Files to Change

| File | Change |
|---|---|
| `scripts/enforcement/tests/test_legal_sanity_scan_retired.py` | Create — 5 tests asserting retirement (see TDD list) |
| `docs/standards/FINAL_REPORT_VERIFICATION.md` | Append `## Migration verification (2026-10-14)` section |
| GitHub issues #3804, #3871, #3933, #3935 | Close as superseded (comment + `gh issue close`) |

---

## TDD Test List (red → green)

All tests verify the *retired state* of the scanner — not that the scanner works, but that it is gone. Write the tests against the live checkout; each must fail if someone re-adds the scanner.

1. **`test_scanner_script_absent_from_scripts_legal`** — assert `Path("scripts/legal/legal-sanity-scan.sh").resolve()` does not exist in the repo root. Resolves against `git rev-parse --show-toplevel` to be path-stable.
2. **`test_no_pre_commit_hook_invokes_legal_sanity_scan`** — read `.pre-commit-config.yaml` and assert no hook entry or `entry:` value contains the substring `legal-sanity-scan`.
3. **`test_no_ci_workflow_invokes_legal_sanity_scan`** — glob `.github/workflows/*.yml` and assert no file contains the substring `legal-sanity-scan`.
4. **`test_skill_is_compatibility_pointer_not_executable`** — read `.claude/skills/coordination/legal-sanity-scan/SKILL.md` frontmatter; assert `type: reference` (not `executable`, `gate`, or missing) and body contains "Retired".
5. **`test_enforcement_scripts_no_live_invocation`** — glob `scripts/enforcement/*.sh` and `scripts/enforcement/*.py`; assert no file's contents contain the string `legal-sanity-scan` outside of a `#` comment line.

---

## Acceptance Criteria

- [ ] All 5 regression tests pass: `uv run pytest scripts/enforcement/tests/test_legal_sanity_scan_retired.py -xvs`.
- [ ] Issues #3804, #3871, #3933, #3935 are closed with a superseded comment referencing #3936 retirement decision.
- [ ] `docs/standards/FINAL_REPORT_VERIFICATION.md` has a `## Migration verification (2026-10-14)` section listing all confirmed retired surfaces with timestamps and method.
- [ ] `gh issue view 3936` shows no open scanner-bug issues as blockers.
- [ ] No new references to `legal-sanity-scan` as a live gate are introduced by this plan (the existing skill SKILL.md compatibility pointer is intentionally retained as a redirect).

---

## Risks and Open Questions

- **Stale worktrees**: three worktrees (`.worktrees/issue-3549-connection-plan/`, `.worktrees/issue-3549-implementation/`, `.worktrees/issue-3522-private-rule-map-plan/`) still contain `legal-sanity-scan.sh`. These are old, stale worktrees outside main-tree scope. The regression test targets the main checkout and does not fail on worktree copies. Worktree cleanup is governed by `.claude/rules/workstation-hygiene.md` and `scripts/operations/workstation-hygiene.sh`; it is deferred to a hygiene session. Document the known residue in the migration checklist.
- **Wiki paper references**: ~15 files under `knowledge/wikis/engineering/raw/papers/` contain "legal-sanity-scan" text. These are historical papers and logs (not live gate instructions). Per `FINAL_REPORT_VERIFICATION.md:Migration limits` — "historical plans and reports remain historical records." No update required; the migration checklist entry confirms this scope decision.
- **`config/ai-tools/provider-kanban.json` and `provider-work-queue.json`**: these generated files contain entries for #3804 and #3936 related scanner issues. Once #3804 is closed, the next kanban sync will remove the entry automatically. No manual update needed.
- **`enforce-no-legal-sanity-scan` as a CI gate**: the regression tests run under `pytest` locally. Promotion to a CI gate (GitHub Action) is optional follow-up; the regression tests in `scripts/enforcement/tests/` are already covered by the existing enforcement CI pipeline if one fires on that path.
