# Archived Skill: `provider-audit-bootstrap-and-path-classification`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/provider-audit-bootstrap-and-path-classification`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/provider-audit-bootstrap-and-path-classification`
Consolidation date: 2026-04-29

---

---
name: provider-audit-bootstrap-and-path-classification
description: Fix provider-session ecosystem audit failures caused by source-checkout imports and over-aggressive symbolic-path classification.
version: 1.0.0
category: workspace-hub-learned
tags: [provider-audit, source-checkout, pythonpath, stale-paths, classification, workspace-hub]
---

# Provider session audit: source-checkout bootstrap + read classification repair

Use when `scripts/analysis/provider_session_ecosystem_audit.py` or its cron wrapper fails in a repo checkout, or when the audit misclassifies repo paths as symbolic reads.

## When to use
- `bash scripts/cron/provider-session-ecosystem-audit.sh` fails with `ModuleNotFoundError: No module named 'workspace_hub'`
- the audit works in pytest/importlib contexts but fails from the wrapper or shell
- slash-delimited paths such as `scripts/hooks/post-merge` or `.claude/work-queue/WRK-149.md` are being counted as symbolic instead of repo paths
- Claude symbolic-read output looks suspicious while missing-repo counts look artificially low

## Symptoms
- Wrapper log shows:
  - `ModuleNotFoundError: No module named 'workspace_hub'`
- `scripts/analysis/provider_session_ecosystem_audit.py` imports `workspace_hub.workstations.resolver`
- `tests/conftest.py` makes pytest pass by inserting `src/` into `sys.path`, masking the runtime failure
- Audit output shows false symbolic reads for paths that should be repo-relative missing paths

## Root causes
1. The audit script may insert only `REPO_ROOT` into `sys.path`, but the importable package actually lives under `src/workspace_hub`.
2. The wrapper may invoke `uv run --no-project python ...` in a source checkout without exporting `PYTHONPATH=$REPO_ROOT/src`.
3. `classify_read_target()` may treat any slash-delimited symbolic-looking string as symbolic when the real first path component exists in the repo.

## Fix pattern

### 1. Bootstrap imports inside the script
At the top of `scripts/analysis/provider_session_ecosystem_audit.py` ensure both roots are added:

```python
REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
```

Why:
- direct shell execution needs `src/`
- keeping `REPO_ROOT` also preserves access to sibling script modules like `scripts.bash_command_prefixes`

### 2. Harden the wrapper for source checkouts
In `scripts/cron/provider-session-ecosystem-audit.sh`, before calling Python:

```bash
export PYTHONPATH="${REPO_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}"
uv run --no-project python scripts/analysis/provider_session_ecosystem_audit.py "$@" \
  >> "${LOG_FILE}" 2>&1
```

Why:
- the wrapper should work from cron/non-pytest contexts
- this avoids relying on an editable install or ambient shell state

### 3. Repair slash-path classification
In `classify_read_target()` keep truly symbolic slash names symbolic only when the repo does not contain the first path component and the candidate path does not exist.

Use this rule:

```python
if SYMBOLIC_SLASH_NAME_RE.fullmatch(text):
    first_component = text.split("/", 1)[0]
    candidate = repo_root / text
    if not text.startswith(".") and not safe_exists(repo_root / first_component) and not safe_exists(candidate):
        return text, "symbolic", False
```

Effect:
- `coordination/workspace/repo-capability-map` remains symbolic when the repo has no `coordination/`
- `scripts/hooks/post-merge` becomes a repo path if `scripts/` exists
- `.claude/work-queue/WRK-149.md` becomes a repo path instead of a symbolic read

## Regression tests to add

### Wrapper test
Update `tests/cron/test_provider_session_ecosystem_audit_wrapper.py` to assert the wrapper exports `PYTHONPATH="${REPO_ROOT}/src...`.

### Script bootstrap test
Add a test in `tests/analysis/test_provider_session_ecosystem_audit.py` asserting the script text contains:
- `REPO_ROOT / "src"`
- `sys.path.insert(0, str(SRC_ROOT))`

### Classification tests
Add tests proving:
- `scripts/hooks/post-merge` is classified as `repo` when `scripts/` exists
- `.claude/work-queue/WRK-149.md` is classified as `repo` when `.claude/` exists
- true symbolic names like `coordination/workspace/repo-capability-map` remain `symbolic`

## Verification sequence
Run all of these:

```bash
uv run pytest tests/analysis/test_provider_session_ecosystem_audit.py tests/cron/test_provider_session_ecosystem_audit_wrapper.py -q
bash scripts/cron/provider-session-ecosystem-audit.sh
env -u PYTHONPATH uv run --no-project python scripts/analysis/provider_session_ecosystem_audit.py > /tmp/provider-session-audit-smoke.out
uv run --no-project python scripts/cron/validate-schedule.py
```

Expected:
- pytest passes
- wrapper exits 0
- direct source-checkout smoke run succeeds even without inherited `PYTHONPATH`
- schedule validation remains green

## Operational impact
- Fixes false wrapper failures in cron/source checkout environments
- Makes Claude symbolic-read output more trustworthy
- Prevents repo-missing-path debt from being hidden behind over-broad symbolic classification
- Produces a more accurate stale-path remediation report for follow-on issue creation

## Pitfalls
- pytest may already pass because `tests/conftest.py` inserts `src/`; do not treat that as proof the wrapper is healthy
- do not classify all slash-delimited names as symbolic; check whether the repo owns the first path component
- keep `docs/ops/legacy-claude-reference-map.md` and historical audit reports separate from current instructional surfaces when acting on stale-path findings
