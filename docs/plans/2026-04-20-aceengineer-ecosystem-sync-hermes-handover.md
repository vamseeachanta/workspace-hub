# Handover: AceEngineer Ecosystem Sync — Tasks 7–11 + Adversarial Review of Tasks 1–6

**For:** Hermes agent (or any capable follow-on agent)
**From:** Claude Code session, 2026-04-20
**Mission:** (1) Adversarially review 6 commits already landed on branch `feat/ecosystem-sync` and produce a findings report. (2) Implement Tasks 7–11 of the plan with the same TDD discipline. Do NOT invoke the Stage-1 end-to-end review yet — that runs separately after Task 11 lands.

---

## Immutable facts you need before doing anything

- **Repo root (main worktree):** `/mnt/local-analysis/workspace-hub`
- **Feature worktree (where you work):** `/mnt/local-analysis/workspace-hub/.claude/worktrees/ecosystem-sync`
- **Feature branch:** `feat/ecosystem-sync` — 6 commits ahead of main.
- **Design spec:** `docs/plans/2026-04-19-aceengineer-ecosystem-sync-design.md` (commit `25921037e`)
- **Full implementation plan:** `docs/plans/2026-04-20-aceengineer-ecosystem-sync-plan.md` (commit `ad2c86fb7`) — 17 tasks. Only Tasks 7–11 of Stage 1 remain.
- **Plan-approval marker:** `.planning/plan-approved/ecosystem-sync.md` exists in the worktree so the pre-commit `require-plan-approval.sh` hook passes. Do NOT delete or rename this file.
- **Python runtime:** `uv run` — never bare `python`/`pytest` (standing user rule, memory key `uv_run_isolation`).
- **Commit convention:** `feat(ecosystem-sync): <short summary>` — no AI footers, no "Co-authored-by", no "Generated with …".

### Commits already on `feat/ecosystem-sync`

| # | SHA | Subject | Files |
|---|---|---|---|
| 1 | `5a37abf87` | scaffold package with Signal dataclass | models.py + symlink + tests |
| 2 | `53f9e841c` | config loader + 6-repo production config | config.py + config.yaml + tests |
| 3 | `87147eb35` | state load/save with timestamp-aware change detection | state.py + tests |
| 4 | `e2496a4d4` | signal 1 — release tag detector + fixtures | signals.py (initial) + fixture builder + .gitignore + tests |
| 5 | `ca2b12b55` | signal 2 — new case-study / example detector | signals.py (append) + tests |
| 6 | `8b8b0a9a5` | signal 3 — README capability section diff | signals.py (append) + tests |

Total: 21/21 tests passing on commit 6.

---

## PART A — Adversarial review of commits 1–6

**Mindset (non-negotiable):** You are hunting for defects, not confirming the plan was followed. Charitable reading is explicitly forbidden. Assume the implementers were tired, the controller was rushed, and the tests are optimistic. Your job is to find everything that might break in production.

Review target: `git diff 00a3ffc38..8b8b0a9a5` (6 commits, ~450 lines of Python, 4 test files, 1 bash script, config + gitignore).

**Minimum required investigations** — skip any with a written justification if you believe it is truly irrelevant:

