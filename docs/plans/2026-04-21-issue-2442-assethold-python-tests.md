# Plan for #2442: assethold CI — python-tests.yml never green since 2025-09-28 (YAML parse + deprecated actions + fork-transfer artifacts)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-21
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2442
> **Parent meta-issue:** https://github.com/vamseeachanta/workspace-hub/issues/2424
> **Review artifacts:** scripts/review/results/2026-04-21-plan-2442-claude.md | ...-codex.md | ...-gemini.md
> **Note:** `status:plan-approved` was pre-applied at handoff generation before any plan existed; orchestrator rolled the label back to `status:plan-review` this session (governance comment 4290738146). This plan is the canonical artifact and is in Wave 2 re-review after Wave 1 (3× MAJOR) revisions; user re-approval in-thread is required before execution.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `assethold/.github/workflows/python-tests.yml` (432+ lines) — comprehensive matrix workflow (Python 3.9–3.12 × ubuntu/windows/macos), test + integration + financial-data + quality-gate jobs. YAML parse fails at startup — 0 jobs register, 0s duration.
- Found: `assethold/.github/workflows/docs.yml` (35 lines, much smaller). YAML is structurally valid. Also fails with 0s/zero-jobs. Already has `workflow_dispatch` trigger.
- Found: `assethold/requirements-consolidated.txt` exists; `assethold/requirements.txt` does NOT exist. Workflow references `requirements.txt` at 3 sites (lines 74, 222, 269).
- Found: `assethold/pyproject.toml` — setuptools-based (not pure uv), dependencies include sibling repo `assetutilities` (git-local dep implication for CI install).
- Found: `assethold/tests/` — full pytest tree: `unit/`, `integration/`, `net_lease/`, `options/`, `portfolio/`, `contracts/`, plus 7 top-level `test_*.py` files. Tests exist; discovery path is intact.
- Found: `assethold/uv.lock` — lockfile present.
- Gap: workflow refers to non-existent `requirements.txt`. `requirements-consolidated.txt` exists but self-declares "now replaced by pyproject.toml — Kept for reference only" (verified 2026-04-21, file header). Install path must resolve `assetutilities` sibling dep and install the project from `pyproject.toml` — but must use `uv pip install --system` (NOT `uv sync --frozen`) to preserve the existing `--system` install pattern that all downstream `pytest`/`mypy`/`flake8` commands depend on (they run without `uv run` prefix).

### Standards
Not applicable — this is an infrastructure/CI-health remediation, not a domain engineering deliverable.

### LLM Wiki pages consulted
No relevant wiki pages — CI health is repo-hygiene work, not domain knowledge.

### Documents consulted
- Issue #2442 body — read-only investigation dispatched 2026-04-21 with 6 precise fix sites and confirmation that fork-transfer (samdansk2 → vamseeachanta) is NOT contributing.
- Parent meta-issue #2424 — "6-of-7 repos red across ecosystem"; this is the HIGH PRIORITY / deepest-debt entry (never-green for 7 months vs the sibling repos' 4-day red windows).
- Memory `project_assethold_ownership_transfer.md` — transfer samdansk2 → vamseeachanta completed; local origin may be stale. Verified: `git remote -v` on `/mnt/local-analysis/workspace-hub/assethold/` points at `vamseeachanta/assethold.git` (canonical).
- `gh run list --repo vamseeachanta/assethold --branch main --limit 15` (2026-04-21) — confirmed 15/15 red on both workflows, all 0s duration (startup rejection pattern).

