---
name: gsd-operational-audit
description: Audit a repo's live GSD/get-shit-done workflow state against docs, issues, and runtime outputs to find stale issues, automation reliability gaps, parser drift, migration residue, and policy contradictions.
version: 1.2.0
author: Hermes Agent
license: MIT
---

# GSD Operational Audit

Use when a repo claims to use GSD/get-shit-done and you need to determine what is actually working, what is stale, and what needs cleanup.

## When to use
- User asks whether GSD is really adopted or just planned
- User wants to know how well the ecosystem is using get-shit-done-cc
- There are open GSD migration issues and you need to verify them against repo reality
- There may be drift between `.planning/`, docs, issues, cron jobs, and runtime tooling

## Critical: Resolve the real repo path FIRST

On ace-linux-1, `~/workspace-hub` is a **sparse overlay** with almost nothing in it (only `.claude/state/corrections/`). The real git repo is at `/mnt/local-analysis/workspace-hub`. Subagents given `~/workspace-hub` will report everything as missing.

**Discovery pattern** (run before any audit work):
```bash
# Check if CWD is a git repo
git -C ~/workspace-hub status 2>&1 | head -1
# If "fatal: not a git repository", find the real one:
find /mnt -name "workspace-hub" -type d -maxdepth 3 2>/dev/null
```

Use the resolved path (`/mnt/local-analysis/workspace-hub`) for ALL subsequent commands, subagent contexts, and file searches. This single mistake can waste an entire subagent delegation.

## Audit order

1. Verify open GSD-related issues against repo reality
2. Validate the nightly researcher / automation loop end-to-end
3. Compare `STATE.md` and `.planning/` artifacts with live `gsd-tools` output
4. Search for migration residue from pre-GSD workflow surfaces
5. Check policy alignment across issues, AGENTS.md, templates, provider routing, and machine naming

## Step 1: Verify GSD issues against reality

Pull the main GSD issues first:
- onboarding / migration
- evaluation / adoption
- nightly researcher
- specs-to-planning migration
- workflow residue cleanup

Use `gh issue view <id> --comments --json ...` and compare with the filesystem.

Typical close/rescope outcomes:
- **Close** when the implementation already exists and only historical residue remains
- **Rescope** when the original adoption/evaluation goal is complete but hardening/cleanup remains
- **Keep open** when the feature exists but reliability or policy acceptance criteria are still unmet

## Step 2: Validate nightly GSD researcher

Check these surfaces together:
- `config/scheduled-tasks/schedule-tasks.yaml`
- `scripts/cron/gsd-researcher-nightly.sh`
- `.planning/research/*.md`
- `logs/research/*.log`
- `logs/daily/*.md`
- `scripts/productivity/sections/research-highlights.sh`

What to look for:
- schedule exists and points to the right script
- research artifacts are actually accumulating
- daily summary includes latest research findings
- failures in logs are categorized as:
  - git contention/index corruption
  - CLI timeout/failure
  - push race / ref lock
  - missing path/host guard problems

Important interpretation:
- If artifacts exist and daily summary consumes them, the issue is no longer "setup"; it is "reliability hardening"

### Hardening patterns that worked well

For `gsd-researcher-nightly.sh`, the highest-value fixes were:
- increase timeout budget for WebSearch-heavy runs
- retry once on primary Claude failure/timeout with **reduced context**
- make output validation **domain-aware** (`synthesis` must not be validated like daily domain reports)
- trim conversational preamble before the canonical markdown heading

### Verifying hardening is actually deployed (not just committed)

Critical check before closing reliability issues: compare the **commit timestamp** of hardening changes against the **cron execution timestamps** in logs.

Technique:
1. `git log --format='%h %ad %s' --date=iso -- scripts/cron/gsd-researcher-nightly.sh` — when did the fix land?
2. Check log output for feature markers (e.g., `timeout=300s` vs `timeout=180s`, `model=haiku`, `budget=$0.50`) — does the log show the new features?
3. If cron ran BEFORE the commit, the hardened script has NOT been tested in production — do NOT close the issue.

Real example: hardening commit landed at 4pm, cron runs at 6:35am — the next day's run is the first real test. This caught a premature closure attempt where 6/7 runs looked good but were all on the OLD script.

### Best test strategy for cron bash scripts

Prefer a behavioral shell test under `scripts/cron/tests/` that:
- creates a temp workspace with the same relative layout
- copies the real script under test
- stubs `date`, `hostname`, `flock`, `git`, `claude`, and `notify.sh` via `PATH`
- asserts artifact creation, retry behavior, and skip behavior

