# Sibling SSoT Implementation Review Notes

Use this reference when hardening or reviewing sibling-repo SSoT implementation work after local tests have passed.

## Review split: stale vs valid provider findings

When Codex/Gemini reviews disagree with current files:

1. Verify the exact on-disk artifact named by the finding before accepting or rejecting it.
2. Mark findings as stale only with concrete evidence: file path, current line/content, and the reviewer claim being contradicted.
3. Do not let one stale finding invalidate the whole review. Extract still-valid blockers from the same review and fix them.
4. Rerun compact review after fixing valid blockers, with prompts pointing at the latest staged diff/artifacts.

## Portable script hardening patterns

Sibling SSoT scripts are expected to run across Linux, Windows Git Bash, and sometimes macOS-like environments. Avoid Linux-only assumptions unless the script explicitly gates by workstation.

- If a helper shells out to Linux utilities such as `findmnt`, guard with `shutil.which()` or catch `FileNotFoundError`, `TimeoutExpired`, and `OSError`; return a structured fallback such as `"unknown"` rather than crashing.
- If Bash pipes Python through stdin and falls back from system `python3` to `uv`, include Python dependencies explicitly. For PyYAML-backed stdin snippets, use:

```bash
uv run --with pyyaml --no-project python "$@"
```

Plain `uv run --no-project python "$@"` does not ensure `yaml` is importable in a fresh isolated environment.

## Closeout checklist additions

Before commit/push/issue closeout for sibling SSoT changes:

- Targeted tests pass for registry, Hermes config rendering, sibling symlink contracts, repair dry-run/apply safety, and remote workstation ground truth.
- `git diff --cached --check` passes.
- Provider review has no unresolved MAJOR; stale findings are explicitly contradicted with artifact evidence.
- Staged diff is checked for accidental memory bridge churn or agent-worktree path leakage.
