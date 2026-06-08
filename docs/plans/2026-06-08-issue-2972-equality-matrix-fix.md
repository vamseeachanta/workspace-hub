# Plan for #2972: fix silently-broken equality-matrix + fail-loud cron

> **Status:** draft → plan-review
> **Complexity:** T1
> **Date:** 2026-06-08
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2972
> **Parent epic:** https://github.com/vamseeachanta/workspace-hub/issues/2967
> **Client:** N/A
> **Coordinates with:** #2894 (substrate revival, BLOCKS #2887 family)

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/readiness/build-equality-matrix.py` — `import yaml` at line 22, **no PEP-723 header**. Run-line in docstring (line 11) says `uv run python ...` — that mode does NOT resolve third-party deps.
- Found: `scripts/ai/generate-agent-radar.py` — carries the working pattern: PEP-723 header (`# /// script` … `dependencies = ["pyyaml"]`) and its cron uses `uv run --script`. **This is the fix template.**
- Found: cron line (weekly, Mondays 04:30): `... && uv run python scripts/readiness/build-equality-matrix.py >> logs/quality/equality-$(date).log 2>&1`.

### Gaps identified
- `build-equality-matrix.py` has no dependency declaration, so `uv run python` (no project env with pyyaml) raises `ModuleNotFoundError: yaml`.
- The cron job's failure has **no notification path** — output appends to a dated log nobody reads; no MAILTO, no alert.

### Evidence (embedded verification)

**Reproduction proof** (2026-06-08, exact cron invocation):
```
$ cd /mnt/local-analysis/workspace-hub && uv run python scripts/readiness/build-equality-matrix.py; echo EXIT=$?
ModuleNotFoundError: No module named 'yaml'   (Traceback at line 22)
EXIT=1
```
- Failure mode matches issue claim: YES (import failure). Correction to original phrasing: exit is **1**, not 0; the silence is the missing notification path, not a masked exit.

**Staleness proof** (`ls -t docs/reports/*equality*.html`):
- Last committed: `docs/reports/2026-05-31-machine-equality-matrix.html` — 8 days stale; weekly cron has fired (and failed) every Monday since.

**Working-pattern proof** (`head -5 scripts/ai/generate-agent-radar.py`):
```
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
```

Source count: 4 (issue body + 3 file/command findings). ✔

---

## Deliverable
The weekly machine-equality matrix builds clean on every active machine, regenerates committed evidence, and any future build failure raises a loud notification instead of rotting in an unread log.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/readiness/build-equality-matrix.py` | add PEP-723 header (`dependencies = ["pyyaml"]`); update docstring run-line to `uv run --script` |
| Create | `scripts/readiness/equality-matrix-cron.sh` | wrapper: run collect + build; on non-zero, emit a loud notification (existing notifications surface under `logs/notifications/`) and exit non-zero |
| Modify | crontab (via documented procedure, not auto-edit — `crontab:*` is deny-listed) | point the weekly line at the new wrapper; provide the exact line in the PR for the user to apply |
| Create | `tests/readiness/test_build_equality_matrix.py` | TDD: import-resolves, builds matrix from fixture state, exits 0 on success / non-zero on malformed input |
| Update | `docs/plans/README.md` | index this plan |

---

## TDD Test List

| Test name | What it verifies | Expected |
|---|---|---|
| test_module_imports_under_uv_script | `uv run --script build-equality-matrix.py --help` resolves pyyaml | exit 0, no ModuleNotFoundError |
| test_builds_matrix_from_fixture_state | given 2 fixture `equality-*.yaml`, produces HTML + verdicts | HTML contains both machine columns |
| test_cron_wrapper_fails_loud | wrapper given a forced build failure | non-zero exit + a notification record written |
| test_cron_wrapper_success_quiet | wrapper on healthy build | exit 0, evidence file produced |

---

## Acceptance Criteria
- [ ] `uv run --script scripts/readiness/build-equality-matrix.py` builds clean on ace-linux-1 AND ace-linux-2 (no ModuleNotFoundError).
- [ ] Fresh `docs/reports/<date>-machine-equality-matrix.html` regenerated and committed with current 2-machine evidence.
- [ ] Cron wrapper exits non-zero AND writes a notification record on failure (proven by a forced-failure test).
- [ ] Exact replacement crontab line provided in the PR for the user to apply (no auto crontab edit — deny-listed).
- [ ] `uv run pytest tests/readiness/test_build_equality_matrix.py -v` passes.

---

## Adversarial Review Summary
<!-- Architecture-level review already done by Codex on the parent epic #2967.
     T1 slice: 1-provider plan review (Codex) sufficient per AGENTS.md scale rule. To run after user nods on scope. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Codex | pending | T1 plan-review to dispatch on approval |

---

## Risks and Open Questions
- **Risk:** ace-linux-2 may resolve `uv`/pyyaml differently (different PATH); the `--script` mode self-contains deps, which removes the project-env assumption — mitigation built into the fix.
- **Open (user):** prefer the loud-failure notification via the existing `logs/notifications/` JSONL surface, or also push to Telegram (ties into epic F4)? Default: JSONL surface only for this T1 slice; Telegram escalation deferred to F4.
- **Coordination:** confirm whether to land this under #2972 or fold into #2894 (substrate revival). Recommendation: land here (narrow, testable), reference from #2894.

## Complexity: T1
**T1** — single-file dependency-declaration fix + a thin wrapper + tests; no new subsystem. Observability-first slice that unblocks measurement before any reconciler writes (per epic rollout order).