This worked better than grep-only/static tests for validating retry/fallback behavior.

### Crontab drift from schedule-tasks.yaml

See "Crontab drift from YAML source of truth" section below for the full detection and fix workflow.

## Step 3: Check GSD state/dashboard drift

Run the live tools:
- `node .claude/get-shit-done/bin/gsd-tools.cjs state-snapshot`
- `node .claude/get-shit-done/bin/gsd-tools.cjs roadmap analyze`
- `node .claude/get-shit-done/bin/gsd-tools.cjs phase-plan-index <phase>`
- `node .claude/get-shit-done/bin/gsd-tools.cjs init manager`

Then compare against:
- `.planning/STATE.md`
- `.planning/ROADMAP.md`
- `.planning/PROJECT.md`

Common failure mode:
- `STATE.md` has moved important values into YAML frontmatter or section blocks, but `cmdStateSnapshot()` still parses older body fields like `Current Phase`, `Total Phases`, `Progress`, etc.

If `state-snapshot` returns many nulls while `STATE.md` is clearly populated, flag it as a parser drift issue.

## Step 4: Search for migration residue

Search for:
- `lifecycle HTML`
- `stage-`
- `20-stage`
- `specs/`
- old work-queue folders / stage prompts

**Performance warning:** `grep -rn` on the full workspace-hub can timeout (300s+) due to repo size (36K+ files, nested repos, large binary artifacts). Always scope searches to specific directories:
```bash
# GOOD: scoped to active directories
grep -rn 'work.queue' --include='*.md' AGENTS.md docs/standards/ .planning/ 2>/dev/null
# BAD: full-repo grep will timeout
grep -rn 'work.queue' --include='*.md' 2>/dev/null
```

Interpret carefully:
- historical references in archives or reflect-history are low priority
- active skills/docs/templates that can still steer agents are high priority

Pay special attention to contradictions like:
- `AGENTS.md` says "GitHub issues only; no local work-queue"
- other docs still describe `.claude/work-queue/` as canonical

That is a policy conflict, not just stale wording.

## Step 5: Check policy alignment

Inspect:
- `AGENTS.md`
- issue templates
- provider routing docs
- machine naming docs
- architecture docs for GSD/provider roles

Look for gaps in:
- provider routing matrix
- machine naming normalization (`dev-primary` vs `ace-linux-1`, etc.)
- issue intake fields matching actual machine inventory
- how GitHub issue intake maps to GSD planning/execution artifacts

## Output format

Return findings in five buckets:
1. **Working now**
2. **Implemented but unreliable**
3. **Parser/state drift**
4. **Migration residue**
5. **Policy contradictions / missing operating model**

Then provide:
- issues to close
- issues to rescope
- issues to keep open
- top 3-5 hardening tasks in priority order

## Cron health monitoring pattern

When the repo has `config/scheduled-tasks/schedule-tasks.yaml`, a health-check script (`scripts/monitoring/cron-health-check.sh`) can validate all jobs automatically:

1. Parse the YAML with Python (`uv run --no-project python3 -c "import yaml; ..."`)
2. For each task: resolve log path (handle globs with `shopt -s nullglob` + stat newest), check mtime staleness, grep for error patterns
3. Status categories: OK, STALE (log older than expected interval), MISSING (no log file), ERROR (error patterns found)
4. Skip Windows-scheduler tasks and `log: null` entries
5. Write JSON report to `.claude/state/cron-health/YYYY-MM-DD.json`

### Pitfalls discovered during implementation
- **Arg parsing:** `for i in "$@"` with `shift` inside the loop doesn't work — `shift` doesn't affect the already-expanded list. Use `while [[ $# -gt 0 ]]` instead.
- **UTC vs local date:** If the script uses `date -u +%Y-%m-%d`, tests must also use `date -u`. A timezone offset can cause the test to look for `2026-04-01.json` while the script wrote `2026-04-02.json`.
- **`.claude/state/` is gitignored** in this repo — reports written there are local-only unless force-added or synced another way.
- **Glob log patterns** (e.g., `logs/research/*.log`): use `shopt -s nullglob` to avoid literal glob strings when no files match, then `stat -c %Y` to find the newest file.

### Crontab drift from YAML source of truth

`config/scheduled-tasks/schedule-tasks.yaml` is the declared source of truth, but the live crontab can drift silently:

**How to detect:** Compare YAML task IDs against `crontab -l` entries. Parse YAML with Python, match crontab lines by script basename.

