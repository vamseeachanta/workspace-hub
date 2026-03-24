# WRK-643 Verification Summary

## Scope

Stabilize workspace-hub `uv` execution for hooks and hook-adjacent queue tools by
defaulting to a repo-local writable cache.

## Files Changed

- `scripts/lib/uv-env.sh`
- `.claude/hooks/check-encoding.sh`
- `scripts/operations/setup-hooks.sh`
- `.claude/work-queue/scripts/generate-index.py`
- `scripts/work-queue/generate-html-review.py`

## Strategy

- define a shared helper that exports `UV_CACHE_DIR` under
  `.claude/state/uv-cache` unless already overridden
- source that helper from the hook script that invokes `uv`
- replace `uv` shebang-only entry points with shell/Python polyglot launchers so
  the repo-local cache is set before `uv` starts

## Validation Commands

```bash
bash .claude/hooks/check-encoding.sh
./.claude/work-queue/scripts/generate-index.py
./scripts/work-queue/generate-html-review.py WRK-643
bash scripts/work-queue/validate-queue-state.sh
```

## Results

- `check-encoding.sh` executed without requiring `/home/<user>/.cache/uv`
- `generate-index.py` regenerated `.claude/work-queue/INDEX.md`
- `generate-html-review.py WRK-643` generated
  `.claude/work-queue/assets/WRK-643/review.html`
- `validate-queue-state.sh` passed
- repo-local cache directory created at `.claude/state/uv-cache`

## Notes

- This fixes the specific failure mode seen during commit-hook execution in
  sandboxed environments where `/home/<user>/.cache/uv` is not writable.
- The helper preserves external overrides by honoring an existing
  `UV_CACHE_DIR`.
