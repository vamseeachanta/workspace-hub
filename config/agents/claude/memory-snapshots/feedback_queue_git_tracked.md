---
name: Queue jobs must reference git-tracked files
description: Before submitting solver queue jobs, verify input files are git-tracked — untracked files won't exist on licensed-win-1
type: feedback
---

Never submit a solver queue job referencing a file that isn't tracked by git. The queue processor on licensed-win-1 does `git pull` then resolves paths relative to REPO_ROOT — untracked files simply don't exist there.

**Why:** L01 job failed on licensed-win-1 because the .owr source file (1.7MB) was local-only and not in git. Wasted a queue cycle and debugging time.

**How to apply:** Before running `submit-job.sh` or creating queue YAML, run `git ls-files <path>` to confirm the input file is tracked. If not, either `git add` + push it first, or choose an alternative approach (e.g., run the smoke test directly on the machine where the file exists).
