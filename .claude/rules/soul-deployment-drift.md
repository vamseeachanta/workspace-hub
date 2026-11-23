# Soul Deployment Drift — Universal

A machine must load what `origin/main` holds, not merely what its checkout
contains. Committed and pushed is not the same as in force.

## Why this rule exists

Measured 2026-09-10. Four machines carried correct, working symlinks into valid
checkouts and were 70, 88, 11 and 120 commits stale. Every one loaded the
engineering register; not one loaded the raw-data rule committed after it. A
fifth machine had no links at all and no symlink privilege to create them, and
had just completed work governed by the rule it was not loading.

Nothing reported any of this, because `check-soul-runtime-drift.sh` checks
whether committed artifacts match a rebuild from source — in-repo drift — and no
check looked past the repository.

## The check

    scripts/enforcement/check-soul-deployment-drift.sh [--quiet] [--no-fetch]

Compares the SHA-256 of each deployed provider file against the blob in
`origin/main`, for claude, codex, hermes, gemini and agy. Exit 1 on any stale or
absent deployment.

**It compares content, so the transport is a detail.** A symlink, a copy and a
hard link are all acceptable and all equally checked. That matters on accounts
without symlink privilege, where `install-soul-runtime.sh` refuses to leave a
copy because a copy "would rot invisibly" — with this gate it no longer rots
invisibly, and a refreshed copy is as good as a link.

The authority is the `origin/main` blob, never the working tree: a stale or dirty
checkout must not be able to declare itself current.

## Reading the output

A checkout behind on other paths while the runtimes match origin is **not** a
failure. That is the distinction the gate exists to draw: a stale checkout is
informational, a stale runtime is the failure.
