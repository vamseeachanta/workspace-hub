# #3549 Implementation Amendment — Slice C/D Resume

> **Status:** plan-review — round 3 MAJOR corrected inline; user decision required
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3549
> **Base plan:** `docs/plans/2026-07-16-issue-3549-registry-connection-helpers.md`
> **Candidate baseline:** `d9db0d7665c66736ae185e462213c92da9a65d82`
> **Lane:** lane:claude

## Goal and unchanged architecture

This amendment will authorize a focused command module and test module required
by the Python 400-line gate, correct the command-boundary findings with new
review-driven RED tests, and resume the approved hostname-first design. It will
not change explicit verified fallback, conventional host-key checking, the
single shell-free launch, or the no-retry rule.

The current WIP branch contains Slice A/B/C commits. They will remain preserved
but unapproved. Renewed user approval will authorize correction of that WIP; it
will not retroactively approve pre-amendment commits.

## Scope decisions

- `connection.py` and `test_connection_resolver.py` are 376 and 397 lines. New
  command behavior will remain in `connection_command.py`, and its tests will
  remain in `test_connection_cli.py`.
- `registry.yaml` is 405 lines in WIP. The next registry edit will remove at least
  five non-semantic blank/comment lines so the candidate is at most 400 lines.
- The 541-line `docs/plans/README.md` and 488-line
  `docs/modules/cli/WORKSPACE_CLI.md` will remain byte-identical to the candidate
  baseline. Their pre-existing debt will not expand this issue.
