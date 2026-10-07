# Plan for #3932: wiki frontmatter validation silently skips arbitrarily named worktrees

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-10-07
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3932
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-10-07-plan-3932-claude.md | ...-codex.md | ...-agy.md

---

## Resource Intelligence Summary

### Existing repo code

- EXISTS: `scripts/enforcement/check-wiki-sibling-frontmatter.py` (297 lines) — `main()` at lines 224–292 resolves repo identity via `git rev-parse --show-toplevel` (line 239) and uses `Path(repo_root_str).name` (line 243) as the repo name. When a worktree is named `wt-wiki-cabledyn-3931`, `Path.name` returns `"wt-wiki-cabledyn-3931"`, which fails the `repo_name != "llm-wiki" and not repo_name.startswith("llm-wiki-")` guard (line 246), causing the script to exit 0 without validating any staged files. Conversely, a worktree named `llm-wiki-cabledyn` incorrectly derives `expected_client_slug = "cabledyn"` (line 251) from the worktree name rather than the actual remote repository identity.
- EXISTS: `tests/enforcement/test_check_wiki_sibling_frontmatter.py` (19 test cases) — all existing tests use `_make_wiki_repo(tmp_path, name)` which names the test repo directory after the desired identity (e.g., `llm-wiki-mkt-a`). No test creates a repo where the checkout directory name differs from the remote origin slug. The fixture strategy at lines 42–63 creates hermetic git repos but sets no remote, so the `git remote get-url origin` path is not exercised.
- EXISTS: `.claude/rules/wiki-sibling-routing.md` — Rule C: "client slug must match repo identity AND exist in registry". The rule states identity is derived from `basename(git rev-parse --show-toplevel)`, matching the current implementation — the rule itself needs no change, but the implementation must align with canonical remote identity rather than checkout basename.
- EXISTS: `scripts/agents/install-pre-commit-hook-cross-repo.sh` — installs the frontmatter check as a pre-commit hook in wiki repos. Worktree checkouts inherit this hook from the main repo, so the bug surfaces whenever a developer uses `git worktree add` with a non-canonical directory name.

### Standards

Not applicable — this is a Python enforcement script issue.

### LLM Wiki pages consulted

No relevant wiki pages — wiki frontmatter enforcement is a workspace-hub tooling concern.

### Documents consulted

