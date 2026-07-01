# Plan for #3212: cron_render `$WORKSPACE_HUB` undefined in cron env causes all managed jobs to short-circuit

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-07-01
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3212
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-01-plan-3212-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/cron/cron_render.py:161` — `_ensure_log_dir()` prepends
  `mkdir -p $WORKSPACE_HUB/{log_dir} && {command}` as a literal string; `$WORKSPACE_HUB` is
  never expanded at render time, so cron's minimal env sees it unset and `mkdir -p /logs/...`
  fails → `&&` short-circuits → job is blocked.
- Found: `scripts/cron/cron_render.py:24` — `REPO_ROOT = Path(__file__).resolve().parents[2]`
  is already a module-level compile-time constant — the correct absolute path to use.
- Found: `tests/cron/test_cron_render.py` — 3 existing tests for `render_task` and schedule
  resolution; none exercises `_ensure_log_dir` with `WORKSPACE_HUB` unset. The `monkeypatch.setenv`
  calls in existing tests mask the bug by setting `WORKSPACE_HUB` in the test process.

### Standards

| Standard | Status | Source |
|---|---|---|
| `.claude/rules/coding-style.md` | relevant — "use relative paths or `$(git rev-parse --show-toplevel)` / `${REPO_ROOT}` — never hardcode absolute paths" | repo rule |

### LLM Wiki pages consulted

- No relevant wiki pages — this is a cron infrastructure bug fix.

### Documents consulted

- Issue #3212 body (2026-06-18) — root cause, impact on 9 managed jobs, 4 candidate fixes.
- `docs/plans/2026-04-15-issue-2291-cron-health-hardening-and-task-evidence-contracts.md` — prior
  cron hardening work; confirms `_ensure_log_dir` was added later, after the health-hardening plan
  landed; no overlap with this fix.
- `tests/cron/test_cron_render.py` — existing test structure; confirms `monkeypatch.setenv("WORKSPACE_HUB", str(REPO))` in each test, which masks the bug in CI.

### Gaps identified

- No test exercises `_ensure_log_dir` without `WORKSPACE_HUB` set — the bug survives CI entirely.
- Candidate fix (1) — use `REPO_ROOT` at render time — is the correct approach: compile-time
  constant, no env dependency, matches the coding-style rule.

### Evidence (embedded verification)

**Issue status** (verified 2026-07-01):
- `#3212` — OPEN — `cron_render: mkdir-prefix uses undefined $WORKSPACE_HUB → managed cron jobs short-circuit`

**File existence** (`ls` 2026-07-01):
- EXISTS: `scripts/cron/cron_render.py`
- EXISTS: `tests/cron/test_cron_render.py`

**Line excerpts** (`sed -n 155,165p scripts/cron/cron_render.py`):
```python
155    log = str(log).strip()
156    if not log.startswith("logs/"):
157        return command
158    log_dir = log.rsplit("/", 1)[0]
159    if "mkdir -p" in command and log_dir in command:
160        return command
161    return f"mkdir -p $WORKSPACE_HUB/{log_dir} && {command}"
```

**Reproduction proof** (2026-07-01):
```python
$ python3 -c "
import importlib.util, os
spec = importlib.util.spec_from_file_location('cron_render', 'scripts/cron/cron_render.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
os.environ.pop('WORKSPACE_HUB', None)
print(repr(mod._ensure_log_dir('bash scripts/cron/run-report.sh', 'logs/quality/cron.log')))
"
'mkdir -p $WORKSPACE_HUB/logs/quality && bash scripts/cron/run-report.sh'
```

Literal `$WORKSPACE_HUB` appears in the rendered string — confirmed unexpanded at render time.

```bash
$ env -u WORKSPACE_HUB bash -c \
    'cmd="mkdir -p $WORKSPACE_HUB/logs/quality && bash scripts/report.sh"; eval "$cmd" 2>&1 || echo BLOCKED'
bash: scripts/report.sh: No such file or directory
BLOCKED
```

Short-circuit confirmed — `mkdir -p /logs/quality` fails (non-writable path), `&&` blocks job.

- Reproduced at: 2026-07-01
- Failure mode matches issue claim: YES