- `scripts/workspace` will remain unchanged. Its connection paths already do not
  exist, the file is 575 lines, and Windows fallback must exit 4. Follow-on
  [#3561](https://github.com/vamseeachanta/workspace-hub/issues/3561) will own its
  split, path repair, explicit machine selection, and documentation.

## Review-driven TDD corrections

### CLI option and launch matrix

`tests/workstations/test_connection_cli.py` will add exact RED cases before any
production correction:

| Stimulus | Expected exit | Expected stderr |
|---|---:|---|
| each abbreviation `--fall`, `--dry`, `--reg`, `--over`, `--use` | 2 | exact redacted usage class |
| exact `--fallback` | existing domain result | proves the real option remains accepted |
| runner raises `OSError(errno.ENOENT, secret)` | 127 | `error: ssh_client: missing` only |
| runner raises `PermissionError(errno.EACCES, secret)` | 126 | `error: ssh_client: not_executable` only |
| runner raises `OSError(errno.ENOEXEC, secret)` | 126 | `error: ssh_client: not_executable` only |
| runner raises `OSError(errno.E2BIG, secret)` | 126 | `error: ssh_client: not_executable` only |
| runner raises `FileNotFoundError(errno.EACCES, secret)` | 126 | proves errno, not subclass, controls mapping |
| runner raises `PermissionError(errno.ENOENT, secret)` | 127 | proves errno, not subclass, controls mapping |
| runner raises `FileNotFoundError(None, secret)` | 126 | proves a missing errno cannot become 127 |
| child returns `-signal.SIGINT` | 130 | no synthesized endpoint/identity detail |
| child returns `7` | 7 | unchanged child status |

Every abbreviated option will assert zero resolver/runner calls; exact
`--fallback`, `--dry-run`, `--registry-path`, `--overlay-path`, and `--user` will
remain accepted controls. Every launch exception row will assert the secret is
absent and the runner is called exactly once. The parser will set
`allow_abbrev=False`. Launch mapping
will return 127 only for `ENOENT`, 130 for `KeyboardInterrupt` or child SIGINT,
126 for every other pre-child `OSError`, and the unchanged child status otherwise.

### Registry versus overlay error boundary

Command-level RED tests will inject errors after registry policy resolution:

| Overlay stimulus | Expected exit | Exact stderr |
|---|---:|---|
| monkeypatched leaf `os.open(..., dir_fd=parent_fd)` raises `FileNotFoundError(errno.ENOENT, secret)` | 4 | `error: overlay.file: unavailable` |
| raw `OSError(errno.EIO, secret)` representing post-open/read I/O | 5 | `error: overlay.file: io_failure` |
| `OverlayIntegrityError("overlay.file", "digest_mismatch")` | 5 | `error: overlay.file: digest_mismatch` |

The ENOENT test will enter through `main`, use a valid registry/policy and real
overlay loader, and fail at the leaf filesystem boundary—not by injecting an
already-classified domain exception. The EIO test will inject after the leaf is
opened/read. Each case will assert the secret, endpoint, identity, and
registry-unavailable class are absent, and the runner is never called. Registry file/policy resolution
will keep its narrow exit-3 block. Overlay domain errors will retain exits 4/5;
otherwise-unclassified overlay-local `OSError` will become redacted exit 5.

### Executable and platform regression checks

Direct executable mode is already green and will be treated as regression
coverage, not a promised RED. A test will invoke the executable script without
`sys.executable`, from a non-repository CWD and a copied checkout path containing
spaces, and will verify the shebang/mode boundary.

Native Windows tests will invoke both PowerShell wrappers from a non-repository
CWD and a copied path containing spaces. For each wrapper they will pass two
distinct explicit machine IDs (`node-alpha`, `node-beta`) and capture the exact
wrapper-to-CLI argv through a fake `uv.cmd`. The hostname cases will assert:

```text
uv run python <checkout>\scripts\operations\connection\connect-workstation.py <machine>
```

The Tailscale wrapper argv test will append the explicit fallback switch. A
separate required-native test will use real `uv`, real Python, and the real shared
CLI on `windows-latest`, with only `ssh.cmd` faked. It will invoke `node-beta
--fallback`, require exit 4 plus exact redacted `unsupported_platform` stderr,
and prove the SSH shim records zero invocations. The static contract test
will forbid command strings, `Start-Process`, legacy `-Method`, and tracked target
or operator defaults. Synthetic protocol addresses will be assembled at runtime;
no test source will contain an endpoint literal.

## Canonical Candidate Changed-Path Map

This table supersedes the base plan's changed-path table. The frozen candidate
set will be computed from `d9db0d7665c66736ae185e462213c92da9a65d82` and will
equal these rows plus the conditional runbook only when its predicate fires.

| Action | Path |
|---|---|
| Modify | `config/workstations/registry.yaml` |
| Modify | `src/workspace_hub/workstations/resolver.py` |
| Create | `src/workspace_hub/workstations/connection.py` |
| Create | `src/workspace_hub/workstations/connection_command.py` |
| Create | `scripts/operations/connection/connect-workstation.py` |
| Modify | `scripts/operations/connection/connect-workspace-tailscale.sh` |
| Modify | `scripts/operations/connection/connect-workspace-tailscale.ps1` |
| Modify | `scripts/operations/connection/ssh-dev-secondary.sh` |
| Modify | `scripts/operations/connection/connect-workspace-linux.sh` |
| Modify | `scripts/operations/connection/connect-workspace-windows.ps1` |
| Delete | `scripts/operations/connection/.fuse_hidden0002aeb10000414f` |
| Delete | `scripts/operations/connection/.fuse_hidden0002aeb100013f84` |
| Modify | `config/tabby/config.yaml` |
| Create | `config/workstations/connection-governed-paths.yaml` |
| Create | `scripts/enforcement/check-connection-helper-endpoints.py` |
| Modify | `scripts/enforcement/install-hooks.sh` |
| Create | `tests/workstations/test_connection_resolver.py` |
| Create | `tests/workstations/test_connection_cli.py` |
| Create | `tests/operations/test_connection_helpers_bash.py` |
| Create | `tests/operations/test_connection_helpers_ps1_contract.py` |
| Create | `tests/operations/test_connection_helpers_ps1_native.py` |
| Create | `tests/enforcement/test_connection_helper_endpoints.py` |
| Create | `.github/workflows/connection-helper-parity.yml` |
| Conditional | `docs/ops/remote-linux-access.md` — modify only if `connect-workstation.py`, `machine-local fallback overlay`, or `--dry-run` is absent; otherwise preserve it and record all three tokens |
| Modify | `config/tabby/QUICK_REFERENCE.md` |
| Modify | `config/tabby/INTERNET_ACCESS_SUMMARY.md` |
| Modify | `docs/modules/cli/SCRIPT_ORGANIZATION.md` |
| Modify | `docs/plans/2026-07-16-issue-3549-registry-connection-helpers.md` |
| Create | `docs/plans/2026-07-16-issue-3549-amendment.md` |
| Modify | `docs/reports/2026-07-16-issue-3549-registry-connection-helpers-plan.html` |
| Create | `.planning/plan-approved/3549.md` — user-created, revision-bound approval evidence |
| Create | `scripts/review/results/2026-07-16-plan-3549-amendment-security-round1.md` |
| Create | `scripts/review/results/2026-07-16-plan-3549-amendment-governance-round1.md` |
| Create | `scripts/review/results/2026-07-16-plan-3549-amendment-compatibility-round1.md` |
| Create | `scripts/review/results/2026-07-16-plan-3549-amendment-security-round2.md` |
| Create | `scripts/review/results/2026-07-16-plan-3549-amendment-governance-round2.md` |
| Create | `scripts/review/results/2026-07-16-plan-3549-amendment-compatibility-round2.md` |
| Create | `scripts/review/results/2026-07-16-plan-3549-amendment-security-round3.md` |
| Create | `scripts/review/results/2026-07-16-plan-3549-amendment-governance-round3.md` |
| Create | `scripts/review/results/2026-07-16-plan-3549-amendment-compatibility-round3.md` |

The six already-written review artifacts and final round-3 artifacts are
gitignored by default and will be force-added by exact path only. The governed
manifest will explicitly include `connection_command.py` and
`test_connection_cli.py`. `docs/plans/README.md`, `WORKSPACE_CLI.md`, and
`scripts/workspace` will be verified byte-identical to the baseline.

## Verification and approval gates

The automatic review loop stops after round 3. Renewed approval will require
either a final no-MAJOR review or an explicit user waiver of the round-3 verdicts
after inspecting this inline correction. The user—not the implementing agent—will:

1. apply `status:plan-approved` to issue #3549; and
2. create `.planning/plan-approved/3549.md` containing `Approved-by`, RFC-3339
   `Approved-at`, exact `Reviewed-commit`, the three round-3 artifact paths and
   SHA-256 digests, and either `Verdict: no-major` or
   `Waiver: round-3-major-after-inline-corrections`.

Before implementation, the orchestrator will mechanically require the live label
set to contain `status:plan-approved` and exclude `status:plan-review`; parse every
required marker field; match `Reviewed-commit` to the published inline-correction
commit; recompute all three artifact digests; and reject any other Verdict/Waiver
value. Implementation will remain blocked unless every check passes. After
approval, correction will use strict RED→GREEN TDD and run:

```text
Approved-by: <owner identity>
Approved-at: <RFC-3339 UTC timestamp>
Reviewed-commit: <40 lowercase hex>
Verdict: no-major
Artifact: <64 lowercase hex>  scripts/review/results/...-security-round3.md
Artifact: <64 lowercase hex>  scripts/review/results/...-governance-round3.md
Artifact: <64 lowercase hex>  scripts/review/results/...-compatibility-round3.md
```

For an explicit waiver, the `Verdict` line will be replaced by exactly
`Waiver: round-3-major-after-inline-corrections`. The preflight will obtain labels
with `gh issue view 3549 --json labels`, reject missing approved or remaining
review labels, validate field/hex/timestamp formats, require `Reviewed-commit` to
equal `git ls-remote origin refs/heads/feature/3549-registry-connection-helpers`,
and feed the three normalized `<sha>  <path>` entries to `sha256sum --check`.

```text
uv run pytest tests/workstations/test_connection_resolver.py tests/workstations/test_connection_cli.py tests/operations/test_connection_helpers_bash.py tests/operations/test_connection_helpers_ps1_contract.py tests/operations/test_connection_helpers_ps1_native.py tests/enforcement/test_connection_helper_endpoints.py -q
```

The candidate will also pass the inherited baseline, Ruff, the Python
400-line/50-line checker, `wc -l` at 400 or fewer for every changed file, Bash
syntax, ShellCheck, required-native Windows CI, legal scan, Gitleaks, exact
changed-path equality, adversarial code review, completeness, and cleanup gates.
