# Orchestrator consistency (#2841)

`scripts/cron/consistency-weekly-check.sh` writes a dated `YYYY-MM-DD-matrix.md` here each
weekly run (Sun 06:00, dev-primary). Those dated matrices are **gitignored** — they are
ephemeral run outputs. The **durable record on drift is the rolling `consistency-drift`
GitHub issue** (the check upserts ONE issue, updating its body each run rather than spawning
duplicates). This README is the only tracked file in the directory.

Lanes (per #2841): Claude / Codex+Hermes (2 quota-independent lanes). The check covers the
per-machine probe (#2860), SOUL runtime drift, dream dead-letters (#2845), read-back
freshness, and cron declarations.