### Gaps identified
- No existing CI-green evidence for `python-tests.yml` — this workflow has never been green on main since first run 2025-09-28.
- No baseline pytest run recorded in CI — need phase-1 minimal-smoke workflow validation before attempting matrix-wide green.
- `assetutilities` dependency resolution in CI — `pyproject.toml` declares `[tool.uv.sources] assetutilities = { path = "../assetutilities" }`, which does not exist on a hosted GitHub Actions runner. Resolved in Phase 2 fix list below (add `actions/checkout` step for `vamseeachanta/assetutilities` into `../assetutilities` — Option M1 — to match local dev layout referenced by `pyproject.toml`).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-21 via `gh issue view 2442 --json state,labels`):
- `#2442` — OPEN — labels: `priority:high`, `cat:infrastructure`, `status:plan-review` (approval label was pre-applied before any artifact existed; rolled back to `status:plan-review` by orchestrator this session per governance comment 4290738146)
- `#2424` — parent meta-issue (referenced, not re-fetched this session)

**File existence** (`ls` 2026-04-21):
- EXISTS: `/mnt/local-analysis/workspace-hub/assethold/.github/workflows/python-tests.yml`
- EXISTS: `/mnt/local-analysis/workspace-hub/assethold/.github/workflows/docs.yml`
- EXISTS: `/mnt/local-analysis/workspace-hub/assethold/requirements-consolidated.txt`
- MISSING: `/mnt/local-analysis/workspace-hub/assethold/requirements.txt` (referenced by workflow — this is the install-step break)
- EXISTS: `/mnt/local-analysis/workspace-hub/assethold/pyproject.toml`, `uv.lock`, `tests/`

**Line excerpts** (`grep -n` against HEAD of `assethold/.github/workflows/python-tests.yml`, 2026-04-21):
```
122:        DATABASE_URL: sqlite:///:memory:        # UNQUOTED — triggers YAML mapping error
138:        DATABASE_URL: sqlite:///:memory:        # UNQUOTED — same defect, second occurrence
144:      uses: codecov/codecov-action@v3          # DEPRECATED — Node 16; folded into P1 sweep
153:      uses: actions/upload-artifact@v3         # DEPRECATED — GitHub hard-rejects v3
166:      uses: actions/upload-artifact@v3         # DEPRECATED — second site
339:      uses: github/codeql-action/upload-sarif@v2   # DEPRECATED — v2 retired
345:      uses: actions/upload-artifact@v3         # DEPRECATED — third site
```

**YAML-parse root-cause proof** (`python -c "import yaml; yaml.safe_load(open('.github/workflows/python-tests.yml'))"`, 2026-04-21):
```
yaml.scanner.ScannerError: mapping values are not allowed here
  in ".github/workflows/python-tests.yml", line 122, column 40
```
Confirms unquoted `sqlite:///:memory:` at line 122 is the first fatal parse error; GitHub Actions rejects the workflow at startup (0s / 0 jobs pattern) because of this.

**Requirements reference evidence** (`rg -n requirements .github/workflows/python-tests.yml`):
```
 74:        uv pip install --system -r requirements.txt
222:        uv pip install --system -r requirements.txt
269:        uv pip install --system -r requirements.txt
```
All three install sites reference non-existent `requirements.txt`. `requirements-consolidated.txt` exists but self-declares "replaced by pyproject.toml ->� Kept for reference only" (verified 2026-04-21, file header lines 1-4). Correct remediation: replace with `uv pip install --system -e ../assetutilities` (preserves `--system` install pattern that bare pytest/mypy/flake8 commands depend on). The existing `uv pip install --system -e .` steps (lines 79, 224, 271) install assethold after assetutilities is satisfied.

**Gap proof** (`ls assethold/requirements.txt 2>&1`):
- `ls: cannot access 'assethold/requirements.txt': No such file or directory` → confirms missing install-target.

**Fork-transfer artifacts** (`rg -l samdansk2 /mnt/local-analysis/workspace-hub/assethold`):
- `assethold/README.md` — prose reference only (not a CI blocker)
- `assethold/src/assethold/__init__.py` — author string (not a CI blocker)
- `assethold/pyproject.toml.backup` — backup file, not loaded
- `assethold/poetry_latest_versions.txt` — ancillary
- CRITICAL: zero matches in `.github/workflows/` — confirms fork-transfer is NOT contributing to workflow startup failure, consistent with issue body.

