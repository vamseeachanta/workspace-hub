# Plan for #4220: feat(hygiene): generic inventory of work files outside any git repository

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-11-04
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/4220
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-11-04-plan-4220-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/operations/surface-inventory.sh` — bash script, repo-centric, iterates subdirectory clones/worktrees, classifies as CLONE/WORKTREE/PLAIN, outputs git stats per repo; does NOT walk for files outside git repos and produces no JSON manifest
- Found: `scripts/operations/workstation-hygiene.sh` — bash script, `--root DIR`, `--apply`, `--sizes`, `--caches` flags; reports/removes disk residue from agent runs; does NOT classify files by git-membership
- Found: `docs/plans/2026-09-03-issue-3816-generated-work-surface-inventory.md` — scope: repo membership and adapter expectations per surface; different domain — #4220 focuses on files NOT inside any git repo
- Found: `scripts/operations/tests/` — existing test directory with `test_workstation_hygiene.sh`, `test_job_queue_*.py`, `test_rollout_claude_permissions.sh`, `test_solver_campaign_runner.py`; new test file lands here
- Gap: no Python tool exists that walks a directory tree and classifies files by git-membership; `surface-inventory.sh` does not expose this information
- Gap: `scripts/operations/outside-git-inventory.py` does not exist

### Standards

| Standard | Status | Source |
|---|---|---|
| N/A — internal hygiene tooling | — | — |

### LLM Wiki pages consulted

- No relevant wiki pages for outside-git inventory patterns in this repo.

### Documents consulted

- Issue [#4220](https://github.com/vamseeachanta/workspace-hub/issues/4220) — specifies: root dir, repos list, config YAML, manifest output at run time; "No host or machine paths in code"; read-only; counts and classifies files outside every git repo; allow-list for caches
- `docs/plans/2026-09-03-issue-3816-generated-work-surface-inventory.md` — prior art for work-surface inventory; confirms this is a different scope
- `scripts/operations/surface-inventory.sh` — confirms bash-only prior art; not reusable as Python manifest output
- `scripts/operations/workstation-hygiene.sh` — scope is disk residue removal, not git-membership classification

### Gaps identified

- `scripts/operations/outside-git-inventory.py` does not exist; must be created from scratch
- `scripts/operations/tests/test_outside_git_inventory.py` does not exist; must be created for TDD
- No Python utility in this repo checks whether an arbitrary file path is inside a specific git checkout

### Evidence (embedded verification)

**Issue statuses** (verified 2026-11-04T via `gh issue view`):
- `#4220` — OPEN — feat(hygiene): generic inventory of work files outside any git repository

**File existence** (`ls` 2026-11-04):
- EXISTS: `scripts/operations/surface-inventory.sh`
- EXISTS: `scripts/operations/workstation-hygiene.sh`
- EXISTS: `scripts/operations/tests/` (directory, with test files)
- MISSING (new — this plan creates): `scripts/operations/outside-git-inventory.py`
- MISSING (new — this plan creates): `scripts/operations/tests/test_outside_git_inventory.py`

**Gap proofs**:
- `ls scripts/operations/outside-git-inventory.py 2>&1` → "No such file or directory"
- `grep -rl "outside.*git\|git.*outside\|not.*repo\|outside.*repo" scripts/operations/` → empty → no existing implementation

**Abandoned Codex branches** (`git branch -r | grep 4220` 2026-11-04):
- `codex/hyg4220-work`, `codex/nwh4220-work`, `codex/spy4220-work` — all exist
- `gh pr list --repo vamseeachanta/workspace-hub --head codex/hyg4220-work` → no open PRs → abandoned; no parallel work in progress

**Issue labels** (verified 2026-11-04):
- `#4220` carries `gate:completeness`, `gate:completeness-v2` only — no `status:working`