Common drift patterns found in practice:
- **Stale log paths:** YAML updated (e.g., split shared cron.log into per-task files) but crontab still points to old paths
- **Missing tasks:** New tasks added to YAML but never installed (setup-cron.sh is additive-only by default)
- **Orphan tasks:** Tasks removed from YAML but still in crontab (e.g., `claude-plugin-audit`)
- **/tmp/ log paths:** Jobs logging to `/tmp/` — lost on reboot, invisible to repo-level health checks

**Fix workflow:**
1. Run `bash scripts/cron/setup-cron.sh --dry-run --replace` to preview the correct crontab
2. Compare against `crontab -l` to identify drift
3. Run `bash scripts/cron/setup-cron.sh --replace` to overwrite with YAML-derived entries
4. For orphan tasks: either add them to YAML properly or accept their removal

The `--replace` flag (added in this workflow) generates the entire crontab from YAML, removing orphans and fixing stale paths in one operation. The default additive mode is preserved for backward compatibility.

**Multi-machine rollout:** After fixing one machine, raise GH issues for other machines with the `--replace` command and verification steps. Each machine's crontab is derived from the same YAML filtered by its `machines` list.

### Shared-log anti-pattern

Multiple cron tasks MUST NOT share a single log file (e.g., `.claude/state/learning-reports/cron.log`). Problems:
- Error patterns from one task cascade as false positives to all tasks sharing the log
- Impossible to determine per-task health from a combined log
- Health monitoring that scans for error patterns will flag every task that shares the log

Fix: give each task its own dated log path (e.g., `logs/maintenance/TASK-$(date +%Y%m%d).log`).
Also avoid `/tmp/` log paths — they're lost on reboot and invisible to repo-level health checks.

## Step 6: Mine session signals for failure patterns

Session telemetry lives at `.claude/state/session-signals/*.jsonl` (gitignored, local-only).
Records are newline-delimited JSON. Key event types:

| Event | What it tells you |
|-------|-------------------|
| `session_tool_summary` | Tool calls per WRK per session — detect runaway loops |
| `session_end` | End-of-session signals including `correction_events`, `skill_invocations`, `wrk_items_touched` |
| `smoke_test` | Per-repo smoke test pass/fail with passed/failed counts |
| `test_health_summary` | Cross-repo TDD pairing percentage |
| `drift_counts` | Python runtime violations, file placement violations, git workflow violations |

### Runaway loop detection

Sessions with 100+ tool calls are suspicious. To find the worst offenders:

```bash
cat .claude/state/session-signals/*.jsonl | uv run python3 -c "
import sys, json, collections
wrk_stats = collections.defaultdict(lambda: {'sessions': 0, 'total_calls': 0, 'max_calls': 0})
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try: d = json.loads(line)
    except: continue
    if d.get('event') == 'session_tool_summary':
        wrk = d.get('wrk', 'unknown')
        calls = d.get('tool_calls', 0)
        wrk_stats[wrk]['sessions'] += 1
        wrk_stats[wrk]['total_calls'] += calls
        wrk_stats[wrk]['max_calls'] = max(wrk_stats[wrk]['max_calls'], calls)
by_effort = sorted(wrk_stats.items(), key=lambda x: x[1]['total_calls'], reverse=True)
for wrk, s in by_effort[:10]:
    print(f'{wrk:>12s}  {s[\"sessions\"]:6d} sessions  {s[\"total_calls\"]:10d} total  {s[\"max_calls\"]:6d} max')
"
```

### Smoke test failure patterns

Look for repos with consecutive-day failures (persistent breakage vs. one-off):

```bash
cat .claude/state/session-signals/*.jsonl | uv run python3 -c "
import sys, json
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try: d = json.loads(line)
    except: continue
    if d.get('event') == 'smoke_test' and d.get('status') == 'fail':
        print(f'{d.get(\"ts\",\"?\")[:10]}  {d.get(\"repo\",\"?\"):25s}  passed={d.get(\"passed\",0)} failed={d.get(\"failed\",0)}')
"
```

Key insight: `passed=0 failed=0` means the test runner itself crashed — not that tests failed. Fix the harness, not the tests.

**Status field pitfall:** Smoke tests can have `status: "fail"`, `"timeout"`, or `"error"`. When scanning for failures, match ALL non-pass statuses, not just `"fail"`. The `worldenergydata` 18-day failure streak was entirely `"timeout"` records that would be missed by `status == "fail"` checks. Use:
```python
fail_statuses = {"fail", "timeout", "error"}
```