1. **Signal dedupe collisions.** Task 4 uses `release:<repo>:<tag>`. Task 5 uses `case-study:<repo>:<path>`. Task 6 uses `readme-diff:<repo>:<heading>:<hash-prefix>`. Can any two different inputs produce the same dedupe key? Explicit probe: a file literally named `released v1.0.0` under `case-studies/`. A README heading that contains a colon. A tag whose name contains a slash.
2. **Test isolation.** Fixtures live at `tests/ecosystem-sync/fixtures/repos/repo-*` and are gitignored. If a developer runs the test suite without first running `build_fixtures.sh`, which tests fail and how? (Hint: case-study and release tests read these fixtures at import time via path resolution.) Propose a `conftest.py` autobuild hook or defend its absence.
3. **`_extract_section` under adversarial markdown.** What happens with (a) a heading that is exactly `## Capabilities` inside a fenced code block? (b) trailing whitespace on the heading line like `## Capabilities  `? (c) a lowercase heading `## capabilities`? (d) a nested subsection `### Capabilities` directly below a `## Features` that lacks a body? Run the function mentally; file-cite each case.
4. **`detect_release_tag` 90-day age cutoff.** The cutoff uses `datetime.fromisoformat(ts_out.strip())` on the output of `git log -1 --format=%cI <tag>`. Does `%cI` guarantee an `isoformat`-parseable string across all git versions? What about annotated vs lightweight tags — does the same command return consistent output? Is the `timezone.utc` comparison correct against a timezone-aware commit date?
5. **`detect_new_case_study` git-diff behavior.** When `state.last_commit_sha` is a commit no longer in the repo (e.g., force-push upstream, squashed history), what does `git diff <missing-sha>..HEAD` do? Does `detect_new_case_study` handle that gracefully or propagate an unhandled exception? Write a failing-case example.
6. **Mutable default hazard in `RepoState`.** Task 3 uses `field(default_factory=list)` / `field(default_factory=dict)` — correct. But is `RepoState` itself reused across repos? Check `run.py` (not yet implemented) can't mutate `last_seen_tags` of one repo's state and accidentally aliasing into another's.
7. **YAML round-trip of `RepoState`.** `save_state` uses `yaml.safe_dump` with `sort_keys=True`. When a repo's `last_readme_hash` dict gets sorted, does the on-disk order differ from what the next `load_state` returns? Any canonicalization drift that would make `has_substantive_change` falsely fire on load+save+load?
8. **Symlink `scripts/ecosystem_sync → ecosystem-sync`.** Is this symlink committed with mode `120000`? `git ls-files --stage scripts/ecosystem_sync` should show `120000`. If someone clones the repo on Windows (or any FS without symlink support), what breaks and how is the breakage diagnosed? Propose a CI guard.
9. **`build_fixtures.sh` idempotency.** The script does `rm -rf` on its own output dirs. Can it fail partway and leave the test suite in a state where some fixtures are current and others stale? Is `set -euo pipefail` enough, or does line 38's `cat > ... || mkdir -p ...` actually suppress the error properly?
10. **Type consistency.** `Signal.kind` is `Literal["release", "case-study", "readme-diff", "showcase"]`. Every detector constructs `Signal(kind=...)`. Grep: do any construct `kind="release"` vs `kind="releases"` vs `kind="tag"` inconsistency? What does mypy/pyright say if you run it?
11. **`_previous_semver` edge cases.** What if `all_tags` contains only the current tag (first release ever)? What if multiple tags point to the same commit? What if a tag is named `v0` (matches `^v?\d+$`? the regex `^v?\d+\.\d+(\.\d+)?$` requires at least `N.N`, so `v0` is correctly rejected, but confirm).
12. **Cross-machine path assumptions.** Production `scripts/ecosystem-sync/config.yaml` hard-codes `/mnt/local-analysis/workspace-hub/<repo>`. What happens on `ace-windows`? On `ace-macos`? Is the plan's scope "Linux cron on ace-linux-1 only" enough justification, or should `config.yaml` support env-var expansion now?
13. **Commit 4 plan-gate bypass history.** Commit `e2496a4d4` was initially blocked twice (`logs/hooks/plan-gate-events.jsonl` shows blocked-then-bypassed) before the marker was added. Verify that `.planning/plan-approved/ecosystem-sync.md` now exists with an mtime newer than `.planning/STATE.md`. If not, Tasks 7–11 will re-trigger the block. `ls -la .planning/plan-approved/ .planning/STATE.md` — include the output in your report.

**Output format for Part A:** Write a report to `docs/plans/2026-04-20-aceengineer-ecosystem-sync-review.md` with the following sections, and **commit it** as a separate commit (`docs(plans): adversarial review of ecosystem-sync commits 1-6`) BEFORE starting Part B:

