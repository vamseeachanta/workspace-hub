# Autonomous Codex Burn Launch Closeout

Use this reference when turning a 12-hour / overnight Codex-credit burn request into a concrete launch plan or handoff.

## What to produce before launching

- A lane table with repo, issue/bundle IDs, reason it is safe for autonomous execution, branch/worktree path, and validation target.
- A manifest under a durable run directory such as `/mnt/local-analysis/codex-burn-YYYYMMDD/manifest.md` or `.json`.
- Per-lane prompt files that force live issue-state verification before any mutation.
- Explicit exclusion of human-in-loop tasks: unapproved plans, legal/tax filing submissions, external outreach, payment/account actions, credential setup, production deployment, and ambiguous destructive cleanup.

## Launch hygiene

For each lane capture before or at launch time:
- PID or Hermes session id.
- Parent PID / launcher PID when launching from a shell wrapper.
- Prompt path.
- Worktree/clone path.
- Branch name.
- Log path.
- Initial `git status --short` and issue labels.
- Full launch command or a command file path plus a hash of the command file.
- `launched_at` timestamp, immediate post-spawn liveness, and the expected output/exit-code file paths.

If launching from a shell instead of Hermes process tools, use a wrapper that writes `${lane}.pid`, `${lane}.ppid`, `${lane}.exit`, `${lane}.status.json`, and `${lane}.log` files. Write the exit code from a `trap` or subshell wrapper. Without these files, exact exit status, parent process, immediate post-spawn state, and byte-for-byte launch command become unrecoverable after process exit; never reconstruct or fabricate them in later monitoring evidence.

## Monitoring cadence

Every 60-90 minutes:
1. Refresh provider quota artifacts when available.
2. Check process liveness from PID/session files.
3. Inspect logs for completion, blockers, or repeated sandbox/stdin stalls.
4. Verify each completed lane with git status, recent commits, pushed branch/main ancestry, and GitHub comments/labels.
5. Top up only from the vetted autonomous backlog; avoid launching duplicate work on an issue already `agent:codex` or `status:working` unless explicitly recovering it.

## Supplemental audit when launch evidence is incomplete

If a burn wave was launched without durable PID/exit/status files, do a supplemental audit instead of guessing:
- Record what is directly observable now: process list, Hermes/background session list if available, current git status/branch/origin ancestry, issue labels/state, prompt/log paths, and log tail hashes.
- Recover only evidence that exists in logs (for example Codex session IDs or PIDs printed during launch); label it as log-derived rather than launch-time durable evidence.
- State explicitly that final local process exit codes and byte-for-byte launch command state are unrecoverable after process exit when `${lane}.exit` / `${lane}.status.json` were not written at launch.
- Produce both machine-readable JSON and concise Markdown under the run directory so future monitoring can compare exact paths, issue states, hashes, and blockers.

## Checklist-grade continuation audits

