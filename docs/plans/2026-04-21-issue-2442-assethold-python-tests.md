# Plan for #2442: assethold CI — python-tests.yml never green since 2025-09-28 (YAML parse + deprecated actions + fork-transfer artifacts)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-21
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2442
> **Parent meta-issue:** https://github.com/vamseeachanta/workspace-hub/issues/2424
> **Review artifacts:** scripts/review/results/2026-04-21-plan-2442-claude.md | ...-codex.md | ...-gemini.md
> **Note:** Issue #2442 already carries `status:plan-approved` label (pre-applied from handoff generation). This plan is the canonical artifact; adversarial review still required before execution.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `assethold/.github/workflows/python-tests.yml` (432+ lines) — comprehensive matrix workflow (Python 3.9–3.12 × ubuntu/windows/macos), test + integration + financial-data + quality-gate jobs. YAML parse fails at startup — 0 jobs register, 0s duration.
- Found: `assethold/.github/workflows/docs.yml` (35 lines, much smaller). YAML is structurally valid. Also fails with 0s/zero-jobs. Already has `workflow_dispatch` trigger.
- Found: `assethold/requirements-consolidated.txt` exists; `assethold/requirements.txt` does NOT exist. Workflow references `requirements.txt` at 3 sites (lines 74, 222, 269).
- Found: `assethold/pyproject.toml` — setuptools-based (not pure uv), dependencies include sibling repo `assetutilities` (git-local dep implication for CI install).
- Found: `assethold/tests/` — full pytest tree: `unit/`, `integration/`, `net_lease/`, `options/`, `portfolio/`, `contracts/`, plus 7 top-level `test_*.py` files. Tests exist; discovery path is intact.
- Found: `assethold/uv.lock` — lockfile present.
- Gap: workflow refers to non-existent `requirements.txt`; must switch to `requirements-consolidated.txt` or `uv sync`.

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
- `assetutilities` dependency resolution in CI unverified — sibling-repo dep may require additional CI install steps (e.g., `uv pip install -e ../assetutilities` pattern) not currently expressed in workflow.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-21 via `gh issue view 2442 --json state,labels`):
- `#2442` — OPEN — labels: `priority:high`, `cat:infrastructure`, `status:plan-approved` (drift: approval label pre-applied before plan artifact existed; noted in governance comment)
- `#2424` — parent meta-issue (referenced, not re-fetched this session)

**File existence** (`ls` 2026-04-21):
- EXISTS: `/mnt/local-analysis/workspace-hub/assethold/.github/workflows/python-tests.yml`
- EXISTS: `/mnt/local-analysis/workspace-hub/assethold/.github/workflows/docs.yml`
- EXISTS: `/mnt/local-analysis/workspace-hub/assethold/requirements-consolidated.txt`
- MISSING: `/mnt/local-analysis/workspace-hub/assethold/requirements.txt` (referenced by workflow — this is the install-step break)
- EXISTS: `/mnt/local-analysis/workspace-hub/assethold/pyproject.toml`, `uv.lock`, `tests/`

**Line excerpts** (`sed -n N,Mp .github/workflows/python-tests.yml`):
```
122:        DATABASE_URL: sqlite:///:memory:        # UNQUOTED — triggers YAML mapping error
136:        DATABASE_URL: sqlite:///:memory:        # UNQUOTED — same defect, second occurrence
153:      uses: actions/upload-artifact@v3         # DEPRECATED — GitHub hard-rejects v3
166:      uses: actions/upload-artifact@v3         # DEPRECATED — second site
339:      uses: github/codeql-action/upload-sarif@v2   # DEPRECATED — v2 retired
345:      uses: actions/upload-artifact@v3         # DEPRECATED — third site
```

**Requirements reference evidence** (`rg -n requirements .github/workflows/python-tests.yml`):
```
 74:        uv pip install --system -r requirements.txt
222:        uv pip install --system -r requirements.txt
269:        uv pip install --system -r requirements.txt
```
All three install sites reference non-existent `requirements.txt`. Correct file is `requirements-consolidated.txt`.

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
| Install target (CI + local) | `assethold/requirements-consolidated.txt` |
| Dep manifest (verify) | `assethold/pyproject.toml`, `assethold/uv.lock` |
| Test roots (discovery) | `assethold/tests/` (unit/, integration/, etc.) |
| Plan review — Claude | `scripts/review/results/2026-04-21-plan-2442-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-21-plan-2442-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-21-plan-2442-gemini.md` |

---

## Deliverable