<!-- Source count: issue body + 5 live verifications (gh run list, git remote, workflow line reads, file existence, fork-artifact grep) + 1 memory reference = 7 distinct sources. Minimum ≥3 satisfied. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-21-issue-2442-assethold-python-tests.md` |
| Primary workflow to fix | `assethold/.github/workflows/python-tests.yml` |
| Secondary workflow (phase-3) | `assethold/.github/workflows/docs.yml` |
| Install source of truth (CI + local) | `assethold/pyproject.toml` (via `uv pip install --system -e .`; sibling dep via `uv pip install --system -e ../assetutilities`) |
| Obsolete (not used) | `assethold/requirements-consolidated.txt` (self-declared reference-only) |
| Test roots (discovery) | `assethold/tests/` (unit/, integration/, etc.) |
| Plan review — Claude | `scripts/review/results/2026-04-21-plan-2442-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-21-plan-2442-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-21-plan-2442-gemini.md` |

---

## Deliverable

**Issue-close criterion:** `python-tests.yml` achieves its first green on `vamseeachanta/assethold` main (at least one smoke cell green = P2 complete). Full `quality-gate` chain (P3) and `docs.yml` are follow-on scope — not required to close #2442.

Phased remediation: (1) YAML-parse + deprecated-action fixes to make startup succeed, (2) install-step + sibling-dep resolution so at least one matrix cell passes (issue-close gate), (3) full matrix green + docs.yml diagnosis (follow-on issues if needed).

---

## Pseudocode

```
# PHASE 1 — startup unblock (deterministic; lifts "0s/0 jobs" symptom)
for each occurrence at lines 122, 138:
    wrap value in double quotes:
        DATABASE_URL: sqlite:///:memory:  ->  DATABASE_URL: "sqlite:///:memory:"

for each occurrence at lines 153, 166, 345:
    bump:  actions/upload-artifact@v3  ->  actions/upload-artifact@v4

bump line 339:  github/codeql-action/upload-sarif@v2  ->  @v3

bump line 144:  codecov/codecov-action@v3  ->  @v4
    # folded into P1 sweep (per Gemini review) — Node 16 deprecation class;
    # completes the "no deprecated actions remain" sweep

# ACCEPTANCE-PHASE-1: workflow parses; jobs register; matrix executes;
#   jobs may still fail on install step, but runs are no longer 0s-startup-reject.
#   Verification: YAML parses via `python -c "import yaml; yaml.safe_load(...)"`
#   with exit 0; `gh run view <run-id>` shows jobs[] != [].

# PHASE 2 — install-step correctness (startup unblocked + smoke cell green)
# Deliverable narrowed (per Codex + Claude convergent review): P2 targets
# "first non-zero-jobs run + one smoke cell green". Full `quality-gate`
# (which chains test + integration-tests + financial-data-tests) is P3.
#
# CRITICAL: must use `uv pip install --system` (NOT `uv sync --frozen`)
# because all downstream pytest/mypy/flake8 commands run bare (no `uv run`
# prefix). `uv sync` creates a .venv/ that bare commands cannot see.

# P2 fix 1: replace non-existent requirements.txt with sibling-dep install
# (requirements-consolidated.txt is self-declared "reference only" —
#  pyproject.toml is authoritative; existing line 79/224/271 already does
#  `uv pip install --system -e .` which installs the project itself)
for each occurrence at lines 74, 222, 269:
    replace:  uv pip install --system -r requirements.txt
    with:     uv pip install --system -e ../assetutilities
# The existing `-e .` steps (lines 79, 224, 271) remain unchanged —
# they install assethold with assetutilities already satisfied from above.

# P2 fix 2: resolve assetutilities sibling-dep on hosted runner
# Chosen mechanism: M1-revised — git clone (NOT actions/checkout, which
# requires path UNDER $GITHUB_WORKSPACE; ../assetutilities is rejected).
# git clone works because assetutilities is PUBLIC (verified Wave 3).
# Insert AFTER the main repo checkout in each of the 3 dep-installing jobs
# (test, integration-tests, financial-data-tests):
    - name: Clone assetutilities sibling dependency
      run: git clone --depth 1 https://github.com/vamseeachanta/assetutilities.git ../assetutilities