```
## Summary
Count of findings: Critical / Major / Minor / Nit.

## Findings
### [CRITICAL] <short title>
**Location:** file:line
**Defect:** <what is wrong>
**Proof:** <steps to reproduce or line-cited argument>
**Proposed fix:** <what to change>

### [MAJOR] ...
### [MINOR] ...
### [NIT] ...

## Investigations performed
One paragraph per item 1-13 above, stating what you actually did (files read, commands run) and what you concluded.
```

**Do NOT skip findings you cannot fix yet.** Classify them and move on. Critical findings that block Tasks 7–11 must be flagged at the top of the report with "BLOCKS_TASK_7_PLUS" — in that case, pause and return control to the user before starting Part B.

---

## PART B — Implement Tasks 7–11 (TDD discipline, plan-verbatim code)

After Part A's review is committed, proceed through Tasks 7–11 in order. Each task's text below is copy-pasted from the full plan — use the text here as authoritative if it disagrees with the plan file for any reason (unlikely, but if so flag it).

**Global constraints for Part B — ABSOLUTELY CRITICAL:**

- **NEVER bypass git hooks.** Not `--no-verify`, not `FORCE_PLAN_GATE=1`, not `--no-gpg-sign`, nothing. If a hook blocks your commit, STOP. Diagnose the root cause (likely a missing marker file or a gitignore change). Fix the root cause OR return control to the user. Do NOT use documented bypass flags without explicit user authorization.
- **Do NOT push.** `feat/ecosystem-sync` has no upstream; keep it that way until the user merges or asks you to push.
- **Stop after Task 11's commit.** Tasks 12–17 (prep PR work, systemd install) are Stage 2 and require a separate authorization. Do NOT run `build_fixtures.sh --doctor --dry-run` etc. beyond what Task 11's smoke test calls for.
- **Do NOT modify files outside each task's listed files** except when the task explicitly says "modify" or when a pre-existing file path appears in the task's commit command.
- **Maintain TDD discipline:** write the failing test FIRST, run it, confirm the expected failure message, then write the minimal implementation. Confirm green. Commit. Do not squash steps.
- **Test numbering** (cumulative): after Task 7 total should be 24; after Task 8 total 26; after Task 9 total 31; after Task 10 total 34; after Task 11 depends on whether the shell smoke test counts — at minimum 34 Python tests still pass.

### Task 7 — Signal 5 (showcase/website labeled closed-issue detector)

**Files:**
- Modify: `scripts/ecosystem-sync/signals.py` (append)
- Create: `tests/ecosystem-sync/test_signals_showcase.py`

Test file content (verbatim):

```python
from unittest.mock import patch
from scripts.ecosystem_sync.signals import detect_showcase_labeled_closed_issues
from scripts.ecosystem_sync.state import RepoState


def _mock_gh_output(issues_by_label: dict[str, list[dict]]):
    """Return a function that mocks subprocess.run for gh issue list."""
    import json
    def fake_run(cmd, **kwargs):
        from subprocess import CompletedProcess
        for label, issues in issues_by_label.items():
            if f"--label" in cmd and label in cmd:
                return CompletedProcess(
                    cmd, 0, stdout=json.dumps(issues), stderr=""
                )
        return CompletedProcess(cmd, 0, stdout="[]", stderr="")
    return fake_run


def test_detects_new_closed_issue():
    issues = {"showcase": [
        {"number": 42, "title": "Deep-learning mooring model", "body": "body",
         "labels": [{"name": "showcase"}], "closedAt": "2026-04-20T10:00:00Z"}
    ]}
    state = RepoState(
        last_sync_utc="2026-04-20T00:00:00Z", last_commit_sha="",
        last_closed_showcase_issues=[],
    )
    with patch("subprocess.run", side_effect=_mock_gh_output(issues)):
        sigs = detect_showcase_labeled_closed_issues(
            "digitalmodel", state, since="2026-04-19"
        )
    assert len(sigs) == 1
    assert sigs[0].payload["issue_number"] == 42


def test_skips_known_issue():
    issues = {"showcase": [
        {"number": 42, "title": "T", "body": "b",
         "labels": [{"name": "showcase"}], "closedAt": "2026-04-20T10:00:00Z"}
    ]}
    state = RepoState(
        last_sync_utc="2026-04-20T00:00:00Z", last_commit_sha="",
        last_closed_showcase_issues=[42],
    )
    with patch("subprocess.run", side_effect=_mock_gh_output(issues)):
        sigs = detect_showcase_labeled_closed_issues(
            "digitalmodel", state, since="2026-04-19"
        )
    assert sigs == []


def test_skips_not_planned():
    issues = {"showcase": [
        {"number": 42, "title": "T", "body": "b",
         "labels": [{"name": "showcase"}, {"name": "not-planned"}],
         "closedAt": "2026-04-20T10:00:00Z"}
    ]}
    state = RepoState(
        last_sync_utc="2026-04-20T00:00:00Z", last_commit_sha="",
        last_closed_showcase_issues=[],
    )
    with patch("subprocess.run", side_effect=_mock_gh_output(issues)):
        sigs = detect_showcase_labeled_closed_issues(
            "digitalmodel", state, since="2026-04-19"
        )
    assert sigs == []
```