### Correction capture status

**IMPORTANT:** Corrections are captured in TWO separate locations:

1. `.claude/state/session-signals/*.jsonl` — has `correction_events` and `skill_invocations` arrays in `session_end` records, but these are **always empty** (detection not wired into the session emitter).
2. `.claude/state/corrections/session_YYYYMMDD.jsonl` — **this is the active store**. The `capture-corrections.sh` PostToolUse hook writes here. As of 2026-04, 8,965+ corrections across 3,127 files have been captured.

**Audit pitfall:** Do NOT conclude "no corrections captured" based only on session-signals data. Always check `.claude/state/corrections/` too. The initial #1426 audit made this exact mistake.

To analyze correction data for skill promotion candidates:
```bash
bash scripts/enforcement/correction-to-skill-candidates.sh --threshold 10
```

This finds files with 10+ corrections (strong skill candidates) and existing skills that are frequently corrected (need updates).

### Pitfalls

- **Volume:** Signal files can contain 200K+ records (390 files, 73MB observed). Always stream with Python, never try to load all into memory at once or use `jq` on the full set.
- **execute_code quoting trap:** Do NOT embed multi-line Python with nested quotes inside `terminal()` f-strings in `execute_code` — it will cause SyntaxErrors. Instead, write a standalone `.py` script to `/tmp/audit-signals.py` via `write_file`, then run it with `terminal("uv run --no-project python3 /tmp/audit-signals.py")`.
- **`.claude/state/` is gitignored.** Reports written there stay local-only. Commit reports to `docs/reports/` instead.
- **Many "none" events:** The majority of records may be placeholder/test data with `event: none`. Filter by event type first. In the 2026-04 audit: 225K "none" events vs 7.3K session_tool_summary.

## Enforcement gradient promotion pattern

When a repo has a policy at Level 0 (Prose) that needs to be promoted through enforcement levels:

### Level progression
| Level | What | How to verify |
|-------|------|---------------|
| Level 0 — Prose | .md doc exists | `test -f docs/standards/POLICY.md` |
| Level 1 — Micro-skill | Auto-loaded reminder | Skill file references the policy |
| Level 2 — Script | Binary check script | `scripts/enforcement/require-*.sh` or `scripts/ai/*.py` with tests |
| Level 3 — Hook | PreToolUse/Stop hook | Registered in `.claude/settings.json`, fires automatically |

### Claude hook protocol (for Level 3)
Hooks read JSON from stdin: `{"tool_name": "Bash", "tool_input": {"command": "gh pr create ..."}}`
- Extract via: `jq -r '.tool_name // empty'` and `jq -r '.tool_input.command // empty'`
- To BLOCK: output `{"decision": "block", "reason": "..."}` to stdout
- To ALLOW: exit 0 with no JSON output
- Non-zero exit is NOT used for blocking — hook always exits 0
- Timeout patterns: 5s lightweight, 10s medium, 15s heavy (cross-review)

### Compliance measurement formula
When auditing enforcement compliance, use three weighted dimensions:
- Infrastructure (30%): policy docs exist, gate scripts exist, hooks registered
- Artifacts (30%): work items with review evidence (WRK dirs, review result files)
- Git evidence (40%): commits with review keywords vs total non-trivial commits

This produces a single compliance % that can be tracked over time. Threshold: 80%.

Script: `scripts/ai/verify-adversarial-reviews.sh --days 30 --json`

### Common gap pattern
Infrastructure scores 100% while git evidence scores <10% — this means the enforcement
machinery exists but is advisory-only. The fix is to wire scripts into hooks (Level 2 → Level 3)
so enforcement is automatic, not manual.

## Verification gates inventory

When auditing, check for these enforcement scripts and hooks:

| Gate | Script | Hook | What it prevents |
|------|--------|------|-----------------|
| Cross-review | `scripts/enforcement/require-cross-review.sh` | `cross-review-gate.sh` Gate 1 | PR without review |
| Plan review | `scripts/enforcement/require-plan-review.sh` | `cross-review-gate.sh` Gate 3 | Execution without reviewed plan |
| Artifact verify | `scripts/enforcement/require-verify-artifacts.sh` | `cross-review-gate.sh` Gate 2 | Ship without verification |
| TDD pairing | `scripts/enforcement/require-tdd-pairing.sh` | `cross-review-gate.sh` Gate 4 | Commits without test files |
| Tool-call ceiling | `.claude/hooks/tool-call-ceiling.sh` | PostToolUse | Runaway sessions (500 call limit) |
| Smoke escalation | `scripts/enforcement/smoke-test-escalation.sh` | Manual/cron | Persistent test failures |
| Skill candidates | `scripts/enforcement/correction-to-skill-candidates.sh` | Manual/cron | Correction patterns not promoted |