# PHASE GATE ENFORCEMENT (addresses Claude Wave-1 MAJOR — unenforceable gate):
# Phase 1 and Phase 2 MUST be separate commits pushed to main sequentially.
# (Direct-to-main per assethold repo convention — no branch/PR required.)
# Executor sequence:
#   1. Commit P1 edits (7 sites: YAML quoting + deprecated actions)
#   2. Push to main, wait for CI run, verify: jobs[] != [] (startup unblocked)
#   3. Only after P1 CI verification: commit P2 edits (3 install + 3 checkout)
#   4. Push to main, wait for CI run, verify: smoke cell green
# If P1 CI fails unexpectedly: investigate before P2 commit (do not bundle).
# If P2 CI fails: iterate on main with additional fix commits.

# ACCEPTANCE-PHASE-2: at least one matrix cell (py3.11 ubuntu-latest)
#   completes with smoke cell `conclusion=success`.
#   Full quality-gate chain deferred to P3.

# PHASE 3 — full workflow green (test + integration + financial + quality-gate) + docs.yml
# Full matrix + upstream jobs needed for quality-gate chain to reach conclusion=success.

drive remaining matrix cells / jobs to green:
    # address any test-red exposed in P2 smoke
    # verify integration-tests and financial-data-tests jobs complete
    # quality-gate depends on all three — must propagate success

diagnose docs.yml zero-jobs:
    # workflow_dispatch already present — trigger manual run, capture logs
    # most-likely: mkdocs --strict failing against missing docs/api/
    # fix path-filter OR add docs/api/ skeleton OR relax --strict

harden python-tests matrix:
    # narrow matrix if macos/windows are secondary (reduce noise)
    # add pip-cache / uv-cache for speed

# ACCEPTANCE-PHASE-3: green on main for push-trigger; quality-gate=success
#   (requires all of test, integration-tests, financial-data-tests green);
#   coverage upload works; docs.yml produces interpretable logs
#   (green OR documented-deferred)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify (P1) | `assethold/.github/workflows/python-tests.yml` | Quote DATABASE_URL at lines 122, 138 (×2); bump `actions/upload-artifact@v3 → v4` at lines 153, 166, 345 (×3); bump `github/codeql-action/upload-sarif@v2 → v3` at line 339 (×1); bump `codecov/codecov-action@v3 → v4` at line 144 (×1). Total P1 sites: **7**. |
| Modify (P2) | `assethold/.github/workflows/python-tests.yml` | Replace `uv pip install --system -r requirements.txt` with `uv pip install --system -e ../assetutilities` at lines 74, 222, 269 (x3). Add `git clone --depth 1` step for `vamseeachanta/assetutilities` into `../assetutilities` AFTER the main checkout in each of the 3 dep-installing jobs (test / integration-tests / financial-data-tests). NOTE: uses `git clone` not `actions/checkout` because checkout@v4 requires path under $GITHUB_WORKSPACE; ../assetutilities is outside it. Existing `uv pip install --system -e .` steps (lines 79, 224, 271) unchanged. Total P2 sites: **3 install edits + 3 new clone steps = 6**. |
| Verify (P2) | `assethold/pyproject.toml` | Confirm `assetutilities` is in `[project.dependencies]` and `[tool.uv.sources]` points to `{ path = "../assetutilities" }` — the P2 sibling-checkout step places the repo at that exact path so both `uv pip install --system -e ../assetutilities` and the existing `-e .` step resolve correctly. |
| Possibly modify (P3) | `assethold/.github/workflows/docs.yml` | Adjust `--strict` / path-filter / docs/api skeleton after workflow_dispatch log capture. |