Implementation (append to signals.py):

```python
import json

SHOWCASE_LABELS = ("showcase", "website")
SKIP_LABELS = ("not-planned", "duplicate")


def detect_showcase_labeled_closed_issues(
    repo_name: str, state: RepoState, since: str,
) -> list[Signal]:
    """Signal 5: issues closed with showcase or website label since last sync."""
    known = set(state.last_closed_showcase_issues)
    signals: list[Signal] = []
    seen_nums: set[int] = set()

    for label in SHOWCASE_LABELS:
        try:
            result = subprocess.run(
                ["gh", "issue", "list",
                 "--repo", f"vamseeachanta/{repo_name}",
                 "--label", label, "--state", "closed",
                 "--search", f"closed:>={since}",
                 "--json", "number,title,body,labels,closedAt",
                 "--limit", "100"],
                capture_output=True, text=True, check=True, timeout=60,
            )
            issues = json.loads(result.stdout or "[]")
        except (subprocess.CalledProcessError, json.JSONDecodeError, subprocess.TimeoutExpired):
            continue

        for issue in issues:
            num = issue["number"]
            if num in known or num in seen_nums:
                continue
            labels = {l["name"] for l in issue.get("labels", [])}
            if labels & set(SKIP_LABELS):
                continue
            seen_nums.add(num)
            body = issue.get("body", "") or ""
            truncated = " ".join(body.split()[:500])
            signals.append(Signal(
                repo=repo_name,
                kind="showcase",
                title=f"[sync] {repo_name} #{num}: {issue['title']}",
                body=(
                    f"Upstream issue closed with `{label}` label.\n\n"
                    f"Link: https://github.com/vamseeachanta/{repo_name}/issues/{num}\n\n"
                    f"## Upstream body (truncated)\n\n{truncated}\n\n"
                    f"## Proposed website update\n\nBlog post / case study draft."
                ),
                dedupe_key=f"showcase:{repo_name}:{num}",
                payload={"issue_number": num, "label": label},
            ))
    return signals
```

Note: `import json` goes at the top of `signals.py` with existing imports, not inline mid-file.

Commit: `feat(ecosystem-sync): signal 5 — labeled closed-issue detector`

### Task 8 — Digest renderer with golden tests

**Files:**
- Create: `scripts/ecosystem-sync/digest.py`
- Create: `tests/ecosystem-sync/test_digest.py`
- Create: `tests/ecosystem-sync/golden/empty.md`
- Create: `tests/ecosystem-sync/golden/with_signals.md`

Get the verbatim code for `digest.py`, `test_digest.py`, and both golden files from `docs/plans/2026-04-20-aceengineer-ecosystem-sync-plan.md` under "## Task 8". The code is plan-verbatim; do not improvise.

Test expectations: `render_digest(...)` must produce output that byte-exactly matches `golden/empty.md` for the empty case and `golden/with_signals.md` for the signals case. If the test fails by a trailing-whitespace or single-character difference, fix the renderer — NOT the golden file. (The plan authored both; they match.)

Commit: `feat(ecosystem-sync): digest renderer + golden tests`