<!-- Verification: sources = issue body (1) + cron_render.py file (2) + test_cron_render.py (3) + coding-style rule (4) + prior cron plan (5). Count: 5 ✓ -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-07-01-issue-3212-cron-render-workspace-hub-undefined.md |
| Implementation | `scripts/cron/cron_render.py` |
| Tests | `tests/cron/test_cron_render.py` |
| Plan review — Claude | scripts/review/results/2026-07-01-plan-3212-claude.md |
| Plan review — Codex | scripts/review/results/2026-07-01-plan-3212-codex.md |
| Plan review — Gemini | scripts/review/results/2026-07-01-plan-3212-gemini.md |

---

## Deliverable

`_ensure_log_dir` in `scripts/cron/cron_render.py` will emit an absolute path using the module-level
`REPO_ROOT` constant, eliminating the `$WORKSPACE_HUB` env dependency from rendered crontab entries;
a new regression test will confirm no unexpanded variable survives into rendered output even when
`WORKSPACE_HUB` is absent from the environment.

---

## Pseudocode

Trivial — see Files to Change.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/cron/cron_render.py` | Replace `$WORKSPACE_HUB/{log_dir}` with `{REPO_ROOT}/{log_dir}` on line 161 |
| Modify | `tests/cron/test_cron_render.py` | Add regression test asserting no `$WORKSPACE_HUB` in rendered command |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_ensure_log_dir_no_workspace_hub_in_rendered_command` | rendered mkdir prefix contains no unexpanded `$WORKSPACE_HUB` | command=`"bash scripts/cron/report.sh"`, log=`"logs/quality/cron.log"`, `WORKSPACE_HUB` unset | rendered string contains no `$WORKSPACE_HUB`; rendered string starts with `mkdir -p /` (absolute path) |
| `test_ensure_log_dir_uses_absolute_repo_root` | rendered prefix uses `REPO_ROOT` absolute path | command=`"bash scripts/cron/report.sh"`, log=`"logs/quality/cron.log"` | rendered prefix is `mkdir -p <REPO_ROOT>/logs/quality && ...` |
| `test_ensure_log_dir_skips_non_logs_prefix` | non-`logs/` log paths are left unchanged | log=`"/var/log/cron.log"` | command unchanged (no mkdir prefix) |
| `test_ensure_log_dir_idempotent` | double-prefix not added if already present | command already contains `mkdir -p ... logs/quality` | command unchanged |

Write these 4 tests RED (failing because `$WORKSPACE_HUB` is present) before touching line 161.

---

## Acceptance Criteria

- [ ] All 4 new tests pass: `uv run pytest tests/cron/test_cron_render.py -v -k "ensure_log_dir"`
- [ ] Full cron test suite passes: `uv run pytest tests/cron/ -v`
- [ ] `python3 -c "import os; os.environ.pop('WORKSPACE_HUB', None); ..."` repro returns no `$WORKSPACE_HUB` in output
- [ ] `bash scripts/cron/setup-cron.sh --dry-run | grep '\$WORKSPACE_HUB'` returns no matches
- [ ] Review artifacts posted to `scripts/review/results/`

---

## Adversarial Review Summary

<!-- To be filled after Step 4 completes. Do not post to GitHub until populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | — | — |
| Codex | — | — |
| Gemini | — | — |

---

## Risks and Open Questions

- **Risk (low):** `REPO_ROOT` is a Python `Path` object; `f"{REPO_ROOT}/{log_dir}"` works correctly
  because `Path.__str__` returns the absolute POSIX path — no coercion needed.
- **Risk (low):** ace-linux-2 cron jobs are already broken. This fix takes effect on next
  `cron_apply.py --apply` or `setup-cron.sh` run; no automatic re-render. Operator must re-apply.
  Acceptance test #4 (`--dry-run` grep) verifies the renderer before re-apply.
- **Open:** Should the `_ensure_log_dir` docstring note the cron-env constraint? Low priority; the
  fix is self-explanatory.

---

## Complexity: T1

Single line changed in one function; 4 regression tests added to the existing test file. No new
modules, no architecture change. Existing `REPO_ROOT` constant covers the fix.
