# Plan for #4473: fix(cron): preserve pull collisions and expose missing seat usage status

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-11-04
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/4473
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-11-04-plan-4473-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/readiness/build-equality-matrix.py` lines 862–869 — writes `{date.today().isoformat()}-machine-equality-matrix.html` to `REPORTS = REPO / "docs" / "reports"` on every scheduled run; also writes stable `machine-equality-matrix.html` alias; dated file lands in git-tracked checkout, blocking fast-forward pulls
- Found: `scripts/fleet/collect_account_usage_fleet.py` line ~349 — when all per-account probes fail, writes `{"account": None, "reason": "no live sample for any account"}` to `recommendation[prov]`; per-seat probe time and per-seat error reason are not surfaced
- Found: `scripts/fleet/collect_account_usage_fleet.py` lines ~308–320 — `samples[acct]` accumulates per-seat probes; `accounts_out[acct]` rows are built from these but `source` and `error` fields are not forwarded into the recommendation when ranking fails
- Found: `tests/readiness/test_build_equality_matrix.py` — existing test file for the matrix; new seam tests will extend this file
- Gap: `scripts/readiness/build-equality-matrix.py` has no `--dated-output-dir` or `--no-dated` CLI argument; dated output path is hard-coded relative to `REPO`
- Gap: `scripts/fleet/collect_account_usage_fleet.py` recommendation block lacks a `seats` or `probe_summary` field listing per-seat status when all probes fail

### Standards

| Standard | Status | Source |
|---|---|---|
| N/A — internal cron/scheduler tooling | — | — |

### LLM Wiki pages consulted

- No relevant wiki pages for cron/pull-collision patterns in this repo.

### Documents consulted

- Issue [#4473](https://github.com/vamseeachanta/workspace-hub/issues/4473) — specifies two root causes: (1) dated HTML pull collision from scheduled matrix run, (2) silent per-seat usage drop in fleet collector
- `docs/plans/2026-09-03-issue-3816-generated-work-surface-inventory.md` — different scope (repo adapter coverage), but confirms the pattern of output-seam design for scheduled scripts
- `scripts/ai/assessment/collect-account-usage.py` — per-seat probe format: `source` and `error` fields carry result reason; exits 0 even when both providers unavailable

### Gaps identified

- No `--dated-output-dir` or `--no-dated` CLI parameter in `build-equality-matrix.py` — dated file cannot be redirected without modifying the script
- No per-seat `source`, `error`, or `captured_at` forwarded in fleet collector recommendation when all accounts fail

### Evidence (embedded verification)

**Issue statuses** (verified 2026-11-04T via `gh issue view`):
- `#4473` — OPEN — fix(cron): preserve pull collisions and expose missing seat usage status

**File existence** (`ls` 2026-11-04):
- EXISTS: `scripts/readiness/build-equality-matrix.py`
- EXISTS: `scripts/fleet/collect_account_usage_fleet.py`
- EXISTS: `scripts/ai/assessment/collect-account-usage.py`
- EXISTS: `tests/readiness/test_build_equality_matrix.py`
- MISSING (new — this plan creates): `tests/fleet/test_collect_account_usage_fleet.py`

**Line excerpts** (`sed -n 858,875p scripts/readiness/build-equality-matrix.py`):
```
    REPORTS.mkdir(parents=True, exist_ok=True)
    out = REPORTS / f"{date.today().isoformat()}-machine-equality-matrix.html"
    out.write_text(html, encoding="utf-8")
    # Stable (undated) alias so GitHub Pages serves a fixed "latest" URL that never
    # changes as the dated reports roll over (published by scripts/build_pages.py).
    latest = REPORTS / "machine-equality-matrix.html"
    latest.write_text(html, encoding="utf-8")
    print(f"wrote {out} (+ {latest.name} alias) ({reporting}/{active} active reporting)")
```