- Issue body [#3932](https://github.com/vamseeachanta/workspace-hub/issues/3932) — describes exact failure: `wt-wiki-cabledyn-3931` exits 0 without validating; `llm-wiki-cabledyn` incorrectly treats as a client wiki. Specifies fix: "resolve repository identity from verified canonical metadata and add regression tests for canonical generic/client checkouts and arbitrarily named worktrees." Confirms intake workaround: direct `_validate()` invocation with explicit owner.
- Issue [#3931](https://github.com/vamseeachanta/workspace-hub/issues/3931) (CableDyn intake) — the triggering context; a worktree named for the intake task rather than the repo was used for staged CableDyn content, exposing the identity resolution gap.
- `docs/plans/2026-05-22-issue-2778-wiki-sibling-routing-contract.md` — prior plan establishing the enforcement script. Specifies "repo-identity via git rev-parse, NOT path-prefix" (r2-F1) in the test coverage notes — this rule was intended to address path-prefix matching but did not anticipate worktree basename divergence from remote name.
- `scripts/enforcement/check-wiki-sibling-frontmatter.py` lines 239–251 — the identity resolution code path; `git rev-parse --show-toplevel` returns the worktree path, not the primary checkout path for git worktrees added with `git worktree add <path>`.

### Gaps identified

- No `git remote get-url origin` fallback for worktrees in `check-wiki-sibling-frontmatter.py`.
- No test covering a repo where checkout directory name differs from the remote origin repo name.
- No test covering `git worktree add` scenarios (worktrees are always named with the exact canonical `llm-wiki` / `llm-wiki-<slug>` prefix in current fixtures).

### Evidence (embedded verification)

**Issue status** (verified 2026-10-07 via `gh issue view`):
- `#3932` — OPEN — fix: wiki frontmatter validation silently skips arbitrarily named worktrees

**File existence** (`ls` 2026-10-07 from live clone):
- EXISTS: `scripts/enforcement/check-wiki-sibling-frontmatter.py`
- EXISTS: `tests/enforcement/test_check_wiki_sibling_frontmatter.py`
- EXISTS: `.claude/rules/wiki-sibling-routing.md`
- EXISTS: `scripts/agents/install-pre-commit-hook-cross-repo.sh`

**Line excerpts** (from live checkout):
```
check-wiki-sibling-frontmatter.py:239-251:
    repo_root_str = _git_safe(["rev-parse", "--show-toplevel"])
    if repo_root_str is None:
        print("[wiki-frontmatter] not inside a git repo — skipping", file=sys.stderr)
        return 0
    repo_root = Path(repo_root_str)
    repo_name = repo_root.name

    if repo_name != "llm-wiki" and not repo_name.startswith("llm-wiki-"):
        # Not a wiki repo — bail early. Workspace-hub and other repos are out-of-scope.
        return 0

    is_client_wiki = repo_name.startswith("llm-wiki-")
    expected_client_slug = repo_name[len("llm-wiki-"):] if is_client_wiki else None
```

**Gap proofs**:
- `git worktree add /tmp/wt-wiki-cabledyn-3931 HEAD` inside `llm-wiki` → worktree directory name `wt-wiki-cabledyn-3931` → `repo_root.name = "wt-wiki-cabledyn-3931"` → bail early at line 246 → exit 0 (false pass, no validation).
- `git worktree add /tmp/llm-wiki-cabledyn HEAD` inside `llm-wiki` → `expected_client_slug = "cabledyn"` → Rule C fires on any `client:` that is not `"cabledyn"` (incorrect client identity applied to a generic wiki worktree).

**Reproduction proofs:**
- Issue body confirms direct reproduction during CableDyn intake 2026-10-01 (issue #3931 context). Code path confirmed by source read 2026-10-07.
- Failure mode observed matches issue claim: YES — `Path(repo_root_str).name` returns the worktree directory name, not the remote origin repo slug.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-10-07-issue-3932-wiki-frontmatter-worktree-identity.md` |
| Implementation | `scripts/enforcement/check-wiki-sibling-frontmatter.py` |
| Tests | `tests/enforcement/test_check_wiki_sibling_frontmatter.py` |
| Plan review — Claude | `scripts/review/results/2026-10-07-plan-3932-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-10-07-plan-3932-codex.md` |
| Plan review — Agy | `scripts/review/results/2026-10-07-plan-3932-agy.md` |

---

## Deliverable

`check-wiki-sibling-frontmatter.py` resolves repository identity from `git remote get-url origin` (parsed to extract the repo slug from the URL) rather than `Path(repo_root).name`; when no remote is configured, the script falls back to checkout basename (preserving existing behavior for offline hermetic fixtures). New tests cover: canonical generic worktree with arbitrary name, canonical client worktree with arbitrary name, and non-wiki worktree with an `llm-wiki-*`-shaped name.

---

## Pseudocode

```python
def _resolve_repo_identity(repo_root: Path) -> str | None:
    """Return the canonical repo name from remote origin URL, or None to fall back to basename."""
    url = _git_safe(["remote", "get-url", "origin"], cwd=repo_root)
    if not url:
        return None
    # Accept both SSH (git@github.com:owner/repo.git) and HTTPS (https://github.com/owner/repo.git)
    # Strip trailing .git, take the last path component
    name = url.rstrip("/").split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name or None

# In main(), replace:
#   repo_name = repo_root.name
# With:
#   repo_name = _resolve_repo_identity(repo_root) or repo_root.name
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/enforcement/check-wiki-sibling-frontmatter.py` | Add `_resolve_repo_identity()` helper; replace `repo_root.name` with remote-origin resolution + basename fallback |
| Modify | `tests/enforcement/test_check_wiki_sibling_frontmatter.py` | Add 3 new tests for worktree identity scenarios; extend `_make_wiki_repo` to accept optional remote URL |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_enforcement_resolves_identity_from_remote_origin` | Generic llm-wiki with worktree named `wt-wiki-task-123` still enforces correctly | Repo with remote `https://github.com/example/llm-wiki.git`, dir name `wt-wiki-task-123`, staged wiki page with valid generic frontmatter | exit 0 (pass) |
| `test_enforcement_resolves_client_slug_from_remote_origin` | Client wiki with worktree named `task-branch` resolves slug from remote | Repo with remote `https://github.com/example/llm-wiki-mkt-a.git`, dir name `task-branch`, staged page with `client: mkt-a` | exit 0 (pass with matching client slug) |
| `test_enforcement_rejects_wrong_client_in_remote_resolved_worktree` | Mismatched client slug still fails when identity is from remote | Repo with remote `https://github.com/example/llm-wiki-mkt-a.git`, dir name `wt-mkt-a-task`, staged page with `client: other-client` | exit 1, Rule C error |
| `test_enforcement_skips_arbitrary_worktree_of_non_wiki_repo` | Non-wiki remote with an `llm-wiki-*`-shaped checkout name bails early | Repo with remote `https://github.com/example/workspace-hub.git`, dir name `llm-wiki-temp` | exit 0 (bail early — remote identity is workspace-hub, not a wiki) |
| `test_enforcement_falls_back_to_basename_when_no_remote` | No remote configured → existing behavior preserved | Repo with no remote, dir name `llm-wiki` | exit 0 (pass for valid generic frontmatter) — same as current |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest tests/enforcement/test_check_wiki_sibling_frontmatter.py -v`
- [ ] No regression: all 19 existing test cases remain green
- [ ] A worktree of `llm-wiki` named `wt-wiki-cabledyn-3931` with a staged generic-wiki page correctly validates (exit 0 for valid frontmatter, exit 1 for invalid)
- [ ] A worktree of `llm-wiki` named `llm-wiki-cabledyn` with remote set to `https://github.com/vamseeachanta/llm-wiki.git` correctly identifies as generic (not client) and applies generic rules
- [ ] A worktree of `llm-wiki-mkt-a` named `wt-mkt-a-task-99` with remote set to `https://github.com/vamseeachanta/llm-wiki-mkt-a.git` correctly applies client rules with slug `mkt-a`
- [ ] Docs updated: comment in `_resolve_repo_identity` explains the worktree-naming hazard and the URL-parsing strategy

---

## Adversarial Review Summary

*To be filled after Step 4 completes.*

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | — | — |
| Codex | — | — |
| Agy | — | — |

---

## Risks and Open Questions

- **Risk:** The SSH remote URL format (`git@github.com:owner/repo.git`) differs from HTTPS. The pseudocode splits on `/` and takes the last component — for SSH this would return `repo.git` (then `.git` stripped), which is correct. However, exotic remote formats (e.g., `ssh://git@github.com/owner/repo`) parse the same way. Implementer must verify both SSH and HTTPS paths in test fixtures.
- **Risk:** The `_git_safe` fallback returns `None` on failure (line 60–65). If `git remote` returns a non-zero exit but with partial output, `_git_safe` returns `None`. The fallback to `repo_root.name` is safe but reintroduces the worktree-name problem for repos without a remote. This is acceptable for hermetic test fixtures and offline use. Document explicitly in the function's docstring.
- **Open:** Should the remote URL be required in installed wikis? The install script (`install-pre-commit-hook-cross-repo.sh`) always operates on repos with a remote, so the fallback-to-basename case applies only to offline fixtures and tests. A `--require-remote` flag could enforce fail-closed for installed hooks, but this is out of scope — mark as a follow-on.

---

## Complexity: T1

Single Python script modified (`check-wiki-sibling-frontmatter.py`) plus one test file extended. One new helper function (~10 lines). No schema changes, no new files created, no cross-repo edits.
