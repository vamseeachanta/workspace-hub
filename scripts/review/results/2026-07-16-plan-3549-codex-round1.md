## Verdict
MAJOR

## Retrieval
- Read `/mnt/local-analysis/workspace-hub/.worktrees/issue-3549-connection-plan/docs/plans/2026-07-16-issue-3549-registry-connection-helpers.md` lines 1-380 with `nl -ba`.
- Read `docs/superpowers/specs/2026-07-15-3549-registry-connection-helpers-design.md` lines 1-290.
- Read `src/workspace_hub/workstations/resolver.py` lines 1-120.
- Read `config/workstations/registry.yaml` lines 1-220.
- Read current connection wrappers and Tabby config under `scripts/operations/connection/` and `config/tabby/config.yaml`.
- Read `scripts/enforcement/install-hooks.sh` lines 1-220.
- Checked file existence with `rg --files`, `git ls-files`, `find`, and `ls` for the plan’s artifact map and files-to-change paths.
- Verified live issue/PR state with `gh issue view 3547/3548/3549/3550` and `gh pr view 3553`.
- Inspected PR #3553 file list and diffs for `docs/ops/remote-linux-access.md`, `config/tabby/REMOTE_ACCESS.md`, and `config/tabby/TAILSCALE_SETUP.md`.
- Grep’d endpoint/operator literals across `scripts/operations/connection`, `config/tabby`, `docs/modules/cli`, `docs/ops`, `config/workstations/registry.yaml`, and workstation tests.
- Ran inherited baseline: `uv run pytest tests/workstations/test_machine_path_resolver.py tests/workstations/test_registry.py tests/workstations/test_dev_secondary_ground_truth.py -q`.
- Checked local tool availability for `shellcheck`, `gitleaks`, and `pwsh`.
- Read `scripts/workflow/render_completeness_html.py` lines 1-75.

## Findings
1. Plan AC lines 325-327 requires “the changed-path manifest equals the reviewed file map,” and implementation line 277 says it will compare the changed-path set with “this plan’s artifact map,” but the Artifact Map at lines 98-117 is not the Files to Change table at lines 180-208. Required changed files missing from the Artifact Map include `.github/workflows/connection-helper-parity.yml`, `scripts/enforcement/check-connection-helper-endpoints.py`, `scripts/enforcement/install-hooks.sh`, `config/tabby/QUICK_REFERENCE.md`, `config/tabby/INTERNET_ACCESS_SUMMARY.md`, `docs/modules/cli/WORKSPACE_CLI.md`, `docs/modules/cli/SCRIPT_ORGANIZATION.md`, `docs/ops/remote-linux-access.md`, and `docs/plans/README.md`. This makes the closeout equality gate ambiguous and likely impossible to satisfy.

2. Plan line 203 marks `docs/ops/remote-linux-access.md` as `Modify`, and lines 44-47 treat it as consulted authority, but the file is absent in this worktree and `git ls-files docs/ops/remote-linux-access.md` returns nothing. PR #3553 does create it, but `gh pr view 3553` shows that PR is still OPEN/draft. The plan needs to make this row explicitly dependency-conditional or describe the post-merge rebase point as the source of the file before it can be modified.

3. Plan AC lines 329-331 requires “Pinned Gitleaks default rules” and an archive scan, but the plan has no artifact or command that pins or installs Gitleaks. Local verification found `gitleaks: MISSING`; the existing `scripts/security/secrets-scan.sh` lines 21 and 62 use the repo `.gitleaks.toml` and fail if `gitleaks` is not already installed, which conflicts with the AC’s “without using the repository’s currently ruleless custom configuration” requirement.

4. Plan AC lines 336-338 gives `uv run python scripts/workflow/render_completeness_html.py 3549 "Registry-driven connection helpers"` as the render command, but `scripts/workflow/render_completeness_html.py` line 72 reads JSON from stdin via `json.load(sys.stdin)`. The plan does not specify the completeness JSON producer or stdin redirection, so the acceptance command is incomplete and not reproducible.

## Blockers
- Finding 1
- Finding 2
- Finding 3
- Finding 4