A green `python-tests.yml` run on `vamseeachanta/assethold` main — the first green in 7 months — achieved via a **phased** remediation: (1) YAML-parse + deprecated-action fixes to make startup succeed, (2) install-step + smoke-test correctness so at least one matrix cell passes, (3) full matrix + docs.yml hardening.

---

## Pseudocode

```
# PHASE 1 — startup unblock (deterministic; lifts "0s/0 jobs" symptom)
for each occurrence at lines 122, 136:
    wrap value in double quotes:
        DATABASE_URL: sqlite:///:memory:  ->  DATABASE_URL: "sqlite:///:memory:"

for each occurrence at lines 153, 166, 345:
    bump:  actions/upload-artifact@v3  ->  actions/upload-artifact@v4

bump line 339:  github/codeql-action/upload-sarif@v2  ->  @v3

# ACCEPTANCE-PHASE-1: workflow parses; jobs register; matrix executes;
#   jobs may still fail on install step, but runs are no longer 0s-startup-reject.

# PHASE 2 — install-step correctness (one matrix cell green)
for each occurrence at lines 74, 222, 269:
    replace:  uv pip install --system -r requirements.txt
    with:     uv pip install --system -r requirements-consolidated.txt
    # (OR switch to `uv sync --frozen` if uv.lock is authoritative;
    #  decide after verifying assetutilities sibling-dep resolution.)

verify assetutilities dependency resolution path:
    if sibling-repo dep needs editable install:
        prepend install step:  uv pip install -e <path-or-git+url>
    else:
        trust pyproject.toml dep list

run locally:  cd assethold && uv run pytest tests/test_smoke.py -v
    # must be green before pushing CI fix

# ACCEPTANCE-PHASE-2: at least one matrix cell (py3.11 ubuntu-latest)
#   completes to "jobs[] populated, conclusion=success or test-only failure"

# PHASE 3 — docs.yml diagnostic + matrix hardening (optional / follow-on)
diagnose docs.yml zero-jobs:
    # workflow_dispatch already present — trigger manual run, capture logs
    # most-likely: mkdocs --strict failing against missing docs/api/
    # fix path-filter OR add docs/api/ skeleton OR relax --strict

harden python-tests matrix:
    # narrow matrix if macos/windows are secondary (reduce noise)
    # add pip-cache / uv-cache for speed
    # verify codecov@v3 -> v5 (optional; not in critical-path)

# ACCEPTANCE-PHASE-3: green on main for push-trigger; coverage upload works;
#   docs.yml produces interpretable logs (green OR documented-deferred)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `assethold/.github/workflows/python-tests.yml` | Quote DATABASE_URL (×2), bump upload-artifact v3→v4 (×3), bump upload-sarif v2→v3 (×1), fix requirements path (×3) |
| Verify | `assethold/requirements-consolidated.txt` | Confirm deps resolve for all matrix Python versions; add missing entries if smoke test fails |
| Possibly modify | `assethold/.github/workflows/python-tests.yml` (phase-2) | Add sibling-repo `assetutilities` install step if needed |
| Possibly modify | `assethold/.github/workflows/docs.yml` (phase-3) | Adjust `--strict` / path-filter / docs/api skeleton |
| Update | `docs/plans/README.md` | Add row for plan 2442 (deferred per constraint — NOT in this session) |

**Out-of-scope for this plan** (deferred to follow-on issues):
- Broader test-failure remediation (if phase-2 exposes red tests unrelated to CI config)
- codecov v3→v5 bump (non-blocking; optional quality improvement)
- Matrix pruning (macos/windows) — defer unless phase-2 reveals per-OS breakage

---

## TDD Test List

Since this plan remediates CI config (not application code), the "tests" are **workflow-state assertions** run via `gh run list / gh run view`.

| Test | What it verifies | Expected state after fix |
|---|---|---|
| phase-1: YAML parses | `gh run view <run-id>` shows `jobs` array non-empty | `jobs[] != []` |
| phase-1: startup time > 0s | workflow doesn't insta-reject | duration > 5s |
| phase-1: upload-artifact step exists as v4 | `rg '@v4' .github/workflows/python-tests.yml` | 3+ hits |
| phase-2: install step succeeds | `gh run view --log` shows `uv pip install` exit 0 for at least py3.11/ubuntu | `Successfully installed` line |
| phase-2: at least one smoke test runs | `gh run view --log` shows `test_smoke.py::* PASSED` | >=1 PASSED |
| phase-2: py3.11 ubuntu job green | job conclusion | `success` |
| phase-3 (optional): docs.yml manual run captures logs | `gh run view` on workflow_dispatch | jobs[] populated |
| parent-issue green-signal | overall workflow on main push | `conclusion=success` for python-tests on next push to main |

Local pre-push gate: `cd assethold && uv run pytest tests/test_smoke.py -v` must pass before pushing phase-2 fix.

---

## Acceptance Criteria

- [ ] `python-tests.yml` YAML parses — next push to main produces a run with non-empty `jobs` array (phase-1 gate)
- [ ] No `actions/upload-artifact@v3` or `github/codeql-action/upload-sarif@v2` remain in `python-tests.yml`
- [ ] Install step references `requirements-consolidated.txt` (or `uv sync`) — zero references to non-existent `requirements.txt`
- [ ] At least one matrix cell (py3.11 / ubuntu-latest) completes with `conclusion=success` (phase-2 gate — the "first green in 7 months" milestone)
- [ ] Local smoke test passes: `cd assethold && uv run pytest tests/test_smoke.py -v`
- [ ] Governance-cleanup note posted on #2442 explaining that the pre-applied `status:plan-approved` label is now backed by a real adversarial-reviewed plan artifact (label-artifact alignment)
- [ ] Review artifacts posted to `scripts/review/results/2026-04-21-plan-2442-{claude,codex,gemini}.md`
- [ ] No changes pushed to `assethold/` in the planning session — fixes land only after `status:plan-approved` is verified to be backed by this reviewed plan
- [ ] (Phase-3, optional) `docs.yml` either goes green OR a follow-on issue is filed with diagnostic logs captured via workflow_dispatch

---

## Adversarial Review Summary

<!-- Populated after Step 3 (Adversarial Review). Pre-review: not approval-ready. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | (pending) | — |
| Codex | (pending) | — |
| Gemini | (pending) | — |

**Overall result:** PENDING

Revisions made based on review: (none yet)

---

## Risks and Open Questions

- **Risk — sibling-dep resolution in CI:** `assetutilities` is listed in `pyproject.toml` dependencies without a specific index/git-url. In a clean GitHub Actions runner, `uv pip install -r requirements-consolidated.txt` may fail to resolve this sibling repo unless it's published to PyPI or the workflow explicitly installs it (`uv pip install -e ../assetutilities` or `git+https://…`). **Mitigation:** smoke-test the install step against the consolidated requirements locally on a fresh venv before pushing phase-2.
- **Risk — phase-2 reveals broad test-red state:** Since the workflow has never been green, real test failures may be latent. **Mitigation:** phase-2 target is explicitly "one matrix cell green via smoke test," not full matrix. File follow-on issues for discovered test debt rather than expanding this plan's scope.
- **Risk — label drift:** #2442 was labeled `status:plan-approved` at handoff-issue creation time, before any plan artifact existed. This violates the plan-approval gate semantics. **Mitigation:** post governance comment noting the drift; treat this plan as undergoing real adversarial review, and re-surface to user before execution even though label says approved.
- **Risk — `docs.yml` underlying cause unknown:** Phase-3 diagnosis is gated on workflow_dispatch log capture; actual failure mode is hypothesized (mkdocs strict vs missing `docs/api/`) but unverified. **Mitigation:** treat phase-3 as diagnostic-first; if root cause is deeper, file a separate follow-on issue and do not block `python-tests.yml` green-signal on `docs.yml`.
- **Open — uv-sync vs requirements file:** Should phase-2 switch the install strategy to `uv sync --frozen` (leveraging `uv.lock`) rather than renaming `requirements.txt → requirements-consolidated.txt`? The former is more idiomatic for uv-managed projects; the latter is the minimum change. **Flag for user decision at approval time.**
- **Open — matrix scope:** Should the py3.9 + windows/macos cells be pruned to accelerate greenlight? Running full 4×3=12 matrix on every push to main is expensive; phase-2 may need to narrow before phase-3. **Flag for user decision.**
- **Open — codecov action version:** `codecov/codecov-action@v3` at line 343 is not explicitly called out in the issue body; GitHub has deprecated older versions. Include in phase-1 or defer? **Flag for user decision.**

---

## Complexity: T2

**T2** — multi-site targeted edits in a single workflow file (6 known fix sites + 3 install-path sites), phased execution with intermediate acceptance gates, cross-repo verification (workspace-hub plan governs edits in sibling repo `assethold/`). Not T3 because the remediation is mechanically deterministic (all fix sites already identified in issue body and verified against live state); no architectural decisions or new subsystems. Not T1 because it spans two phases with distinct acceptance gates and touches sibling-repo dep resolution.
