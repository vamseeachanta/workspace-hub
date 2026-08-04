---
name: feedback-scheduler-audit-digest-covers-ci-workflows
description: "The scheduler audit HTML digest covers the CI workflows and all scripts, not just scheduler config — and --check-html reads disk vs index, which fakes failures on a lagging local main"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c2b08463-0428-41e0-83ad-03ab287f4328
  modified: 2026-08-01T16:26:20.274Z
---

Two traps in `scripts/enforcement/check-scheduler-mutation-surfaces.py`, both hit on 2026-08-01.

## 1. `--check-html` compares DISK against INDEX

`check-scheduler-mutation-surfaces.py:347` does `args.check_html.read_bytes()` — the HTML is read
**from the working tree**, while the render it is compared against is built from the **git index**
(`read_index_records`, `:88`). Two different sources.

On `/mnt/local-analysis/workspace-hub`, local `main` is routinely several commits behind (the
auto-sync owns it, and fast-forwards get blocked by cron-generated files). So an on-disk HTML that
lags the index produces `ERROR: HTML audit is stale` **that is purely a local artifact**.

**I misread this as "I broke main" and said so.** The disproof: regenerating produced a blob
byte-identical to main's, so the "fix" branch had a tree identical to its base — an empty commit.

**Rule: before claiming main is broken, check the workflow's own conclusion for that SHA:**
`gh run list --repo <r> --workflow scheduler-mutation-main.yml --limit 2 --json status,conclusion,headSha`.
That is authoritative and one command away. A local checker result is not.
See [[feedback_verify_generated_state_against_origin_not_working_copy]].

## 2. The audit digest covers the CI workflows themselves

`scripts/enforcement/scheduler_mutation_contract.py:154-171` — `digest_record_union` includes the
checker source, its sibling modules, its tests, **and**:

- `.github/workflows/enforcement-gate.yml`
- `.github/workflows/scheduler-mutation-main.yml`

This is deliberate and good: the attestation covers *the enforcement configuration*, so a step
cannot be silently deleted from CI without invalidating the signed audit. Consequence — **editing
either workflow requires regenerating the audit HTML**, and a PR that *adds* a check trips the same
wire. Diagnosed by reproducing with an index of `origin/main` plus only the workflow change: the
sole diff in the rendered HTML was the embedded `input_digest`.

The render also scans **every** script under `scripts/` via `discover_mutation_surfaces()`, so
"this file contains no scheduler primitive" is NOT sufficient reason to skip `--check-html`.

**Rule: after touching anything in the digest union — scheduler config, any `scripts/**` file, the
checker, its tests, or those two workflows — run all three:**

```
uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py
uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py --check-html docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html
uv run python scripts/cron/build-cron-identity-inventory.py --check
```

Order matters: **stage first, then `--render-html`, then stage the HTML** — the render reads the
index, so rendering before staging produces an audit stale on arrival.

Related: [[project_claude_md_harness_retired]], [[feedback_absence_of_signal_reads_as_success]],
[[feedback_non_required_checks_hide_regressions]].
