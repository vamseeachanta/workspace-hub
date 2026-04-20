# AceEngineer Website — Ecosystem Sync Cycle

- **Date:** 2026-04-19
- **Status:** Draft — awaiting user review
- **Owner:** vamseeachanta
- **Target repo:** `vamseeachanta/aceengineer-website`
- **Runner host:** `ace-linux-1` (local systemd cron)
- **Related memory:** `daily_readiness_cron` (pattern precedent), `data_format_guidelines` (YAML default), `feedback_retry_loop_reset_hazard` (no blind `git reset` in retry loops), `feedback_gh_issue_close_silent_comment_drop` (don't auto-close issues)

## Purpose

Establish a daily automated sync that reviews a curated set of public engineering repositories in the AceEngineer ecosystem and surfaces website-worthy changes as:

1. A human-readable markdown **digest** written to `workspace-hub/docs/sync-reports/YYYY-MM-DD.md`, and
2. **GitHub issues** opened on `vamseeachanta/aceengineer-website` when concrete signals cross a threshold — which the user triages into content updates.

The cron never edits site content (HTML/assets/blog) and never writes to the 6 source repos. All website changes remain human-gated through the issue-triage workflow.

## Scope

**In scope (v1):**

- Six public-facing engineering repos as read-only inputs:
  - `digitalmodel`
  - `assethold`
  - `assetutilities`
  - `CAD-DEVELOPMENTS`
  - `doris`
  - `frontierdeepwater`
- Local cron on `ace-linux-1`, daily at 6:00 AM CT.
- Four signal detectors (release tags, new case studies, README capability diffs, labeled closed issues).
- Idempotent digest writes + deduped issue filing via `gh` CLI.
- Preparatory one-time PR across the 6 repos to standardize README section headings (`Capabilities` / `Features` / `What it does`) and create `showcase` + `website` labels.

**Out of scope (deferred to later phases):**

- Automated draft PRs that edit site HTML or case-studies directly (Approach 3 from brainstorm).
- Public-facing digest (current design keeps digest inside workspace-hub).
- Private or client repos (`client_projects`, `achantas-data`, `investments`, etc.).
- Signal detectors for commit volume or new top-level modules (too noisy for v1).
- Non-daily cadence (weekly summaries, on-demand runs beyond `--dry-run` / `--doctor`).

## Non-goals

- **Auto-publishing to the website.** Cron cannot edit `aceengineer-website/*.html`, blog, or assets. Ever.
- **Auto-closing issues.** Cron only creates. User closes.
- **Perfect signal recall.** Conservative dedupe + false-positive guards are preferred over catching every possible update. A missed day is cheaper than a flood of bad issues.
- **Parallelism inside a run.** Six repos sequential; saving ~20s is not worth harder log reading.

## Architecture

```
[systemd cron, ace-linux-1, 06:00 CT daily]
        │
        ▼
[.claude/cron/ecosystem-sync.sh]               entry point, flock-guarded, logs
        │
        ▼
[scripts/ecosystem-sync/run.py]                orchestrator (uv run)
        │
        ├── load config.yaml + last-sync.yaml
        ├── for each of 6 repos (sequential):
        │       git fetch origin --tags --prune
        │       signals += detect_release_tag(...)
        │       signals += detect_new_case_study(...)
        │       signals += detect_readme_capability_diff(...)
        │       signals += detect_showcase_labeled_closed_issues(...)   # uses gh
        │
        ├── write docs/sync-reports/YYYY-MM-DD.md  (overwrite on re-run)
        ├── open_issue_if_new(signal)              for each signal, deduped via gh search
        │                                          hard cap 20 issues per run
        │
        ├── update last-sync.yaml with new shas/tags/hashes/issue-ids
        └── git add/commit/push                    single attempt → on reject: one
                                                   `git pull --rebase` → re-push → if
                                                   still fails OR conflict: exit non-zero
```

### Boundaries

- **Read-only** on the 6 source repos (only `git fetch`, never `git push`).
- **Write-only** on workspace-hub (`docs/sync-reports/` + state file + commit).
- **Issue-only** on `aceengineer-website` (only `gh issue create` + dedupe via `gh issue list`).
- **Single-process** — one Python orchestrator, no queues/daemons.
- **Idempotent** — same day re-run overwrites digest, dedupes issues, no duplicate commits.

## Components

Five files, each under ~200 lines.

| # | Path | Responsibility |
|---|------|----------------|
| 1 | `.claude/cron/ecosystem-sync.sh` | Cron entry. flock pidfile, `git pull --ff-only` on workspace-hub, invoke `uv run run.py`, append exit/duration to `logs/ecosystem-sync/YYYY-MM-DD.log`. |
| 2 | `scripts/ecosystem-sync/run.py` | Orchestrator. Loads config/state, iterates repos, calls detectors, writes digest, calls issue-opener, persists state. No detection or I/O logic beyond this wiring. Supports `--dry-run` and `--doctor` flags. |
| 3 | `scripts/ecosystem-sync/signals.py` | Detector functions (pure for signals 1–3; signal 5 invokes `gh issue list` for labeled closed issues). `detect_release_tag`, `detect_new_case_study`, `detect_readme_capability_diff`, `detect_showcase_labeled_closed_issues`. Each returns `list[Signal]`. |
| 4 | `scripts/ecosystem-sync/digest.py` | Pure `render_digest(signals_by_repo, skipped, date) -> str`. No I/O. Golden-file testable. |
| 5 | `scripts/ecosystem-sync/issues.py` | `open_issue_if_new(signal)`. Checks existing issues via `gh issue list` before `gh issue create`. Never edits or closes. Retry-once on transient `gh` errors. |

### Config — `scripts/ecosystem-sync/config.yaml`

```yaml
repos:
  - name: digitalmodel
    path: /mnt/local-analysis/workspace-hub/digitalmodel
    readme_sections: ["Capabilities", "Features"]
  - name: assethold
    path: /mnt/local-analysis/workspace-hub/assethold
    readme_sections: ["What it does", "Capabilities"]
  - name: assetutilities
    path: /mnt/local-analysis/workspace-hub/assetutilities
    readme_sections: ["Capabilities", "Features"]
  - name: CAD-DEVELOPMENTS
    path: /mnt/local-analysis/workspace-hub/CAD-DEVELOPMENTS
    readme_sections: ["Capabilities", "Features"]
  - name: doris
    path: /mnt/local-analysis/workspace-hub/doris
    readme_sections: ["Capabilities", "Features"]
  - name: frontierdeepwater
    path: /mnt/local-analysis/workspace-hub/frontierdeepwater
    readme_sections: ["Capabilities", "Features"]
issue_repo: vamseeachanta/aceengineer-website
digest_dir: docs/sync-reports
state_file: .claude/state/ecosystem-sync/last-sync.yaml
max_issues_per_run: 20
```

### State — `.claude/state/ecosystem-sync/last-sync.yaml`

```yaml
digitalmodel:
  last_sync_utc: 2026-04-19T11:00:00Z
  last_commit_sha: a7b0fd4f
  last_seen_tags: ["v2.1.3"]
  last_readme_hash:
    Capabilities: "sha256:ab12…"
    Features: "sha256:cd34…"
  last_case_studies: ["docs/case-studies/mooring-failures.md"]
  last_closed_showcase_issues: [1823, 1901]
assethold:
  # …same shape
```

Git-tracked. Agent-facing structured data → YAML (per `data_format_guidelines`).

## Daily run sequence

```
T+0s    cron fires ecosystem-sync.sh
T+1s    flock grabs /tmp/ecosystem-sync.lock
          → if held, log "previous run in progress, skipped" and exit 0
T+2s    cd workspace-hub
        git pull --ff-only origin main
          → on fail: exit non-zero (alert fires)
T+3s    uv run scripts/ecosystem-sync/run.py

          run.py:
          ├─ load config.yaml
          ├─ load last-sync.yaml
          │    → if missing/unparseable: exit non-zero (alert fires)
          ├─ for each of 6 repos (sequential):
          │     try:
          │       git -C <path> fetch origin --tags --prune    (30s timeout)
          │       signals += detect_release_tag(...)
          │       signals += detect_new_case_study(...)
          │       signals += detect_readme_capability_diff(...)
          │       signals += detect_showcase_labeled_closed_issues(...)
          │     except Exception as e:
          │       skipped[repo] = str(e)
          │       log traceback; continue
          │
          ├─ digest_md = render_digest(signals_by_repo, skipped, today)
          ├─ write docs/sync-reports/YYYY-MM-DD.md             (overwrite if re-run)
          │
          ├─ to_file = signals[:20]                            (hard cap)
          │  suppressed = signals[20:]
          │  digest appended with "Suppressed signals" section listing all in suppressed
          │
          ├─ for signal in to_file:
          │     open_issue_if_new(signal)                      (gh search dedupes)
          │
          ├─ update last-sync.yaml (only if changed)
          └─ git add + commit + push
                → on reject: one `git pull --rebase`
                  → if rebase clean: re-push
                    → on re-push fail: exit non-zero
                  → if rebase conflicts: `git rebase --abort`; exit non-zero

T+~60s  lock released; exit code + counts appended to daily log
```

### Dedupe rules

- **Digest file**: overwrite-in-place on re-run — same inputs → same output.
- **State file**: commit only if substantive state changed — new tags, new commit sha, new case-study paths, changed README hash, or new closed-showcase issue IDs. `last_sync_utc` timestamp updates in the file but a timestamp-only diff is NOT committed (prevents daily empty-sync commits polluting history).
- **Issues**: dedupe key embedded in title prefix — e.g., `[sync] digitalmodel released v2.1.3`. `gh issue list` search is run before create. If matching open issue exists, append a comment noting re-run, do not file a duplicate.

## Signal detection rules

### Signal 1 — New release / version tag

- **Triggers when:** `git tag -l` produces tags not in `state[repo].last_seen_tags`, matching `^v?\d+\.\d+(\.\d+)?$`.
- **Dedupe key:** `release:<repo>:<tag>`.
- **Issue title:** `[sync] <repo> released <tag>`.
- **Body:** `git log <previous-tag>..<tag> --oneline` (top 20) + proposed website update (add to changelog/releases page).
- **Guards:** skip `^nightly-`, `^snapshot-`, `^pre-`; skip tags whose commit is >90 days old.

### Signal 2 — New case study / example file

- **Triggers when:** `git diff --name-status <last_commit_sha>..HEAD -- case-studies/ examples/ demos/ docs/case-studies/` shows status `A`.
- **Dedupe key:** `case-study:<repo>:<file-path>`.
- **Issue title:** `[sync] <repo> added <basename>`.
- **Body:** first 40 lines of the new file + proposed website update (lift into `aceengineer-website/case-studies/`).
- **Guards:** skip `README.md`, `*.template.md`, `CASE_STUDY_TEMPLATE.md`; skip paths containing `/_draft/`, `/wip/`, `/archive/`.

### Signal 3 — README capability section diff

- **Triggers when:** for each configured `readme_sections` heading, extract section body, SHA-256 it, compare to `state[repo].last_readme_hash[heading]`. Fire on mismatch.
- **Dedupe key:** `readme-diff:<repo>:<heading>:<new-hash-prefix-8>`.
- **Issue title:** `[sync] <repo> README "<heading>" section changed`.
- **Body:** unified diff + proposed website update (reflect in engineering.html / about.html).
- **Guards:** normalize whitespace before hashing. Skip diffs that are only issue/PR number references (`#\d+`).

### Signal 5 — Closed issues with `showcase` or `website` label

- **Triggers when:** `gh issue list --repo <repo> --label showcase --state closed --search 'closed:>=<last_sync_date>'` returns issue numbers not in `state[repo].last_closed_showcase_issues`. Repeat with `--label website`.
- **Dedupe key:** `showcase:<repo>:<issue-number>`.
- **Issue title:** `[sync] <repo> #<num>: <original title>`.
- **Body:** upstream body (truncated to 500 words) + link + proposed website update (blog post / case study).
- **Guards:** skip if label includes `not-planned` or closed as `duplicate`.

### Signal ordering and limits

- Detection order per repo: 1 → 2 → 3 → 5.
- **Hard cap: 20 issues filed per run, total.** Overflow listed in digest's "Suppressed signals" section, not filed.
- Digest always contains full list; issues are the triage surface.

## Error handling

| Failure | Behavior |
|---|---|
| `flock` lock held | Exit 0, log "previous run in progress, skipped". |
| `git pull` on workspace-hub fails | Exit non-zero, alert fires. |
| `last-sync.yaml` missing/unparseable | Exit non-zero, alert fires. |
| `git fetch` on a source repo fails | Skip repo; digest shows `⚠ <repo>: fetch failed — <reason>`; continue. |
| `gh issue create` fails | Retry once after 10s; if still fails, digest notes "⚠ N signals could not be filed"; do not abort run. |
| `gh issue list` (dedupe) fails | Treat as "unknown — do not file from this repo"; digest notes "⚠ dedupe check failed for <repo>". |
| Detector exception | Log traceback; skip that signal type for that repo; continue. |
| 20-issue cap reached | File first 20; remainder in "Suppressed signals" section. |
| Commit rejected | One `git pull --rebase`; if clean, re-push; if conflict, `rebase --abort`; exit non-zero. |

**Rule of thumb:** a bad day must not poison good days. State corruption + workspace-hub pull failure are the only non-zero exits. Everything else degrades and surfaces in the digest.

## Testing

- **`tests/ecosystem-sync/test_signals.py`** — one class per detector, fixture repos under `tests/fixtures/`, assertions on signal output + dedupe keys + guard behavior.
- **`tests/ecosystem-sync/test_digest.py`** — golden-file tests. Given a fixed `signals_by_repo`, `render_digest()` produces exactly the snapshot markdown.
- **`tests/ecosystem-sync/test_issues.py`** — mocks `gh` subprocess. Verifies dedupe-before-create, retry-once, graceful failure.
- **`tests/ecosystem-sync/test_run.py`** — integration wiring test with mocked subprocess layer.
- **Manual pre-launch smoke**: `bash .claude/cron/ecosystem-sync.sh --dry-run` run 2–3 times over different days before enabling the systemd timer.

## Observability

Three artifacts:

1. **Digest** — `docs/sync-reports/YYYY-MM-DD.md`, always written (even if zero signals). Footer: `Run: HH:MM:SS CT · Duration: Ns · Repos OK: X/6 · Signals: N · Issues filed: M · Next run: tomorrow 06:00 CT`.
2. **Log** — `logs/ecosystem-sync/YYYY-MM-DD.log`, append-only, rotated by `logrotate`. `logs/` gitignored.
3. **Issue titles** — all prefixed `[sync]`. `gh issue list --repo vamseeachanta/aceengineer-website --search "[sync]"` shows the full history.

**Alerting**: piggyback the existing `daily_readiness_cron` alert channel. Non-zero exit → alert.

**Health check**: `uv run scripts/ecosystem-sync/run.py --doctor` — validates config, repo paths, `gh auth status`, state file parseable, digest dir writable. Exits 0 if healthy.

## Preparatory work (one-time, before enabling cron)

A preparatory PR across the 6 source repos that:

1. Standardizes top-level README to contain at least one of `## Capabilities` / `## Features` / `## What it does` with consistent formatting.
2. Creates `showcase` and `website` labels on each repo via `gh label create`.
3. Back-fills `last-sync.yaml` with current state (tags, README hashes, zero case studies / showcase issues so the first cron run doesn't flood).

This PR is a precondition for enabling the cron. Without it, Signal 3 has nothing consistent to hash and Signal 5 has no labels to query.

## Roll-out sequence

1. Land preparatory PR (README standardization + label creation + backfilled state file).
2. Merge the five component files + tests.
3. Run `--doctor` on `ace-linux-1`; fix anything that fails.
4. Run `--dry-run` for 2–3 days, hand-inspect digests.
5. Enable systemd cron unit.
6. Monitor for 1 week; iterate on signal guards if false positives appear.

## Open risks

- **README drift across repos**: even after standardization, a contributor may later rename a heading. Mitigation: Signal 3 already no-ops silently if the heading is absent (logs a debug note); worst case is missed signals, not bad ones.
- **`gh` auth expiring on `ace-linux-1`**: `--doctor` catches this at run time. Consider a weekly cron that runs `gh auth status` and alerts if it degrades.
- **Backfill day**: first production run after prep-PR may fire many signals for pre-existing state. The 20-issue cap prevents flooding but the user should expect a high-volume first day.
- **Workspace-hub commit-loop contention**: if another cron pushes to workspace-hub at 06:00 CT, the rebase path runs. Stagger cron times if a conflict is observed (e.g., this cron at 06:00, readiness cron at 06:15).

## References

- Pattern precedent: `daily_readiness_cron` (trigger `trig_019GWtRosbZ9rw1HxrGpsvy9`, 6am CT daily)
- Memory: `data_format_guidelines` (YAML for agent-facing structured data)
- Memory: `feedback_retry_loop_reset_hazard` (no `git reset` in retry loops)
- Memory: `feedback_gh_issue_close_silent_comment_drop` (don't auto-close issues)
- Brainstorm session: this conversation (2026-04-19)
