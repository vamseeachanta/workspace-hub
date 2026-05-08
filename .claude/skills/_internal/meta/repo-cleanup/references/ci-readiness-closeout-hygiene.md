# CI-Readiness Closeout Hygiene Sweep

Use after a multi-repo CI/test repair stream, especially when implementation patches are already merged but generated/session artifacts remain dirty.

## Trigger

- Tier-1 repo CI/test fixes are complete or merged.
- Remaining dirt is mostly provider telemetry, session state, quick review prompts/logs, audit reports, or skill-reference evidence.
- User expects transactional closeout: push/merge, branch/worktree disposition, cleanup/removal or explicit evidence preservation, and clean-state proof in the same window.

## Workflow

1. **Inventory before touching anything** per repo:
   ```bash
   git fetch origin --quiet
   git status --short
   git diff --stat
   git diff --name-only
   git ls-files --others --exclude-standard
   git rev-list --left-right --count HEAD...@{u}
   ```
2. **Classify every dirty path**:
   - Durable evidence: plans, review result markdown, skill references, audit lessons, committed closeout ledgers.
   - Recurring generated telemetry worth preserving: provider quota/scorecard/work-queue JSON + matching Markdown reports when those are tracked governance artifacts.
   - Disposable/session churn: `.claude/state/*`, quick prompt/log launch files, transient `.out` files, local session signals, stale generated data/logs with durable copies elsewhere.
3. **Verify durable copies before deleting disposable quick artifacts**:
   ```bash
   git ls-files docs/plans/<plan>.md scripts/review/results/<review-prefix>-*.md
   ```
   Only remove quick prompt/log files after durable plan/review artifacts are tracked and synced.
4. **Secret-scan and validate candidate durable artifacts before commit**:
   ```bash
   grep -Eni 'api[_-]?key|secret|token|password|passwd|bearer|authorization|client_secret|private[_-]?key' <candidate-files> || true
   uv run python - <<'PY'
   import json
   for path in ["config/ai-tools/provider-routing-scorecard.json"]:
       json.load(open(path))
       print(f"ok {path}")
   PY
   git diff --check -- <candidate-files>
   ```
5. **Stage narrowly**. Never `git add .` in closeout hygiene. Stage only classified durable/recurring artifacts; leave or restore disposable session churn.
6. **Commit/push durable artifacts**. If a post-commit ledger appends a new tracked line, make a second narrow ledger commit rather than leaving a new dirty tracked file.
7. **Final proof across repos**:
   ```bash
   git fetch origin --quiet
   git branch --show-current
   git rev-parse --short HEAD
   git rev-parse --abbrev-ref --symbolic-full-name @{u}
   git rev-list --left-right --count HEAD...@{u}
   git status --short
   ```

## Gotchas

- A remote-rejected push can still have landed if another process advanced `origin/main` to the same commit; always `git fetch` and compare `HEAD`, `origin/main`, and ahead/behind before retrying.
- `.claude/state/*` and session-signal JSONL are usually live session churn, not durable evidence. Restore/remove them after durable artifacts are safely committed.
- In parent/nested repo layouts, root `workspace-hub` must not stage nested repo files; run repo-local commands from each repo root.
- Deleted quick-review files may survive as `.fuse_hidden*` while provider/review processes still hold file descriptors. Use `lsof +D <dir>` to identify holders, wait for valid runs to finish, and only terminate clearly stalled/disposable processes before removing the released FUSE-hidden files.
- Concurrent automation can create or commit related artifacts while closeout is running. Re-fetch/re-status after each commit/push, classify any new dirt as task-owned vs unrelated, and never stage unrelated skill/session churn just to make the tree clean.
