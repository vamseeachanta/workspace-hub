---
name: Path.parent walk needs a sentinel — root is its own parent
description: Code that walks up the filesystem with `repo = repo.parent` until a marker is found will infinite-loop at `/` — `Path('/').parent == Path('/')`. Always add a sentinel; preferable to detect environment by env var rather than by file existence.
type: feedback
originSessionId: ec40ba65-385e-48da-98c7-8cf5a6f30e44
---
A common notebook pattern walks up the filesystem looking for a project marker:

```python
repo = Path.cwd().resolve()
while not (repo / 'pyproject.toml').exists():
    repo = repo.parent
```

**This silently infinite-loops** if the marker doesn't exist anywhere on the path. `Path('/').parent` returns `Path('/')` — the loop never terminates because `parent` doesn't fail or return None at the root.

**Why this bites in practice:** environments like Kaggle, CI runners, container scratch volumes, and read-only mounts won't have your project marker anywhere upstream. Your local smoke test passes because `pyproject.toml` is 1–2 levels up; in the foreign environment, the walk goes to `/` and hangs.

Concrete incident, 2026-05-06: `kaggle-rogii-2026/notebooks/00_baseline_carry_forward.ipynb` shipped to Kaggle with this exact pattern in the `else` (non-Kaggle) branch. When path-based environment detection fell through to the else branch on Kaggle, the loop ran for **12 hours** until Kaggle's `CellTimeoutError` killed it. Cost: 12 hours of free-tier compute, no submission, blocked downstream issues. Recovery: file bug ([vamseeachanta/kaggle-rogii-2026#9](https://github.com/vamseeachanta/kaggle-rogii-2026/issues/9)), draft fix plan, re-push.

**How to apply:**

1. **Always add a sentinel** to upward filesystem walks:
   ```python
   for _ in range(10):  # bounded
       if (repo / 'pyproject.toml').exists():
           break
       if repo.parent == repo:
           raise RuntimeError(f'pyproject.toml not found walking up from {Path.cwd()}')
       repo = repo.parent
   else:
       raise RuntimeError('pyproject.toml not found after 10 levels')
   ```
2. **Prefer environment detection by env var, not file existence.** Kaggle sets `KAGGLE_KERNEL_RUN_TYPE`. CI runners set `CI`. Docker sets `/.dockerenv`. These are explicit signals; file-existence checks are brittle.
3. **Pre-emptive fail-fast at the boundary.** When entering a known environment, validate that *expected* things are mounted (e.g., on Kaggle, raise immediately if `/kaggle/input/<slug>` is missing — with a hint about `kernel-metadata.json` `competition_sources`).
4. **Smoke test in the foreign environment, not just locally.** A 5-minute Kaggle dry-run of just the imports + path detection (no modeling) would have caught this in seconds rather than burning 12 hours.

The pattern generalizes beyond paths: any `while next_state != current_state: current_state = next_state(current_state)` loop where `next_state` can be a fixed point of itself needs a sentinel.
