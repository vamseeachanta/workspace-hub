# Plan for #2293: fix(wiki-ingest): make nightly ingest idempotent and push-status truthful

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-15
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2293
> **Review artifacts:** scripts/review/results/2026-04-15-plan-2293-claude.md | scripts/review/results/2026-04-15-plan-2293-codex.md | scripts/review/results/2026-04-15-plan-2293-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/knowledge/wiki-ingest-cron.sh` — nightly ingest wrapper that scans changed files, runs `uv run scripts/knowledge/llm_wiki.py ingest ...`, lints the wiki, updates marker files, and then attempts commit/push with git-safe helpers.
- Found: `scripts/knowledge/llm_wiki.py` — ingest command currently emits `[WARN] Source already exists in wiki: ...` and skips unless forced, which the wrapper currently treats as an ingest error.
- Found: `scripts/knowledge/tests/test_llm_wiki.py` — existing test surface for the wiki CLI.
- Gap: duplicate-source handling is not modeled as an idempotent/non-fatal branch in the nightly wrapper.
- Gap: push-status logging in the wrapper can currently emit contradictory lines (`push failed` and `Changes committed and pushed`) in the same run.

### Standards
| Standard | Status | Source |
|---|---|---|
| Not applicable | n/a | Non-engineering knowledge-management operations issue |

### LLM Wiki pages consulted
- No specific wiki content pages needed; the issue is about the ingest pipeline behavior rather than domain page content.

### Documents consulted
- Issue #2293 body — defines two concrete problems: duplicate-source ingest noise and contradictory push-status messaging.
- `config/scheduled-tasks/schedule-tasks.yaml` — declares `wiki-ingest-nightly` and its evidence log path.
- `logs/wiki-ingest/ingest-2026-04-15.log` — shows actual duplicate-source ingest output and the contradictory push-status lines.
- `scripts/knowledge/wiki-ingest-cron.sh` — current wrapper logic, including ingest invocation, lint flow, marker updates, and push-status logging.
- `scripts/knowledge/llm_wiki.py` — current CLI behavior for duplicate existing sources.
- Related issue #2036 — nightly ingest workflow context.

### Gaps identified
- No explicit success/non-fatal classification for duplicate-known-source ingest outcomes in the nightly wrapper.
- No single-source-of-truth branch for push result reporting in `wiki-ingest-cron.sh`.
- No targeted regression coverage yet proving idempotent duplicate-source behavior in the nightly path.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-15-issue-2293-wiki-ingest-idempotent-and-push-status-truthful.md` |
| Planning index update | `docs/plans/README.md` |
| Implementation | `scripts/knowledge/wiki-ingest-cron.sh` |
| Implementation | `scripts/knowledge/llm_wiki.py` |
| Tests | `scripts/knowledge/tests/test_llm_wiki.py` |
| Tests | `tests/knowledge/test_wiki_ingest_cron.py` |
| Plan review — Claude | `scripts/review/results/2026-04-15-plan-2293-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-15-plan-2293-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-15-plan-2293-gemini.md` |

---

## Deliverable

A bounded wiki-ingest hardening change where duplicate-known sources are handled idempotently/non-fatally in the nightly flow, and push-status reporting becomes mutually exclusive and truthful.

---

## Pseudocode

```text
capture current behavior first:
    reproduce duplicate-source ingest result from llm_wiki
    reproduce nightly wrapper interpretation of that result
    identify the push-status branch that can log contradictory success/failure messages

set target behavior before coding:
    duplicate-known-source outcome in nightly ingest is non-fatal/idempotent
    real ingest failures remain failures
    push reporting uses one mutually exclusive final status branch

implement bounded changes:
    update llm_wiki ingest return/contract or wrapper interpretation so known duplicates do not count as nightly ingest errors
    update wiki-ingest-cron push handling so exactly one final push status is logged
    preserve existing lint and marker update behavior unless directly affected

verify end-to-end:
    duplicate-known-source path yields non-fatal ingest summary
    true ingest error still yields failure
    push-failed and push-succeeded lines cannot both appear in one run
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/knowledge/wiki-ingest-cron.sh` | make duplicate-known-source handling idempotent and fix contradictory push-status logging |
| Modify | `scripts/knowledge/llm_wiki.py` | only if CLI-level signal/output needs to distinguish duplicate-known-source from true ingest failure |
| Modify | `scripts/knowledge/tests/test_llm_wiki.py` | add or update duplicate-source behavior coverage if CLI contract changes |
| Create/Modify | `tests/knowledge/test_wiki_ingest_cron.py` | lock nightly wrapper duplicate-source and push-status behavior |
| Update | `docs/plans/README.md` | add this plan to the index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_wiki_ingest_duplicate_known_source_is_nonfatal` | duplicate-known-source path does not count as nightly ingest error | ingest output containing `Source already exists in wiki` | non-fatal summary / zero hard failure for that file |
| `test_wiki_ingest_true_failure_still_fails` | real ingest failure remains a failure | ingest command error output unrelated to duplicate-known-source | failure status |
| `test_wiki_ingest_push_status_is_mutually_exclusive_success` | successful push path logs success only | stubbed successful git push | success line, no warning-failed line |
| `test_wiki_ingest_push_status_is_mutually_exclusive_failure` | failed push path logs failure only | stubbed failed git push | warning-failed line, no success line |
| `test_wiki_ingest_duplicate_path_preserves_lint_and_marker_updates` | non-fatal duplicate path does not break later lint / marker steps | duplicate-known-source fixture | lint/marker branch still executes |

### TDD sequencing
1. Capture duplicate-known-source output and current nightly wrapper behavior.
2. Write failing tests for duplicate-nonfatal handling and mutually exclusive push-status branches.
3. Implement the smallest CLI/wrapper contract change needed.
4. Re-run targeted tests and verify the expected log semantics.

---

## Acceptance Criteria

- [ ] Duplicate-known-source ingest outcome is treated as idempotent/non-fatal in the nightly wrapper
- [ ] True ingest failures still fail the nightly run appropriately
- [ ] Push-status logging is mutually exclusive: one run cannot emit both failure and success terminal push messages
- [ ] `logs/wiki-ingest/ingest-*.log` semantics become less noisy and more truthful for cron-health consumption
- [ ] Targeted wiki ingest tests pass
- [ ] Plan review artifacts are posted under `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | review not run yet |
| Codex | PENDING | review not run yet |
| Gemini | PENDING | review not run yet |

**Overall result:** PENDING

Revisions made based on review:
- none yet

---

## Risks and Open Questions

- **Risk:** making duplicate-source ingest non-fatal must not accidentally hide true ingest errors.
- **Risk:** if duplicate-source semantics are changed only in the wrapper and not the CLI contract, future callers may still mis-handle the same condition.
- **Open:** is the cleanest fix to change `llm_wiki.py` exit/status semantics, or to keep the CLI unchanged and classify duplicate-known-source in the wrapper only?
- **Non-goals:** no redesign of the full wiki ingest architecture, no broader git-safe overhaul, no general cron-health redesign in this issue.

---

## Complexity: T2

**T2** — bounded wrapper/CLI behavior hardening with targeted regression tests and no broad architecture changes.