> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_python_m_build_no_isolation_flag.md

---
name: python-m-build-no-isolation-flag
description: `python -m build` has no `--isolation` flag — isolated builds are the default; `--no-isolation` is the opt-out. Verified 2026-05-03 during #2617 implementation.
type: feedback
originSessionId: 20bbbf35-b8fa-4295-a1b2-59fd2252ff45
---
`python -m build` (PyPA `build` package) does NOT have an `--isolation` flag. Isolation is the default behavior: build deps install into a fresh PEP-517 venv per invocation. The flag that exists is `--no-isolation` — the opt-out.

**Why:** Verified 2026-05-03 during #2617 implementation when an agent caught my prompt's mistake. I told the agent to "use `--isolation` instead of `--no-isolation`". The correct fix (and what the agent applied) is to **remove `--no-isolation` entirely** — same semantic outcome (isolated builds), correct CLI surface.

**How to apply:** When a test or script uses `python -m build --wheel --no-isolation`, restore isolation by deleting the `--no-isolation` flag, NOT by adding `--isolation`. If a future prompt mentions `--isolation`, treat as a hint and verify against `python -m build --help` before passing through to the implementer.

**Why `--no-isolation` is dangerous in tests:** with `--no-isolation`, the build subprocess writes intermediate artifacts to `<cwd>/build/` and `<cwd>/*.egg-info/` instead of an isolated tmpdir. Parallel pytest sessions building wheels concurrently race on these shared paths. Symptom: flaky `[Errno 2] No such file or directory` on `build_wheel` invocation.

**Memory ref:** flagged by #2566 → filed as #2617 → fixed via digitalmodel PR #567 (squash-merged 2026-05-03 20:27Z).
