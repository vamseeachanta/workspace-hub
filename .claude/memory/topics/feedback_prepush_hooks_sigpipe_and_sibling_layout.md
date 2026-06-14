> Git-tracked snapshot from Claude auto-memory. Captured: 2026-06-14
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_prepush_hooks_sigpipe_and_sibling_layout.md

---
name: feedback_prepush_hooks_sigpipe_and_sibling_layout
description: Two workspace-hub pre-push blockers — review-gate SIGPIPE false-negative (fixed) and check-all sibling-repo path mismatch (open)
metadata:
  node_type: memory
  type: feedback
  originSessionId: 8678d66a-8660-4ebd-bb70-9222d55deb83
---

Two distinct pre-push hooks in workspace-hub blocked a legitimate push during #2925 (skills propagation). Both are environment/tooling defects, NOT missing work.

**1. review-gate SIGPIPE false-negative (FIXED in commit e0c1e9767, branch fix/track-fleet-skills-2925-portable, not yet on origin).** `scripts/enforcement/require-review-on-push.sh` (called by `.git/hooks/pre-push.sh`) detected review evidence via `find … | grep -q .` and `git log … | grep -qiE …`. Under the script's `set -o pipefail`, `grep -q` exits on first match and closes the pipe → upstream `find`/`git log` dies with SIGPIPE (exit 141) → pipefail propagates 141 as pipeline failure → genuine evidence (today-dated `scripts/review/results/*` file AND commit subjects containing review/codex/gemini/adversarial) read as ABSENT → strict-mode block. Fix: capture via command-substitution `[[ -n "$(find …)" ]]` and here-string `grep -qiE … <<< "$var"` so no pipe → no SIGPIPE. **Why it's sneaky:** the same pipeline returns 0 when run interactively (find finishes before grep closes the buffer); it only fails reliably inside the hook context. Don't trust an isolated repro.

**2. check-all sibling-repo path mismatch (OPEN).** After the review-gate passes, `pre-push` runs `check-all` which executes sibling-repo test suites at NESTED paths `/mnt/local-analysis/workspace-hub/{assetutilities,digitalmodel,worldenergydata,assethold}` — but on this machine those repos are SIBLINGS at `/mnt/local-analysis/{repo}` (verified: `digitalmodel/.venv` and `assetutilities` exist as siblings; nested paths exist on NO machine). So check-all fails `directory not found` and rejects every verified push from here. Auto-sync pushes succeed anyway (likely `--no-verify` or different cwd). To land a normal push you must resolve/skip check-all (needs user-authorized bypass; `SKIP_REVIEW_GATE=1` is auto-denied by the harness classifier as a load-bearing control).

**How to apply:** When a workspace-hub push is "rejected" but your work is committed+reviewed, read the FULL pre-push output — there are ≥3 stacked gates (review-gate, secrets, coverage-ratchet, check-all, config-drift). The blocker is often a tooling/layout bug, not your change. Never `SKIP_REVIEW_GATE=1` (harness denies it); fix the gate or escalate to the user. Related: [[feedback_autosync_silent_pusher]] (auto-sync pushed my pre-amend commit to a stale branch → forced a new branch name), [[feedback_recover_stale_branch_for_pr]].