When adding new gates, the pattern is:
1. Write the enforcement script in `scripts/enforcement/`
2. Wire it into `cross-review-gate.sh` (for commit/PR/ship gates) or `settings.json` PostToolUse (for per-call gates)
3. TDD gates use `--staged` flag to check git staging area; `--strict` to block vs. warn

## Cron git contention: shared git-safe library pattern

When multiple cron scripts do git pull/commit/push on the same repo, they WILL race. The fix is a shared library — NOT per-script locking.

### Discovery pattern (what to audit)

1. Search all cron scripts for git operations: `grep -rn 'git pull\|git push\|git commit\|git add' scripts/cron/`
2. Check which use flock: `grep -rn 'flock\|GIT_LOCK' scripts/cron/`
3. Check if they share the SAME lockfile — if each script has its own, the lock provides zero cross-script protection
4. Map schedule overlaps from `config/scheduled-tasks/schedule-tasks.yaml`
5. **Check crontab itself for inline git** — some entries embed raw `git pull --rebase && git commit && git push` directly in the crontab line instead of calling a script. These completely bypass git-safe even if every script uses it:
   ```bash
   crontab -l | grep 'git pull\|git push\|git commit' | grep -v 'scripts/cron/'
   ```
   Real example found: architecture-scan and staleness-scan had inline git at 02:00/03:00 Sun, racing with other jobs.

### Common failure modes (from real logs)

| Mode | Frequency | Symptom |
|------|-----------|---------|
| Push race | ~60% | `remote rejected - cannot lock ref` |
| Index corruption | ~12% | `fatal: .git/index: index file smaller than expected` |
| Stale index.lock | occasional | `Unable to create '.git/index.lock': File exists` |
| Dirty tree blocking rebase | occasional | `error: cannot pull with rebase: You have unstaged changes` |
| Concurrent execution | occasional | Doubled log lines from same script |

### Shared library design (scripts/cron/lib/git-safe.sh)

Key functions: `git_safe_pull`, `git_safe_commit`, `git_safe_push`, `git_safe_sync`

Design decisions that worked:
- **fd-based flock** (`exec 9>"$lockfile"; flock 9`) instead of `flock /path cmd` — avoids `bash -c` which is blocked by Claude deny rules and is fragile with quoting
- **Single lockfile** for all scripts: `/tmp/workspace-hub-git.lock`
- **Index heal** before every pull and commit: `rm -f index.lock; git read-tree HEAD`
- **Auto-stash** dirty tree before rebase, auto-pop after
- **Retry-push** with exponential backoff (3 attempts, 5s/10s/20s)
- **Configurable** via env vars (GIT_SAFE_LOCK, GIT_SAFE_PUSH_RETRIES, etc.)
- **Double-source guard** (`_GIT_SAFE_LOADED`) for scripts that source other scripts

### Integration pattern

```bash
# In each cron script — replaces inline git operations:
GIT_SAFE_LOG_PREFIX="[script-name]"
source "${WS_HUB}/scripts/cron/lib/git-safe.sh"
git_safe_init "$WS_HUB"

# Then use:
git_safe_pull || true        # non-fatal pull
# ... do work ...
git_safe_commit "msg" file1 file2
git_safe_push || true        # non-fatal push
```

### Testing pitfall

Push tests (`git push`) are blocked by Claude's deny rules in `.claude/settings.json`. Guard push tests behind an env var: `GIT_SAFE_TEST_PUSH=1`. Always document this in test output so it's not confused with real failures.

### What NOT to do

- Don't use `rm -f .git/index.lock` as a standalone fix — it races with the actual lock holder
- Don't use `flock /path/lock bash -c '...'` — fragile quoting + blocked in Claude sessions
- Don't implement locking per-script — only works if ALL scripts use the same lockfile
- Don't assume `git pull --rebase` will succeed with dirty working tree — always stash first

## Key heuristic learned

When GSD artifacts, scripts, and outputs all exist but the issue is still open, do not call it "not implemented". Usually the correct label is one of:
- implemented but reliability not proven
- implemented but issue text is stale
- implemented but policy/docs/state parsing have not caught up