### Task 9 — Issue opener (dedupe + retry-once)

**Files:**
- Create: `scripts/ecosystem-sync/issues.py`
- Create: `tests/ecosystem-sync/test_issues.py`

Verbatim code under plan's "## Task 9". 5 tests: skip-on-duplicate, create-when-no-dup, retry-once-on-create-failure, giveup-after-retry, dedupe-check-failure-returns-unknown.

Important: the retry path uses `time.sleep(10)` between attempts — the test patches `time.sleep` so the actual 10-second wait does not occur. Do NOT change this — it's intentional for production real-delay + test fast-path.

Commit: `feat(ecosystem-sync): issue opener with dedupe + retry-once`

### Task 10 — Orchestrator `run.py` (with `--dry-run` and `--doctor`)

**Files:**
- Create: `scripts/ecosystem-sync/run.py`
- Create: `tests/ecosystem-sync/test_run.py`

Verbatim code under plan's "## Task 10". 3 tests: doctor-success, doctor-fails-on-missing-repo, dry-run-writes-no-issues.

`run.py` is the single largest file in Stage 1 (~140 lines). It imports from models, config, state, signals, digest, issues — all prior modules. If any import errors, flag immediately with BLOCKED — do NOT add imports or rewrite modules to make run.py compile.

Commit: `feat(ecosystem-sync): orchestrator with --dry-run and --doctor`

### Task 11 — Bash cron entry (flock + one-shot rebase)

**Files:**
- Create: `.claude/cron/ecosystem-sync.sh`
- Create: `docs/sync-reports/.gitkeep`
- Create: `.claude/state/ecosystem-sync/last-sync.yaml`

Verbatim bash + small seed files under plan's "## Task 11". The script is 40-ish lines of bash with `flock`, `git pull`, `uv run run.py`, and a one-shot-rebase retry path on the state-file push.

**Smoke test** (Step 4 of Task 11): run `bash .claude/cron/ecosystem-sync.sh --doctor`. The RC will likely be NON-ZERO because the 6 source repos may not be fully reachable from the worktree — that's expected. Capture the log at `logs/ecosystem-sync/$(date -u +%Y-%m-%d).log` and confirm the wrapper itself ran (flock obtained, logging worked). Non-zero RC from `run.py --doctor` in the worktree context is an acceptable smoke-test outcome; Task 15 (out of Stage 1 scope) is where `--doctor` should actually pass.

Commit: `feat(ecosystem-sync): bash cron entry with flock + one-shot rebase`

**After Task 11's commit:** report back. Do NOT proceed to Task 12.

---

## PART C — Final handback

Produce a report at `docs/plans/2026-04-20-aceengineer-ecosystem-sync-hermes-handback.md` with:

1. **Adversarial review summary** (Part A): count of findings by severity + link to the full review file.
2. **Implementation summary** (Part B): Tasks 7–11 completed, commit SHAs, test counts per task, hook behavior per commit (MUST be "passed, no bypass" for each).
3. **Smoke-test outcome** from Task 11 Step 4.
4. **Outstanding concerns**: anything that surprised you, anything you had to work around, anything the user should know before Stage 2.
5. **Final commit list:** `git log --oneline 00a3ffc38..HEAD` output, prefixed by branch name.

Commit this file as: `docs(plans): ecosystem-sync Tasks 7-11 + review handback`

---

## Escalation triggers — return control to user immediately if you hit ANY of these

- A pre-commit hook blocks your commit. Return control; do not bypass.
- A test fails in an unexpected way after you've followed the plan verbatim. Return control.
- The adversarial review (Part A) surfaces a CRITICAL finding that blocks Tasks 7–11. Return control after committing the review report.
- Any of the 6 existing commits turns out to have a file not matching its plan text. Return control.
- You believe a step in the plan is wrong or dangerous. Return control with your diagnosis.
- You receive a transient API error (overloaded, 503, timeout) that persists past 3 retries. Return control with the current state described precisely.

**Good working. Keep it plan-verbatim, keep it TDD, and hunt defects honestly.**
