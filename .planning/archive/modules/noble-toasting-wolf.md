# Plan: WRK-1072 — Release Management (SemVer + Changelog)

## Context
Engineering reports reference calculation modules without version traceability. Without
tagged releases, there is no way to reproduce a historic calculation or confirm which
version of assetutilities/digitalmodel was active when a report was produced. This WRK
adds a manual release workflow (tag + CHANGELOG + manifest) to all 5 tier-1 repos.

## Pre-conditions (already met)
- All 5 repos have `version = "X.Y.Z"` in `pyproject.toml` ✓ (currently 0.1.0)
- Commits follow conventional-commits style ✓

## Scripts to Create
Both scripts are reusable across WRKs / agents (≥25% recurrence rule):

| Script | Purpose |
|--------|---------|
| `scripts/release/cut-release.sh <repo> <version> [--dry-run]` | Main release entry point |
| `scripts/release/generate-changelog.sh <repo-path> <version> <since-ref>` | Parse git log → CHANGELOG entry |

## Phase 1 — Scaffold `config/releases/release-manifest.yaml`

Create `config/releases/release-manifest.yaml` with current versions for all 5 repos:
```yaml
# Release manifest — updated by scripts/release/cut-release.sh on every release
generated_at: "<date>"
repos:
  assetutilities: "0.1.0"
  digitalmodel: "0.1.0"
  worldenergydata: "0.1.0"
  assethold: "0.1.0"
  ogmanufacturing: "0.1.0"
```

## Phase 2 — `scripts/release/generate-changelog.sh`

Inputs: `<repo-path> <version> <since-ref>` (since-ref = last semver tag or first commit)

Logic:
1. Run `git -C <repo-path> log --pretty=format:"%s" <since-ref>..HEAD`
2. Parse lines by conventional-commit prefix (feat/fix/docs/refactor/test/perf/chore)
3. Group into sections: Features, Bug Fixes, Documentation, Other
4. Emit Keep-a-Changelog block:
   ```
   ## [<version>] - <date>
   ### Features
   - <feat lines>
   ### Bug Fixes
   - <fix lines>
   ```
5. If no commits found in range, emit a minimal entry with "(no notable changes)"

## Phase 3 — `scripts/release/cut-release.sh`

Arg parsing:
- `$1` = repo name (must be one of: assetutilities digitalmodel worldenergydata assethold OGManufacturing)
- `$2` = version (validated against regex `^[0-9]+\.[0-9]+\.[0-9]+$`)
- `--dry-run` = preview mode (no writes, exit 0=would-succeed)

Steps (skip writes when --dry-run):
1. Validate repo name and semver format; exit 1 on bad input
2. Resolve `<repo-path>` = `$WORKSPACE_ROOT/<repo>`; check it exists
3. Detect `<since-ref>`: `git -C <repo-path> describe --tags --abbrev=0 --match "v*.*.*" 2>/dev/null` or first commit
4. **Bump version**: `sed -i` on `<repo-path>/pyproject.toml` — replace `version = "<old>"` with `version = "<new>"`
5. **Generate CHANGELOG entry**: call `generate-changelog.sh`
6. **Prepend to CHANGELOG.md**: if file exists, insert after `# Changelog` header; otherwise create with header
7. **Commit in submodule**: `git -C <repo-path> add pyproject.toml CHANGELOG.md && git -C <repo-path> commit -m "chore(release): v<version>"`
8. **Tag in submodule**: `git -C <repo-path> tag v<version>`
9. **Update release-manifest.yaml**: `sed -i` to replace `<repo-name>: "<old>"` with `<repo-name>: "<new>"`
10. **Commit at hub level**: `git add config/releases/release-manifest.yaml <repo-path> && git commit -m "chore(release): <repo> v<version>"`
11. Print summary of what was done

Dry-run output format:
```
[DRY RUN] Would bump assetutilities: 0.1.0 → 0.1.1
[DRY RUN] Would tag: v0.1.1
[DRY RUN] Would add CHANGELOG entry (3 commits since 0.1.0)
[DRY RUN] Would update release-manifest.yaml
```

## Phase 4 — TDD Tests

File: `scripts/release/tests/test-cut-release.sh` (bats or plain bash assertions)

| Test | Type | Expected |
|------|------|---------|
| `--dry-run assetutilities 0.1.1` | happy path | exits 0, no file modifications |
| invalid repo name | error | exits 1, "Unknown repo" message |
| invalid version `1.2` | error | exits 1, "Invalid semver" message |
| generate-changelog.sh with no commits | edge | emits "(no notable changes)" entry |
| generate-changelog.sh with feat+fix commits | happy | groups into Features / Bug Fixes sections |
| manifest has correct version after real run | integration | grep shows updated version |

## Critical Files
- `scripts/release/cut-release.sh` — CREATE
- `scripts/release/generate-changelog.sh` — CREATE
- `scripts/release/tests/test-cut-release.sh` — CREATE (TDD)
- `config/releases/release-manifest.yaml` — CREATE
- `<each-repo>/CHANGELOG.md` — CREATE (assetutilities, worldenergydata, assethold, OGManufacturing) or prepend (digitalmodel already has one)

## Verification
```bash
# TDD tests pass
bash scripts/release/tests/test-cut-release.sh

# Dry-run smoke test
bash scripts/release/cut-release.sh assetutilities 0.1.1 --dry-run

# Check manifest
cat config/releases/release-manifest.yaml
```