**Combined fix-site count: 13 (7 P1 + 6 P2)** (prior plan claimed 9 sites; recount driven by (a) adding codecov-action P1 bump, (b) replacing 3 requirements-file edits with 3 `uv pip install --system -e ../assetutilities` switches + 3 new sibling-checkout insertions, (c) correcting line 136 to 138).

**Out-of-session (not edited in this planning session):** `docs/plans/README.md` already contains a row for plan 2442 (verified 2026-04-21 — Codex finding acknowledged); no update needed.

**Out-of-scope for this plan** (deferred to follow-on issues):
- Broader test-failure remediation (if phase-2 exposes red tests unrelated to CI config)
- `actions/setup-python@v4 → v5` and `astral-sh/setup-uv@v1 → v4` pin upgrades (Claude minor finding) — not on the deprecated-blocker critical path; file follow-on hygiene issue
- Matrix pruning (macos/windows) — defer unless phase-2 reveals per-OS breakage

---

## TDD Test List

Since this plan remediates CI config (not application code), the "tests" are **workflow-state assertions** run via `gh run list / gh run view`.

| Test | What it verifies | Expected state after fix |
|---|---|---|
| phase-1: local YAML parses | `python -c "import yaml; yaml.safe_load(open('.github/workflows/python-tests.yml'))"` exits 0 | exit 0, no ScannerError |
| phase-1: CI YAML parses | `gh run view <run-id>` shows `jobs` array non-empty | `jobs[] != []` |
| phase-1: startup time > 0s | workflow doesn't insta-reject | duration > 5s |
| phase-1: upload-artifact is v4 exactly | `rg -c 'upload-artifact@v4' .github/workflows/python-tests.yml` | `== 3` |
| phase-1: no deprecated actions remain | `rg -c 'upload-artifact@v3\|upload-sarif@v2\|codecov-action@v3' .github/workflows/python-tests.yml` | `== 0` |
| phase-2: sibling checkout present | `rg -c 'repository: vamseeachanta/assetutilities' .github/workflows/python-tests.yml` | `>= 1` |
| phase-2: install step succeeds | `gh run view --log` shows `uv pip install --system -e ../assetutilities` exit 0 for at least py3.11/ubuntu | `Successfully installed` line |
| phase-2: at least one smoke test runs | `gh run view --log` shows `test_smoke.py::* PASSED` | >=1 PASSED |
| phase-2: py3.11 ubuntu smoke job green | job conclusion | `success` |
| phase-3: full quality-gate green | `quality-gate` job conclusion (chains test + integration-tests + financial-data-tests) | `success` |
| phase-3 (optional): docs.yml manual run captures logs | `gh run view` on workflow_dispatch | jobs[] populated |
| parent-issue green-signal | overall workflow on main push | `conclusion=success` for python-tests on next push to main |

Local pre-push gate: `cd assethold && uv run pytest tests/test_smoke.py -v` must pass before pushing phase-2 fix. **CI gate on main** (the hosted runner naturally lacks `../assetutilities` before the sibling checkout step runs): push P2 commit to main, wait for CI run, verify smoke cell (py3.11/ubuntu-latest in `test` job) green.

---

## Acceptance Criteria

