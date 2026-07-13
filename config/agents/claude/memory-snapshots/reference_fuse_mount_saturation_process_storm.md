---
name: reference-fuse-mount-saturation-process-storm
description: "NTFS-FUSE /mnt/local-analysis \"timeouts\" are often a runaway process storm, not just inherent slowness — diagnose before blaming the mount"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 72917795-b034-44fd-bee2-a663bced5400
---

The `/mnt/local-analysis` NTFS-FUSE mount is inherently slow, BUT a large share of "filesystem timed out" stalls (git rev-parse exit 124, pytest never starting, `import numpy` timing out at 60s) is a **runaway/stuck process storm saturating mount I/O**, not baseline slowness. Diagnose before concluding "the mount is just slow."

**Diagnostic that nails it:** `ps -eo pid,ppid,stat,etimes,%cpu,cmd --sort=-%cpu`. Tells:
- N identical processes sharing one ppid, age hours, 0% CPU = a deadlocked fan-out (e.g. ~24 `uv` `pip_compileall.py` byte-compile workers stuck 2.7h — byte-compilation should take seconds).
- Long-running `run-all-tests.sh --coverage` + `uv run pytest -v tests/ --cov` (age hours) = the dominant churner; coverage instrumentation re-reads the whole tree from FUSE.
- Multi-hour `rg`/`find` over /mnt/local-analysis from other claude/codex sessions = pure read churn.
- Stale `equivalence_state.py publish` (equality-matrix cron) + git-push-with-hooks, ages 4–16h.
- `mount.ntfs-3g` in **D state** at high %CPU = FUSE driver saturated.

**Litmus test for "mount vs code":** `python -c "print('hi')"` is instant (no site-packages read); `python -c "import numpy"` timing out at 60s proves the FUSE `.venv` is the bottleneck — NOT your code. Any pytest is hopeless until cleared.

**Fixes (in order):**
1. Kill the deadlocked fan-out + stale read-only searches (regenerable/safe). Killing another session's jobs needs USER approval — the auto-mode classifier denies process kills the user didn't name; ask with specific PIDs/patterns. SIGTERM often ignored (D-state) → SIGKILL.
2. If still slow (cold cache after thrash, or unkillable wrappers respawn pytest), don't fight it: **run from a shallow sparse clone on LOCAL disk** (scratchpad is local), or use `gh search code --repo` for repo-content questions. Same fix unblocks the "Leibniz" HF worktree stall ([[project_bokalift_diffraction_licensed_run]] session, 2026-07-11).
3. To commit when local pytest is impossible: verify offline (ruff = the CI linter; black/isort), commit via **GitHub Contents API** (porcelain git also stalls here), open PR, and **let CI run the tests in a clean env** — note the caveat in the PR body. Did this for dm PR #1539 (#1537 diffraction report).

Related: [[reference_ntfs_fuse_git_stalls_local_analysis]] (git-specific), [[feedback_verify_against_real_ci_lint_toolchain]] (ruff≠flake8: this repo gates on ruff, whose default ignores E501).