<!-- Verification: distinct sources — issue body (#1), surface-inventory.sh (#2), workstation-hygiene.sh (#3), prior plan #3816 (#4), Codex branch + PR check (#5). Current count: 5 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-11-04-issue-4220-outside-git-inventory.md |
| Implementation | `scripts/operations/outside-git-inventory.py` |
| Tests | `scripts/operations/tests/test_outside_git_inventory.py` |
| Plan review — Claude | scripts/review/results/2026-11-04-plan-4220-claude.md |
| Plan review — Codex | scripts/review/results/2026-11-04-plan-4220-codex.md |
| Plan review — Gemini | scripts/review/results/2026-11-04-plan-4220-gemini.md |

---

## Deliverable

A host-agnostic Python script `scripts/operations/outside-git-inventory.py` that, given a root directory, a list of git repository paths, and an optional config YAML, walks the root tree, classifies files not inside any listed repository (with an allow-list for caches), and writes a JSON manifest — with full TDD coverage.

---

## Pseudocode

```
function is_inside_any_repo(path, repo_roots):
    # Uses path.resolve().relative_to(repo.resolve()) to test prefix membership
    for repo in repo_roots:
        try:
            path.resolve().relative_to(repo.resolve())
            return True, repo
        except ValueError:
            continue
    return False, None

function load_allowlist(config_path):
    # Returns set of glob patterns for cache/ephemeral files (not flagged as "work")
    # Default patterns: "*.pyc", "__pycache__/**", ".git/**", "node_modules/**", "*.egg-info/**"
    if config_path is None:
        return DEFAULT_CACHE_PATTERNS
    cfg = yaml.safe_load(config_path.read_text())
    return set(cfg.get("allowlist", DEFAULT_CACHE_PATTERNS))

function walk_outside_git(root, repo_roots, allowlist):
    outside = []
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        inside, _ = is_inside_any_repo(path, repo_roots)
        if inside:
            continue
        if any(path.match(pat) for pat in allowlist):
            category = "cache"
        else:
            category = "work"
        outside.append({
            "path": str(path),
            "category": category,
            "size": path.stat().st_size,
        })
    return outside

function main():
    # CLI: --root DIR --repos REPO [REPO ...] --config CONFIG_YAML --out MANIFEST_PATH [--dry-run]
    args = parse_args()
    root = Path(args.root)
    assert root.exists(), f"root does not exist: {root}"
    repo_roots = [Path(r) for r in args.repos]
    allowlist = load_allowlist(Path(args.config) if args.config else None)
    entries = walk_outside_git(root, repo_roots, allowlist)
    manifest = {
        "schema_version": 1,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "root": str(root),
        "repos_checked": [str(r) for r in repo_roots],
        "total": len(entries),
        "work_files": sum(1 for e in entries if e["category"] == "work"),
        "cache_files": sum(1 for e in entries if e["category"] == "cache"),
        "entries": entries,
    }
    if args.dry_run:
        print(f"dry-run: {manifest['work_files']} work files, {manifest['cache_files']} cache files")
        return
    if args.out:
        Path(args.out).write_text(json.dumps(manifest, indent=2))
    else:
        json.dump(manifest, sys.stdout, indent=2)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/operations/outside-git-inventory.py` | main implementation — host-agnostic, read-only, standard library only (plus PyYAML for config); PEP-723 inline deps for `uv run --script` |
| Create | `scripts/operations/tests/test_outside_git_inventory.py` | TDD test suite using temp dirs; no hardcoded paths |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_file_inside_repo_excluded | files inside a listed repo are not in manifest | temp dir with one sub-repo; one file inside repo | manifest `total` = 0, `entries` = [] |
| test_file_outside_repo_included | files outside all repos appear in manifest | temp dir; file outside repos | manifest `total` = 1, `entries[0].category` = "work" |
| test_cache_pattern_classified | files matching allowlist pattern classified as cache | temp dir; file matching `*.pyc`; config allowlist has `*.pyc` | entry with `category` = "cache" |
| test_no_host_paths_in_output | manifest paths derive from args, no hardcoded machine paths | temp dir at `/tmp/testXXX` | manifest `root` matches argument value |
| test_manifest_schema_fields | output JSON has required top-level fields | nominal run | keys: schema_version, generated_at, root, repos_checked, total, work_files, cache_files, entries |
| test_empty_root | empty directory produces empty manifest | temp dir with no files | total=0, entries=[] |
| test_out_file_written | --out writes manifest to specified path | `--out /tmp/manifest.json` | file exists, parses as valid JSON |
| test_nested_repo_inside_root | files under a nested repo excluded when repo listed | temp dir containing a git-inited sub-repo | only files outside sub-repo listed |

---

## Acceptance Criteria

- [ ] `uv run pytest scripts/operations/tests/test_outside_git_inventory.py -v` passes all 8 tests
- [ ] `uv run scripts/operations/outside-git-inventory.py --root /tmp --repos /tmp --out /tmp/manifest.json` runs without error
- [ ] The script contains no hardcoded host or machine paths — all paths passed at runtime
- [ ] The script is read-only: no file mutations, no git writes
- [ ] All entries in the manifest `entries` array have `path`, `category`, and `size` fields
- [ ] `schema_version`, `generated_at`, `root`, `repos_checked`, `total`, `work_files`, `cache_files`, `entries` present in every manifest
- [ ] No regression: `uv run pytest tests/ -x --ignore=tests/quarantine` passes

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | — | pending |
| Codex | — | pending |
| Gemini | — | pending |

**Overall result:** pending (plan is draft)

Revisions made based on review:
- (none yet)

---

## Retention

**Basis:** [Boundary policy, Section 8.1](../document-intelligence/durable-vs-transient-knowledge-boundary.md#81-retention-schedule)

```json
{
  "issue": "#4220",
  "artifact_class": "plan",
  "issue_state": "open",
  "closed_on": null,
  "retention_days": 30,
  "retention_basis": "../document-intelligence/durable-vs-transient-knowledge-boundary.md#81-retention-schedule",
  "retention_status": "advisory",
  "disposition": "archive"
}
```

No fixed expiry while issue is open.

---

## Risks and Open Questions

- **Risk:** `Path.rglob("*")` on a large root directory (e.g., `/mnt/local-analysis`) can be slow; a `--max-depth` option may be warranted in a follow-on
- **Risk:** Symlinks in the directory tree could cause cycles; `rglob` follows symlinks by default — confirm `follow_symlinks=False` as the default or add `--follow-symlinks` flag; flag for user during approval
- **Open:** Should the allow-list defaults be baked in or required via `--config`? Current plan: a sensible default set (`*.pyc`, `__pycache__/**`, `.git/**`, `node_modules/**`) with override via `--config`

---

## Complexity: T2

**T2** — two new files (implementation + test suite), no existing files modified, TDD required, disposable temp dirs for test isolation.