- [ ] Local YAML parse passes: `python -c "import yaml; yaml.safe_load(open('.github/workflows/python-tests.yml'))"` exits 0 (phase-1 pre-push gate)
- [ ] `python-tests.yml` YAML parses in CI — next push produces a run with non-empty `jobs` array (phase-1 CI gate)
- [ ] No `actions/upload-artifact@v3`, `github/codeql-action/upload-sarif@v2`, or `codecov/codecov-action@v3` remain in `python-tests.yml` (P1 deprecated-action sweep complete)
- [ ] Install step uses `uv pip install --system -e ../assetutilities` at all 3 sites (lines 74, 222, 269) — zero references to non-existent `requirements.txt` and zero references to the reference-only `requirements-consolidated.txt`
- [ ] Existing `uv pip install --system -e .` steps preserved at lines 79, 224, 271 (these install the project itself after assetutilities is satisfied)
- [ ] Sibling-repo checkout step (`actions/checkout@v4` for `vamseeachanta/assetutilities` into `../assetutilities`) present before the main checkout in every dep-installing job (test, integration-tests, financial-data-tests)
- [ ] Phase 1 and Phase 2 are separate commits pushed directly to main with CI verification between them (P1 push to main -> wait for CI -> verify jobs register -> P2 push to main -> wait for CI -> verify smoke green). Direct-to-main per assethold repo convention.
- [ ] At least one matrix cell (py3.11 / ubuntu-latest) completes smoke with `conclusion=success` (phase-2 gate — the "first non-zero-jobs, first smoke-green in 7 months" milestone)
- [ ] (FOLLOW-ON, not required to close #2442) Full `quality-gate` job completes `success` on a push to main (phase-3 — requires `test` + `integration-tests` + `financial-data-tests` all green; file as separate issue if latent test debt blocks this)
- [ ] Local smoke test passes: `cd assethold && uv run pytest tests/test_smoke.py -v`
- [ ] Review artifacts posted to `scripts/review/results/2026-04-21-plan-2442-{claude,codex,gemini}.md`
- [ ] No changes pushed to `assethold/` in the planning session — fixes land only after user re-confirms `status:plan-approved` in-thread after reading this revised plan (label-artifact alignment was reset to `status:plan-review` by orchestrator per governance comment 4290738146; re-approval required)
- [ ] (Phase-3, optional) `docs.yml` either goes green OR a follow-on issue is filed with diagnostic logs captured via workflow_dispatch

---

## Adversarial Review Summary

<!-- Wave 1 adversarial review complete; this section records revisions and awaits Wave 2 re-review. -->

**Wave 1 verdicts:**

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | Line-number drift (DATABASE_URL at 138 not 136; codecov at 144 not 343); assetutilities sibling-dep belongs in fix list not risks footnote; YAML-parse root cause unproven; P1→P2 gate unenforceable; local smoke can't catch sibling-dep failure; label-drift governance violation. |
| Codex | MAJOR | P2 acceptance ("one cell green") does not satisfy stated deliverable (quality-gate chains test + integration + financial-data); assetutilities resolution under-specified (pyproject declares `{ path = "../assetutilities" }` but workflow only checks out assethold); `requirements-consolidated.txt` is self-declared "reference only" — default remediation points at an obsolete file; README row already exists. |
| Gemini | MAJOR | Sibling repos not cloned by default in GitHub Actions — local-path install needs explicit checkout step; `codecov/codecov-action@v3` should be in P1 sweep, not Open Questions; install strategy (uv sync vs requirements) left ambiguous. |

**Wave 1 overall result:** MAJOR (3× MAJOR, all convergent on sibling-dep blocker)

**Revisions made based on review:**
- Added `actions/checkout` step for `vamseeachanta/assetutilities` into `../assetutilities` (Option M1) as a Phase-2 fix-list item — addresses Claude + Codex + Gemini convergent blocker. Rationale for M1 over M2 (git+https): `pyproject.toml` already declares `[tool.uv.sources] assetutilities = { path = "../assetutilities" }`; M1 preserves local-dev parity and avoids a `pyproject.toml` rewrite.
- Switched P2 install step from `requirements-consolidated.txt` to `uv pip install --system -e ../assetutilities` at 3 sites (Codex + Gemini) — the consolidated file self-declares "replaced by pyproject.toml — reference only". Uses `--system` install (NOT `uv sync --frozen`) because all downstream pytest/mypy/flake8 commands run bare without `uv run` prefix. The existing `uv pip install --system -e .` steps (lines 79, 224, 271) remain unchanged and install assethold after assetutilities is satisfied.
- Narrowed P2 deliverable to "startup unblocked + smoke cell green"; pushed full `quality-gate` (test + integration-tests + financial-data-tests chain) to P3 (Claude + Codex). Updated Deliverable, Pseudocode, Acceptance Criteria, and TDD list accordingly.
- Re-verified every cited line number via `grep -n` against HEAD (Claude): DATABASE_URL 122, **138** (was 136); codecov-action **144** (was 343); upload-artifact 153, 166, 345; upload-sarif 339; requirements 74, 222, 269. Plan now lists only verified line numbers.
- Folded `codecov/codecov-action@v3 → v4` into P1 deprecated-action sweep (Gemini) — removed from Open Questions.
- Added YAML-parse root-cause proof to §Evidence (Claude): `yaml.scanner.ScannerError: mapping values are not allowed here — line 122, column 40` from `python -c "import yaml; yaml.safe_load(...)"`.
- Updated fix-site count from 9 to 13 (7 P1 + 6 P2). Fix-site table now explicitly enumerates P1 vs P2 sites and counts.
- Added sibling-less Docker container pre-push gate (Claude) — later replaced by feature-branch CI gate (more reliable: hosted runner naturally lacks `../assetutilities`; no Docker setup needed).
- Tightened TDD assertions: `rg -c 'upload-artifact@v4'` exact count 3 (was generic `@v4` 3+ hits); added `rg -c '<deprecated-patterns>'` == 0 check; added local YAML-parse pre-push assertion.
- Removed stale "Update docs/plans/README.md" row from Files to Change (Codex) — README already has a 2442 row.
- Acceptance criteria now require user re-confirmation in-thread after reading revised plan (orchestrator rolled `status:plan-approved` label back to `status:plan-review` earlier this session per governance comment 4290738146); plan no longer proceeds on the pre-applied label.

**Wave 2 revisions** (addressing `uv sync --frozen` correctness gap discovered during live verification):
- Replaced `uv sync --frozen` with `uv pip install --system -e ../assetutilities` at all 3 install sites. Rationale: `uv sync` creates a `.venv/` directory, but all downstream commands (`pytest`, `mypy`, `flake8`, `bandit`, `safety`) run bare without `uv run` prefix — they expect system-installed packages. Switching to `uv sync` would silently break all test/lint steps. The `--system` editable install preserves the existing behavior and is the minimum-change fix.
- Added explicit phase gate enforcement to pseudocode: P1 and P2 must be separate commits on a feature branch, with CI verification between them. Executor must push P1, wait for CI, verify jobs register, then push P2, wait for CI, verify smoke green, then PR to main. Addresses Claude Wave-1 MAJOR "unenforceable gate."
- Replaced Docker container pre-push gate with feature-branch CI gate (the real hosted runner IS the sibling-less environment; Docker repro adds complexity without value since the feature-branch CI run verifies the same thing).
- Documented that existing `uv pip install --system -e .` steps (lines 79, 224, 271) remain unchanged — they install the project itself after assetutilities is satisfied from the previous step.

**Revisions deferred** (with rationale):
- `actions/setup-python@v4 -> v5` and `astral-sh/setup-uv@v1 → v4` pin bumps (Claude MINOR): not on the deprecated-blocker critical path; these versions are still accepted by GitHub Actions. Deferred to a follow-on hygiene issue to keep this plan scoped to the never-green fix.
- Matrix pruning (macos/windows) (Claude MINOR, original Open Question): deferred to P3 or a follow-on; not required to achieve the "first green in 7 months" milestone.
- T2 vs T3 reclassification (Claude MINOR): keeping T2 after P3 scope became deterministic (full quality-gate chain is now a direct gate, not a diagnostic-first unknown); docs.yml phase-3 diagnosis retained as optional/follow-on.

**Wave 3 revisions** (addressing Wave 2 Claude MAJOR + Codex MAJOR):
- Fixed stale "uv sync --frozen" wording in fix-site recount (Claude P1) -- now reads `uv pip install --system -e ../assetutilities`
- Added verified evidence for 3 preconditions: assetutilities is PUBLIC (no token issue), assetutilities has no cascading sibling deps, `test_smoke.py` exists (Claude P1, Codex P1)
- Added `ref: main` coupling as explicit risk with accepted-for-now mitigation (Claude P2)
- Reconciled complexity stanza site count to 13 (7 P1 + 6 P2) (Claude P3)
- Fixed execution strategy: direct-to-main per assethold repo convention, not feature-branch (Codex P2 policy exception)
- Made docs.yml explicitly out-of-scope for P1/P2 success criteria (Codex P2 scope ambiguity)
- Added failure-path contingency to phase gate enforcement block (Codex P3)
- Fixed Unicode encoding artifacts throughout

**Status:** Wave 3 revised, awaiting Wave 3 re-review.

---

## Risks and Open Questions

- **Risk -- sibling-dep resolution in CI (RESOLVED, moved to P2 fix list):** `pyproject.toml` declares `[tool.uv.sources] assetutilities = { path = "../assetutilities" }`; on a hosted runner `../assetutilities` does not exist. **Resolution:** P2 adds `actions/checkout` step for `vamseeachanta/assetutilities` into `../assetutilities` in every job that installs deps. Verification: feature-branch CI run on hosted runner. **Preconditions verified (Wave 3):** (a) `vamseeachanta/assetutilities` is PUBLIC (`gh repo view --json visibility` = PUBLIC, 2026-04-21) -- default GITHUB_TOKEN has read access; (b) `assetutilities/pyproject.toml` has empty `[tool.uv.sources]` -- no cascading sibling deps; (c) `assethold/tests/test_smoke.py` exists (confirmed via `gh api repos/vamseeachanta/assethold/contents/tests/test_smoke.py`).
- **Risk -- `ref: main` coupling (NEW, Wave 3):** The proposed sibling checkout uses `ref: main` for assetutilities. Any breaking change on assetutilities main will flip assethold CI red. **Mitigation:** accepted for now -- assetutilities has low commit frequency and assethold's local dev already depends on assetutilities main via `[tool.uv.sources]`. If assetutilities becomes volatile, pin to a SHA in a follow-on issue.
- **Risk — phase-2 reveals broad test-red state:** Since the workflow has never been green, real test failures may be latent. **Mitigation:** phase-2 target is explicitly "one matrix cell green via smoke test," not full matrix. Broader test remediation that blocks full quality-gate lands in phase-3; file follow-on issues for discovered test debt rather than expanding this plan's scope.
- **Risk — label-drift governance (RESOLVED):** #2442 was labeled `status:plan-approved` at handoff creation before any plan existed. Orchestrator rolled the label back to `status:plan-review` this session (governance comment 4290738146). **Resolution:** this plan requires fresh in-thread user approval after reading the revised artifact; no action needed in the plan file beyond the acceptance criterion.
- **Risk -- `docs.yml` (EXPLICITLY OUT-OF-SCOPE for P1/P2):** docs.yml diagnosis is deferred to a follow-on issue. This plan's success criteria are satisfied when `python-tests.yml` achieves first green. docs.yml is mentioned in P3 as optional/diagnostic only. If P3 is attempted and docs.yml root cause is deeper than expected, file a separate issue.
- **Open — matrix scope:** Should py3.9 + windows/macos cells be pruned to accelerate greenlight? Full 4×3=12 matrix on every push to main is expensive; phase-3 may need to narrow. **Flag for user decision.**
- **Open — P3 test-red handling:** If P2 smoke cell surfaces systemic test failures that prevent the quality-gate chain from reaching success, does the P3 deliverable split into a separate issue (test-debt remediation) while this plan settles at P2-green? **Flag for user decision at P2→P3 transition.**

---

## Complexity: T2

**T2** — multi-site targeted edits in a single workflow file (7 P1 fix sites + 6 P2 sites = 13 total), phased execution with intermediate acceptance gates, cross-repo verification (workspace-hub plan governs edits in sibling repo `assethold/`). Not T3 because the remediation is mechanically deterministic (all fix sites already identified in issue body and verified against live state); no architectural decisions or new subsystems. Not T1 because it spans two phases with distinct acceptance gates and touches sibling-repo dep resolution.