**Line excerpts** (`grep -n "recommendation\|no live sample" scripts/fleet/collect_account_usage_fleet.py`):
```
343:    recommendation: dict[str, dict] = {}
349:            recommendation[prov] = {"account": None, "reason": "no live sample for any account"}
360:        recommendation[prov] = rec
```

**Gap proofs**:
- `grep -c "\-\-output\|\-\-dated\|dated_out" scripts/readiness/build-equality-matrix.py` → 0 → no existing output-dir CLI argument
- `grep -c "probe_summary\|probe_status\|\"seats\"" scripts/fleet/collect_account_usage_fleet.py` → 0 → no per-seat probe forwarding in recommendation

**Reproduction proofs**:
```
$ cd /mnt/local-analysis/workspace-hub && git status docs/reports/
# On a live scheduled run, docs/reports/YYYY-MM-DD-machine-equality-matrix.html
# appears as an untracked file, blocking git pull --ff-only.
# Root cause confirmed statically at build-equality-matrix.py lines 862–865.
```
- Reproduced at: 2026-11-04 (static analysis)
- Failure mode matches issue claim: YES — dated file written to git-tracked directory on every scheduler invocation; per-seat reason absent from recommendation when all probes fail

<!-- Verification: distinct sources — issue body (#1), build-equality-matrix.py (#2), collect_account_usage_fleet.py (#3), collect-account-usage.py (#4), prior plan #3816 (#5). Current count: 5 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-11-04-issue-4473-cron-pull-collision-seat-status.md |
| Tests (matrix, extended) | `tests/readiness/test_build_equality_matrix.py` |
| Tests (fleet, new) | `tests/fleet/test_collect_account_usage_fleet.py` |
| Implementation — matrix | `scripts/readiness/build-equality-matrix.py` |
| Implementation — fleet | `scripts/fleet/collect_account_usage_fleet.py` |
| Plan review — Claude | scripts/review/results/2026-11-04-plan-4473-claude.md |
| Plan review — Codex | scripts/review/results/2026-11-04-plan-4473-codex.md |
| Plan review — Gemini | scripts/review/results/2026-11-04-plan-4473-gemini.md |

---

## Deliverable

`build-equality-matrix.py` routes the dated HTML report through a new `--dated-output-dir` seam (defaulting to `docs/reports/`), keeping only the stable alias in the tracked checkout on cron runs using `--no-dated`; `collect_account_usage_fleet.py` publishes per-seat probe status and probe time in the recommendation block even when all collection attempts fail.

---

## Pseudocode

```
# build-equality-matrix.py fix
function write_reports(html, reports_dir, dated_out_dir, skip_dated):
    if not skip_dated:
        dated_out_dir.mkdir(parents=True, exist_ok=True)
        out = dated_out_dir / f"{date.today().isoformat()}-machine-equality-matrix.html"
        out.write_text(html)
    # stable alias stays in reports_dir (tracked, stable GitHub Pages URL)
    latest = reports_dir / "machine-equality-matrix.html"
    latest.write_text(html)

CLI additions:
    --dated-output-dir DIR   write dated file to DIR instead of REPORTS (default: REPORTS)
    --no-dated               skip writing the dated file entirely; write stable alias only
```

```
# collect_account_usage_fleet.py fix — in build_recommendation()
if not ranked:
    seats = {}
    for acct, row in accounts_out.items():
        if row["provider"] != prov:
            continue
        seats[acct] = {
            "source": row.get("source", "unavailable"),
            "error": row.get("error"),
            "captured_at": row.get("captured_at"),
            "hosts": row.get("hosts"),
        }
    recommendation[prov] = {
        "account": None,
        "reason": "no live sample for any account",
        "seats": seats,
    }
    continue
# existing logic for ranked accounts unchanged
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/readiness/build-equality-matrix.py` | add `--dated-output-dir` / `--no-dated` CLI args; route dated file through seam |
| Modify | `scripts/fleet/collect_account_usage_fleet.py` | forward per-seat source/error/captured_at into recommendation when all probes fail |
| Extend | `tests/readiness/test_build_equality_matrix.py` | TDD: disposable git repo; assert dated file lands in custom dir when flag set; assert stable alias still written to REPORTS |
| Create | `tests/fleet/test_collect_account_usage_fleet.py` | TDD: stubbed probe responses; assert recommendation carries `seats` with per-seat status when all accounts fail |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_matrix_dated_file_in_custom_dir | `--dated-output-dir` routes dated file to specified dir | disposable repo; `--dated-output-dir /tmp/out` | dated HTML written to /tmp/out, NOT to `docs/reports/` |
| test_matrix_stable_alias_in_reports | stable alias always written to `docs/reports/` | disposable repo; default and custom dated-dir modes | `machine-equality-matrix.html` present in `docs/reports/` |
| test_matrix_no_dated_flag | `--no-dated` skips writing any dated file | disposable repo; `--no-dated` | no `2026-*-machine-equality-matrix.html` in `docs/reports/` |
| test_matrix_no_untracked_after_run | no untracked dated file left in clean repo with `--no-dated` | disposable git repo; `--no-dated` | `git status --porcelain docs/reports/` returns empty |
| test_fleet_recommendation_carries_seats_on_all_fail | recommendation includes per-seat status when all probes fail | stubbed accounts_out: two accounts, both source=unavailable | `recommendation["claude"]["seats"]` has both account entries with source/error |
| test_fleet_recommendation_nominal_unchanged | successful probe keeps existing recommendation structure without `seats` | one account with live sample | recommendation has account/headroom_pct/hosts; no `seats` key |

---

## Acceptance Criteria

- [ ] `uv run pytest tests/readiness/test_build_equality_matrix.py -v` passes (existing + 4 new tests)
- [ ] `uv run pytest tests/fleet/test_collect_account_usage_fleet.py -v` passes (2 new tests)
- [ ] Running `build-equality-matrix.py --no-dated` produces no dated file in `docs/reports/`
- [ ] Running `build-equality-matrix.py --dated-output-dir /tmp/x` writes dated file to `/tmp/x/`, not `docs/reports/`
- [ ] The stable `machine-equality-matrix.html` alias is still written to `docs/reports/` in all modes
- [ ] `collect_account_usage_fleet.py` recommendation block includes `seats` mapping with per-seat source, error, and captured_at when all probes fail
- [ ] No regression: `uv run pytest tests/ -x --ignore=tests/quarantine` passes

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | — | pending |
| Codex | — | pending |
| Gemini | — | pending |

**Overall result:** pending (plan is draft)

Revisions made based on review:
- (none yet)

---

## Retention

**Basis:** [Boundary policy, Section 8.1](../document-intelligence/durable-vs-transient-knowledge-boundary.md#81-retention-schedule)

```json
{
  "issue": "#4473",
  "artifact_class": "plan",
  "issue_state": "open",
  "closed_on": null,
  "retention_days": 30,
  "retention_basis": "../document-intelligence/durable-vs-transient-knowledge-boundary.md#81-retention-schedule",
  "retention_status": "advisory",
  "disposition": "archive"
}
```

No fixed expiry while issue is open.

---

## Risks and Open Questions

- **Risk:** The cron schedule may invoke `build-equality-matrix.py` with no arguments; the `--no-dated` default must remain backward-compatible — the cron command line will need an explicit update to suppress the dated file
- **Risk:** `docs/reports/machine-equality-matrix.html` is published via GitHub Pages; changing the write logic for the dated file must not disturb the stable alias write path
- **Open:** Should `--no-dated` become the cron default (cron command updated), or should `--dated-output-dir` point to a non-tracked scratch dir? Flag for user during approval.

---

## Complexity: T2

**T2** — two existing scripts modified, two test files (one extended, one new), disposable git repo fixture required for pull-collision regression.
