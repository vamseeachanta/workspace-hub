## Plan Review — WRK-1072

**Title:** feat(harness): release management — semantic versioning + changelog for tier-1 repos

### Plan Summary

Give tier-1 engineering repos versioned releases with changelogs so it's always
traceable which version of a calculation module produced a given report or result.

**Deliverables:**
- `scripts/release/cut-release.sh` (113 lines) — bumps version, generates changelog, tags repo, updates manifest
- `scripts/release/generate-changelog.sh` (92 lines) — parses conventional commits into CHANGELOG.md format
- `scripts/release/tests/test-cut-release.sh` — 12 TDD tests
- `config/releases/release-manifest.yaml` — single source of truth for repo versions

### Acceptance Criteria
1. `pyproject.toml` has `version` field in all 5 tier-1 repos
2. `cut-release.sh` bumps version, generates CHANGELOG, tags repo
3. `CHANGELOG.md` generated from conventional commits per repo
4. `release-manifest.yaml` updated on every release
5. `--dry-run` flag shows what would be done without writing

### Confirmation

confirmed_by: vamsee
confirmed_at: 2026-03-12T23:01:00Z
decision: passed
route: B
notes: Fast-forward close — plan approved inline, implementation already at 94ad72bb
