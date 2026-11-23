# Plan for digitalmodel#546: Quality Gates CLI must upload full pytest log as a workflow artifact

> **Status:** draft (r1 — proposed work, future tense throughout; awaiting adversarial review and `status:plan-review` transition)
> **Version:** r1
> **Complexity:** T1 (single function, additive change)
> **Date:** 2026-05-03
> **Issue:** [vamseeachanta/digitalmodel#546](https://github.com/vamseeachanta/digitalmodel/issues/546)
> **Triggering symptom:** Quality Gates run id `25250371336` (verified 2026-05-02): artifact `quality-gate-results` retained only the 200-line / ~8.6 KB `output_tail` JSON field, surfacing 1 of 20 failure tracebacks under `pytest --maxfail=20`.
> **Repository under change:** `digitalmodel` (NOT workspace-hub)

---

## Issue + scope

[vamseeachanta/digitalmodel#546](https://github.com/vamseeachanta/digitalmodel/issues/546) reports that when the Quality Gates job fails, only a 200-line tail of pytest output survives in the `quality-gate-results` artifact (embedded as the `output_tail` string inside `reports/quality_gates_results.json`). Triagers cannot recover the other ~19 tracebacks that `--maxfail=20` is supposed to expose. This plan proposes a minimal additive change: tee the full pytest stdout to a sibling file `reports/quality-gates-pytest-full.log` inside the QG CLI's `_execute_tests_gate`, and add that filename to the existing `actions/upload-artifact` step's `path:` list. The JSON metric stays untouched (preserves any downstream PR-comment script that reads `output_tail`). Out of scope: fixing the 244 pre-existing test failures themselves, changing `--maxfail`, enriching the JSON.

---

## Resource Intelligence

### QG CLI / validator code

- **Pytest invocation site** — [`digitalmodel/src/digitalmodel/workflows/automation/quality_gates.py:211-269`](https://github.com/vamseeachanta/digitalmodel/blob/main/src/digitalmodel/workflows/automation/quality_gates.py#L211-L269), function `_execute_tests_gate`.
  - L213: command read from config (`pytest --maxfail=1 -x` default; production override below).
  - L216-222: `subprocess.run(command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=600)` — stdout captured **after** pytest exits, no streaming. There is no `tee`/`Popen`/`pytest.main()` involvement; pytest is a pure subprocess.
  - L240: `output_tail = "\n".join(combined.splitlines()[-200:])` — the exact source of the 8.6 KB field. The full `combined` string already exists in memory at this point.
  - L266: `output_tail` is embedded inside the `metrics` dict only on the FAILURE branch (L256-269). On the PASS branch (L242-255) the full output is currently discarded.
  - L268: `errors=[result.stderr]` references `result.stderr` which was forcibly emptied at L224 (`result.stderr = ""`) — a pre-existing minor bug, **out of scope for this plan**.
- **Reports directory** — `quality_gates.py:87` resolves `self.reports_dir = self.project_root / self.config["settings"]["paths"]["reports_dir"]` and `quality_gates.py:88` calls `mkdir(parents=True, exist_ok=True)` in `__init__`. The directory therefore exists **before** `_execute_tests_gate` runs, so writing `self.reports_dir / "quality-gates-pytest-full.log"` is safe at any point inside that function.
- **CLI wrapper** — [`digitalmodel/src/digitalmodel/workflows/automation/quality_gates_cli.py:45-93`](https://github.com/vamseeachanta/digitalmodel/blob/main/src/digitalmodel/workflows/automation/quality_gates_cli.py#L45-L93). The CLI just calls `validator.execute_all_gates()`; no pytest handling here. **No CLI change required** — the patch lives entirely in `quality_gates.py`.

### Pytest command actually used in CI

From `digitalmodel/.claude/quality-gates.yaml:10`:

```
python -m pytest --maxfail=20 -rfE -p no:asyncio -p no:randomly -p no:sugar -p no:capture --no-header -q --tb=line --cov=src --cov-report=json
```

Salient flags for log-size estimation:
- `--tb=line` — one-line tracebacks (much terser than `--tb=long`).
- `-q` (quiet), `--no-header` — terse summary.
- `-rfE` — display short summary for failures and errors at end.
- No `-v`, no `-n auto` (xdist NOT enabled in production QG config) — eliminates the xdist stdout-interleaving concern in the symptom path. (xdist remains an adversarial concern if `command:` is later reconfigured.)
- `-p no:capture` disables pytest's capture plugin; live test stdout flows through the subprocess pipe.

### Workflow YAML

- File: [`digitalmodel/.github/workflows/quality-gates.yml`](https://github.com/vamseeachanta/digitalmodel/blob/main/.github/workflows/quality-gates.yml).
- L39-40: `mkdir -p reports` runs **before** pytest, so the directory the CLI writes into is also writable to the workflow runner.
- L45-48: invokes `python -m digitalmodel.workflows.automation.quality_gates_cli check --json`.
- L50-59: existing `actions/upload-artifact@v4` step, name `quality-gate-results`, `path:` is a multi-line YAML list:
  ```yaml
  path: |
    reports/quality_gates_results.json
    reports/bandit_report.json
    coverage.json
  ```
  Adding `reports/quality-gates-pytest-full.log` as a fourth line is the minimum-impact change; missing files do not fail the upload (`actions/upload-artifact@v4` warns but exits 0 by default for missing-but-listed files).
- The PR-comment script at L71-118 reads only `reports/quality_gates_results.json` and does NOT touch `output_tail`, so JSON-shape changes are not coupled to PR-comment rendering.

### Log size anchor

- Local repro at `/tmp/qg-repro-60d59565.log`: **12,482 lines / 1,398,149 bytes (≈1.3 MB)** captured 2026-05-02 against digitalmodel SHA `60d59565`.
- The local log was likely captured with default-verbosity pytest. CI's `-q --tb=line --no-header` produces materially smaller output per failure. Realistic CI estimate: **0.3 - 1.5 MB** on a 244-failure run, well below GitHub's 2 GB per-artifact ceiling and the workflow's typical aggregate budget.

### Edge cases verified

- **mkdir-before-pytest:** confirmed via `quality_gates.py:88` (validator init) and `quality-gates.yml:40` (workflow step) — both create `reports/` before `_execute_tests_gate` runs.
- **SIGKILL / timeout:** `subprocess.run(..., timeout=600)` raises `TimeoutExpired` at L270; whatever was already written to the log file by a streaming approach would survive. The simpler in-memory approach (write `combined` after `subprocess.run` returns) loses output on timeout — addressed in Approach.
- **Existing log conflict:** `grep -r "quality-gates-pytest-full" digitalmodel/` returns nothing; no naming collision.
- **xdist:** not active in production QG config; remains a future-work adversarial concern (see Adversarial section).
- **Existing unit tests:** [`tests/workflows/automation/test_quality_gates.py:160-180`](https://github.com/vamseeachanta/digitalmodel/blob/main/tests/workflows/automation/test_quality_gates.py#L160-L180) uses `@patch("subprocess.run")` for `test_execute_tests_gate_pass` and `_failure`. Per memory `feedback_mock_vs_live_invocation_divergence.md`, the new TDD test must include at least one **non-mocked** branch that asserts on a real file written to disk (with a tiny stub command), in addition to the mocked branches.

### digitalmodel `origin/main` SHA (verified 2026-05-02)

```
2dfa61e6192183ad59fd1afc2e2288d1286287b8
```

(Verification command: `gh api repos/vamseeachanta/digitalmodel/commits/main --jq .sha`.)

---

## Preflight (mandatory before any code changes)

Before any code is touched, the implementing agent will:

1. **Hermes preflight** (per workspace-hub memory `feedback_hermes_active_preflight_check.md`):
   ```bash
   pgrep -af 'git (rebase|stash push|commit|merge|reset|checkout)' | grep -v grep || echo "OK: no Hermes activity"
   ```
   If Hermes is active on the digitalmodel checkout, switch to a worktree+feature-branch lane.

2. **Sync and pin base** (digitalmodel repo, not workspace-hub):
   ```bash
   cd /mnt/local-analysis/workspace-hub/digitalmodel
   git fetch origin main
   git switch main
   git pull --ff-only origin main
   git rev-parse HEAD  # expected ancestor: 2dfa61e6192183ad59fd1afc2e2288d1286287b8 or newer
   git merge-base --is-ancestor 2dfa61e6192183ad59fd1afc2e2288d1286287b8 HEAD || { echo "ABORT: base predates pinned SHA"; exit 1; }
   ```

3. **Branch:**
   ```bash
   git switch -c fix/546-qg-cli-full-log-artifact
   ```

4. **No-op verification** that `_execute_tests_gate` matches the line numbers cited above (they may shift if `origin/main` advanced):
   ```bash
   grep -n "_execute_tests_gate\|output_tail\|subprocess.run" src/digitalmodel/workflows/automation/quality_gates.py | head -10
   ```

If any preflight step fails, abort and report state in [vamseeachanta/digitalmodel#546](https://github.com/vamseeachanta/digitalmodel/issues/546) instead of editing.

---

## Approach

Two coupled changes, both in `digitalmodel`:

### Change 1 — `digitalmodel/src/digitalmodel/workflows/automation/quality_gates.py`

In `_execute_tests_gate` (around L211-269), after `subprocess.run` returns and `combined` is constructed (L229), write the full combined output to `self.reports_dir / "quality-gates-pytest-full.log"` **on every branch** (PASS, FAILURE, and inside the TimeoutExpired handler).

Pseudo-diff:

```python
# After L229 (combined = ...) and before the regex parsing at L230:
full_log_path = self.reports_dir / "quality-gates-pytest-full.log"
try:
    full_log_path.write_text(combined, encoding="utf-8", errors="replace")
    logger.info(f"Pytest full log written to {full_log_path} ({len(combined)} bytes)")
except OSError as e:
    logger.warning(f"Could not write pytest full log: {e}")  # non-fatal; gate result still produced
```

Two refinements:

1. **Timeout branch (L270-276)**: `TimeoutExpired.stdout` (and `.stderr` if separate) holds whatever pytest emitted before SIGKILL. Replicate the write inside the `except subprocess.TimeoutExpired as e:` block using `e.stdout` (decoded if bytes). This satisfies the "killed mid-run" edge case without switching to a streaming `Popen` design.
2. **Filename is a constant**, not a config-driven value. Hard-coded `"quality-gates-pytest-full.log"` keeps the workflow YAML reference stable and matches the issue body literally. If a future config knob is wanted, it can be added without breaking this contract.

Estimated diff: **~10 lines added, 0 modified, 0 deleted** in `quality_gates.py`. No imports change.

### Change 2 — `digitalmodel/.github/workflows/quality-gates.yml`

Append one line to the existing `actions/upload-artifact` step's `path:` (L55-58):

```yaml
      - name: Upload quality gate results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: quality-gate-results
          path: |
            reports/quality_gates_results.json
            reports/bandit_report.json
            reports/quality-gates-pytest-full.log   # NEW
            coverage.json
          retention-days: 30
```

Estimated diff: **+1 line** in `quality-gates.yml`. No new artifact upload step needed (reuses existing `name: quality-gate-results`); triagers continue to download a single artifact.

### Total proposed diff size

**~11 lines added, 0 deleted across 2 files.** No public API change. No config schema change.

---

## TDD test specification

Two tests will be added to [`digitalmodel/tests/workflows/automation/test_quality_gates.py`](https://github.com/vamseeachanta/digitalmodel/blob/main/tests/workflows/automation/test_quality_gates.py).

### Test 1 (mocked path, unit test) — `test_execute_tests_gate_writes_full_log`

```python
@patch("subprocess.run")
def test_execute_tests_gate_writes_full_log(self, mock_run, validator, tmp_path):
    """Tests gate must write reports/quality-gates-pytest-full.log on every run."""
    fake_output = ("FAILED tests/x.py::test_a - AssertionError\n" * 1000)  # ~50 KB
    mock_run.return_value = MagicMock(returncode=1, stdout=fake_output, stderr="")
    validator.reports_dir = tmp_path  # redirect writes

    result = validator._execute_tests_gate({"command": "pytest --maxfail=20"})

    log_path = tmp_path / "quality-gates-pytest-full.log"
    assert log_path.exists(), "full pytest log must be written"
    contents = log_path.read_text(encoding="utf-8")
    assert "FAILED tests/x.py::test_a" in contents
    assert len(contents) >= 50_000, "full log must contain entire pytest output, not truncated tail"
    # Existing JSON metric stays intact
    assert "output_tail" in result.metrics
```

This test will fail on `origin/main` (no log written today) and pass after Change 1 lands.

### Test 2 (live invocation, addresses memory `feedback_mock_vs_live_invocation_divergence.md`) — `test_execute_tests_gate_writes_full_log_live`

```python
def test_execute_tests_gate_writes_full_log_live(self, validator, tmp_path):
    """Live (un-mocked) subprocess invocation: tiny shell command stands in for pytest."""
    validator.reports_dir = tmp_path
    # Use 'printf' (cross-platform via python -c) to produce known stdout without pytest dep.
    cmd = 'python -c "import sys;sys.stdout.write(\\"line\\\\n\\"*100)"'

    validator._execute_tests_gate({"command": cmd})

    log_path = tmp_path / "quality-gates-pytest-full.log"
    assert log_path.exists()
    assert log_path.read_text().count("line\n") == 100
```

This proves the file gets written when `subprocess.run` actually executes (not just when its return value is mocked).

### Test 3 (timeout branch) — `test_execute_tests_gate_writes_full_log_on_timeout`

```python
@patch("subprocess.run")
def test_execute_tests_gate_writes_full_log_on_timeout(self, mock_run, validator, tmp_path):
    """Even on TimeoutExpired, partial pytest stdout must be written to the full log."""
    from subprocess import TimeoutExpired
    mock_run.side_effect = TimeoutExpired(cmd="pytest", timeout=600, output="partial output before kill\n")
    validator.reports_dir = tmp_path

    result = validator._execute_tests_gate({"command": "pytest --maxfail=20"})

    log_path = tmp_path / "quality-gates-pytest-full.log"
    assert log_path.exists()
    assert "partial output before kill" in log_path.read_text()
    assert result.status == GateStatus.ERROR
```

All three tests fail before Change 1; all pass after.

---

## Verification

### Local

```bash
cd /mnt/local-analysis/workspace-hub/digitalmodel
PYTHONPATH=src uv run python -m pytest tests/workflows/automation/test_quality_gates.py -k full_log -v
# All three new tests pass.

# End-to-end CLI sanity check (uses repo's real config):
PYTHONPATH=src uv run python -m digitalmodel.workflows.automation.quality_gates_cli check --json > /tmp/qg-stdout.json 2>&1 || true
ls -la reports/quality-gates-pytest-full.log reports/quality_gates_results.json
wc -c reports/quality-gates-pytest-full.log  # expect > 50 KB on a real run
python -c "import json; d=json.load(open('reports/quality_gates_results.json')); print('output_tail present:', any('output_tail' in r.get('metrics',{}) for r in d['results']))"
# Both files exist; output_tail still present in JSON.
```

### CI

After pushing the branch and opening a PR against digitalmodel:

```bash
gh run list --workflow=quality-gates.yml --branch fix/546-qg-cli-full-log-artifact --limit 1
gh run download <run-id> --name quality-gate-results --dir /tmp/qg-artifact-test
ls -la /tmp/qg-artifact-test/
# Expect: quality_gates_results.json, bandit_report.json, coverage.json, quality-gates-pytest-full.log (NEW)
wc -c /tmp/qg-artifact-test/quality-gates-pytest-full.log
# Expect > 100 KB on a run that fails.
grep -c "^FAILED " /tmp/qg-artifact-test/quality-gates-pytest-full.log
# Expect ~ number of failed tests reported in JSON metric.
```

---

## Adversarial counter-arguments

Per workspace-hub memory `feedback_adversarial_review_stance.md`, this section forces defect-hunting on the proposal above.

1. **xdist stdout interleaving (real)** — *Verdict: not a defect for this plan.* Production QG config (`.claude/quality-gates.yaml:10`) does NOT include `-n auto`. If a future operator adds xdist, the full log becomes interleaved-by-worker but is still strictly more useful than a 200-line tail. Mitigation: the log is line-buffered raw subprocess output, so interleaving is at most line-granular, not character-granular. **No code change required now**; document the caveat in the file header comment when Change 1 lands.

2. **Artifact storage cost** — A failing PR run today produces a ~30 KB JSON artifact; this plan adds 0.3-1.5 MB per run for 30 days (default retention). Worst case: 100 PR runs/month × 1.5 MB × 30 days retention = ~4.5 GB peak storage. GitHub's free tier is 500 MB-2 GB depending on plan. *Mitigation if storage pressure emerges:* drop retention on this artifact specifically to 7 days, or split it into a separate `actions/upload-artifact` step with its own retention. **Acceptable risk for v1**; revisit if billing alerts fire.

3. **Simpler alternatives evaluated and rejected:**
   - *Just remove `--maxfail=20`*: defeats the maxfail-budget intent and explodes runtime on broken trees. Rejected.
   - *Just drop the JSON-wrap and dump full output to JSON*: would balloon `quality_gates_results.json` to MB-scale, breaking the PR-comment script's `JSON.parse` (workflow `quality-gates.yml:79`) and any downstream metric consumer. Rejected per issue body's explicit "Don't change the JSON metric — keep both".
   - *Tee from the workflow YAML instead of CLI*: would require restructuring the `Run Quality Gates` step into raw bash + redirection, but the CLI calls pytest from inside Python — there is no shell-level tee point. Rejected.

4. **Local invocation of CLI** — When run outside CI (e.g., a developer's laptop), `self.reports_dir` resolves to `<cwd>/reports/` (per `quality_gates.py:87`). The new file lands next to existing `reports/quality_gates_results.json` — same surface, no surprise location. Local repro at `/tmp/qg-repro-60d59565.log` already used the same convention. **Acceptable.**

5. **Is the JSON `output_tail` still useful?** — Arguably yes: it is the only field rendered inline in CI logs and could conceivably be consumed by a future PR-comment template. Keeping it costs ~8.6 KB per run. The issue body explicitly mandates "keep both". **Keep.**

6. **Mock-vs-live divergence (memory `feedback_mock_vs_live_invocation_divergence.md`)** — The existing test suite uses `@patch("subprocess.run")` heavily (`test_quality_gates.py:160-180`, `:171-180`, `:245`, `:265`, `:300`, `:474`). A pure mock-only test could pass while the live `subprocess.run(...).stdout` attribute access fails on real `CompletedProcess` objects (it doesn't, but the principle applies). **Mitigation:** Test 2 above is intentionally non-mocked.

7. **`combined.splitlines()[-200:]` regression risk** — The new write happens BEFORE the existing splitlines/regex parsing. If `combined` is `None` (impossible given `text=True` + `subprocess.PIPE`, but defensively), `write_text(combined)` would TypeError. *Mitigation:* the existing code at L229 already does `(result.stdout or "")` — the patch will reuse that fallback string.

8. **What's the strongest counter-argument?** *(self-pick if forced to challenge)*: **The whole patch may be unnecessary if the right answer is to upload `reports/` recursively.** `actions/upload-artifact@v4` accepts a directory path. If the workflow already did `path: reports/` (instead of three named files), any new file the CLI writes would be auto-uploaded with zero workflow-YAML changes. Counter-counter: it would also auto-upload coverage HTML, cache files, etc. — bloat. The proposed list-the-file approach is more deliberate and matches the issue body's wording. **Plan stands**, but reviewer should weigh whether to widen `path:` instead, as a follow-up consideration.

---

## Out of scope (explicit)

- **Fixing the 244 pre-existing test failures** found in the local repro — that is a separate triage effort tracked elsewhere.
- **Changing `--maxfail=20`** or any other pytest flag in `.claude/quality-gates.yaml`.
- **Enriching the JSON metric** (e.g., adding a `full_log_path` field). Trivial follow-up but not required by the issue.
- **Switching to streaming `Popen` for live tail** — the in-memory `combined` string approach is simpler and sufficient given the 600 s timeout budget; revisit only if pytest runs grow past memory comfort.
- **Splitting the artifact upload** into a separate `actions/upload-artifact` step with shorter retention — deferred to storage-cost trigger.
- **Fixing the `result.stderr = ""` line at `quality_gates.py:224`** — pre-existing minor bug, file a separate issue if needed.
- **Workspace-hub issues [#2609](https://github.com/vamseeachanta/workspace-hub/issues/2609), [#2585](https://github.com/vamseeachanta/workspace-hub/issues/2585), [#2580](https://github.com/vamseeachanta/workspace-hub/issues/2580)** — explicitly out of scope per task brief.

---

## Acceptance criteria

Concrete checkboxes derived from the [vamseeachanta/digitalmodel#546](https://github.com/vamseeachanta/digitalmodel/issues/546) body:

- [ ] `_execute_tests_gate` writes `reports/quality-gates-pytest-full.log` containing the complete combined stdout+stderr of the pytest invocation on every branch (PASS, FAILURE, TimeoutExpired).
- [ ] `reports/quality_gates_results.json` continues to include `metrics.output_tail` exactly as today (no JSON shape change).
- [ ] `digitalmodel/.github/workflows/quality-gates.yml` `actions/upload-artifact@v4` step lists `reports/quality-gates-pytest-full.log` in `path:` so the file is uploaded to the existing `quality-gate-results` artifact.
- [ ] Three new unit tests (`_writes_full_log`, `_writes_full_log_live`, `_writes_full_log_on_timeout`) added to `tests/workflows/automation/test_quality_gates.py`; all three pass after the patch and fail before it.
- [ ] Local repro: running the CLI locally produces both files in `reports/`.
- [ ] CI verification: a re-run of the Quality Gates workflow on the patch branch produces an artifact `quality-gate-results` whose download contains `quality-gates-pytest-full.log` with size > 50 KB on a failing run, and recovers the full set of `--maxfail=20` tracebacks.
- [ ] No regression in `test_execute_tests_gate_pass` and `test_execute_tests_gate_failure` (existing tests still pass unchanged).
- [ ] PR description references [vamseeachanta/digitalmodel#546](https://github.com/vamseeachanta/digitalmodel/issues/546) and links to a sample artifact download as proof of recovery.

---

## Approval gate

This is a draft plan. **The user owns the `status:plan-approved` transition.** No self-approval, no pre-authorization of downstream agents (per workspace-hub memory `feedback_never_offer_to_self_label_plan_approved.md`). Adversarial review must occur first.