When the user provides a long launch/monitoring checklist and says the judge will mark items, do not claim checklist boxes yourself. Instead, create evidence that lets the judge decide:
- Generate a `current-audit.md` and `current-audit.json` in the run's `monitoring-evidence/` directory with: bundle identity, repo, issues, prompt path, log path, session/run id, launch time if present in logs, finish time, duration, terminal classification, final issue states, branch/head/upstream, artifact paths, and hashes.
- Re-refresh live state at audit time: `gh issue view ... --json ...`, `git status --short --branch`, `git rev-parse HEAD`, `git ls-remote origin refs/heads/<branch>`, tool versions, GitHub auth status with tokens redacted, rate-limit headroom, and a `codex exec` process check.
- Classify conservatively: all bundle processes can be terminal while the overall operation remains incomplete if any requested issue is still open or acceptance criteria are documented as unmet. Use `blocked_partial` for mixed closed/open issue bundles rather than `succeeded`.
- Preserve exact impossibilities separately from blockers: missing original PID/exit-code sidecars, Hermes process handles after exit, byte-for-byte command provenance, and poll chronology are retrospective evidence gaps, not reasons to fabricate success.
- Process checks must avoid counting the check command itself as a live Codex run. Prefer a narrow predicate such as `ps -eo pid,ppid,stat,etime,cmd | awk '/codex exec/ && /<run-dir>/ && !/awk/ {print}'` and record `(empty)` when no matching process remains.
- If reusing prior run evidence for a continuation ask, state that it is pre-existing evidence and verify it still corresponds exactly to the requested bundle set before using it.
- After context compaction or a handoff summary, do not answer checklist-continuation requests from memory. Re-open the latest on-disk audit/report artifacts and re-refresh live process/git/GitHub state before finalizing; otherwise a compacted context can cause stale blocker/status restatement without current evidence.
- Run a post-redaction token scan and final hashes after writing/patching evidence files; if redaction or manual patching changes content, recompute hashes.
- If the user repeats the same long checklist after a blocker/final report, do not only restate the blocker. Produce a compact checklist crosswalk artifact (`checklist-crosswalk-evidence.md/.json`) that maps requirement classes to evidence pointers, impossible/not-applicable items, and current blockers. The crosswalk should say it is evidence for a judge, not self-certification.
- If the repeated checklist says to continue "these bundles" but supplies no new exact bundle IDs, issue numbers, paths, or approval override, treat `new_user_supplied_bundle_refs=0`: refresh the known run directory, issue states, process state, and hashes; record `launched_new_continuation=0`; and stop for explicit user/governance input instead of narrowing an open blocked issue into a new implicit continuation lane. The final response should lead with the newly written evidence paths/hashes plus the exact authorization choices needed; do not bury the stop condition behind the checklist.
- For repeated judge/checklist prompts after a terminal-but-incomplete wave, write an explicit `checklist-crosswalk-evidence-{timestamp}.md/.json` artifact instead of only a final narrative. Include requirement-class rows such as `bundle_identity_and_access`, `environment_and_prerequisites`, `launch_actions`, `monitoring_to_terminal`, `logs_artifacts_and_deliverables`, `sensitive_data_redaction`, `inventory_reconciliation`, `not_possible_retrospectively`, and `blocked_user_input`. Add counts for `identified`, `accessible`, `previously_launched`, and `new_launches_this_turn` so a judge can reconcile prior launches versus current-turn action.
- For live issue-state tables, prefer a lean refresh command after any rich JSON query: `gh issue view N --repo OWNER/REPO --json state,url,updatedAt,closedAt --jq '[.state,.url,.updatedAt,.closedAt] | @tsv'`. If rich `comments` JSON parsing or truncation yields `ERR`, patch the table with this lean refresh rather than leaving ambiguous issue states.
- If a remote-branch refresh (`git ls-remote origin refs/heads/<branch>`) fails with a transient hosting/network error while GitHub issue/API checks still work, retry once during the crosswalk refresh and record the exit/output rather than downgrading an otherwise terminal bundle to unknown. Keep the retry evidence separate from the original launch evidence.

## Evidence redaction and hashing

Before publishing or hashing monitoring evidence:
- Redact GitHub tokens, API keys, bearer values, and credential-like environment outputs even if the upstream command masked part of the token.
- Prefer neutral placeholders such as `[REDACTED_GITHUB_TOKEN]` or `[REDACTED_GITHUB_TOKEN_PREFIX]`; do not preserve token prefixes in final artifacts unless they are necessary for a test fixture.
- Run a strict high-confidence secret scan over the evidence directory before final reporting. Example patterns to catch include `github_pat_...`, `gh[opsu]_...`, `sk-...`, `AKIA...`, and private-key headers.
- Compute final artifact hashes only after redaction; if redaction changes content, recompute hashes and report the post-redaction hashes.

## Reporting shape

Keep user-facing updates short and operational:
- launched count / target concurrency
- issue or bundle hyperlinks
- run directory / manifest path
- running vs completed vs blocked
- next monitoring time

Do not imply work is complete when it is merely launched. Use `running`, `blocked`, or `landed + verified` states only.