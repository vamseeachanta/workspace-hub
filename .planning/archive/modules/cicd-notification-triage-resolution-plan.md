# CI/CD Notification Triage & Resolution Plan

## Overview

All unread GitHub notifications are CI/CD failures across 3 repositories. There are also 2 pending Dependabot PRs to review.

## Notification Summary

| Repository | Failing Workflows | Root Cause | Notifications |
|------------|------------------|------------|---------------|
| **workspace-hub** | Baseline Testing CI/CD, Scheduled Baseline Audit | Deprecated `actions/upload-artifact@v3` / `download-artifact@v3` | ~10 |
| **worldenergydata** | CI, Nightly | Orphaned git submodule `pymvil` in `assetutilities` dependency | ~12 |
| **digitalmodel** | Quality Gates, OrcaFlex/AQWA/Catenary Module Tests | Missing `uv venv` before `uv pip install` | ~20 |

**Pending PRs:** worldenergydata #114 (actions bump), #115 (scrapy bump) - both blocked by CI
**Auto-created Issue:** worldenergydata #117 (nightly failure)

---

## Resolution Steps

### Step 1: Fix workspace-hub workflows (artifact actions v3 -> v4)

**Files:**
- `.github/workflows/baseline-check.yml` - lines 210, 245, 289
- `.github/workflows/baseline-audit.yml` - lines 319, 334

**Changes:** Replace all `actions/upload-artifact@v3` with `@v4` and `actions/download-artifact@v3` with `@v4`.

Note: v4 has breaking changes around artifact naming (must be unique per job) and multi-path uploads. Will audit each usage for compatibility.

### Step 2: Fix digitalmodel workflows (add uv venv step)

**Files:** `.github/workflows/quality-gates.yml` and potentially all 11 workflow files:
- `aqwa-tests.yml`, `catenary-riser-tests.yml`, `diffraction-tests.yml`
- `gmsh-meshing-tests.yml`, `hydrodynamics-tests.yml`, `mooring-analysis-tests.yml`
- `orcaflex-tests.yml`, `structural-analysis-tests.yml`, `viv-analysis-tests.yml`
- `workflow-automation-tests.yml`

**Changes:** Add `uv venv` step before `uv pip install` commands in **all 11** workflow files (confirmed by user).

### Step 3: Fix assetutilities submodule issue (unblocks worldenergydata)

**Root cause:** `src/assetutilities/modules/pymvil` is registered as a git submodule (mode 160000) but:
- No `.gitmodules` file exists in the repo
- No `pymvil` repository exists under `vamseeachanta/`

**Fix:** Remove the orphaned submodule reference from assetutilities:
```
git rm --cached src/assetutilities/modules/pymvil
git commit -m "fix: remove orphaned pymvil submodule reference"
git push
```
This will allow `git submodule update --recursive --init` to succeed during dependency installation.

**Confirmed:** User approved removing the orphaned submodule.

### Step 4: Review & merge worldenergydata PRs

- **PR #114** - Bumps 7 GitHub Actions (checkout, setup-uv, upload-artifact, codecov, etc.). Review and merge after CI passes.
- **PR #115** - Bumps scrapy 2.12.0 -> 2.13.4. Review and merge after CI passes.

### Step 5: Close issue #117

Close worldenergydata issue #117 (auto-created nightly failure) once nightly workflow passes.

### Step 6: Mark all notifications as read

```
gh api notifications -X PUT -f read=true
```

---

## Verification

After each repo fix:
1. Push the fix commit
2. Monitor the workflow run: `gh run watch <run-id> --repo <repo>`
3. Confirm the workflow passes before moving to next repo

Final: Confirm all notifications are resolved and no new failures appear.
