#!/usr/bin/env python3
"""Build a commit for the issue-2403-embeddings-spike branch without touching
the worktree index. Uses git ls-tree + mktree + commit-tree + update-ref.

Applies two changes vs current HEAD:
 - add   docs/reports/embeddings-spike/README.md         (new blob 0fb1fb867...)
 - mod   docs/document-intelligence/embeddings-model-selection.md (new blob c1a06445...)
"""
from __future__ import annotations
import subprocess
import sys

WORKTREE_GITDIR = "/mnt/local-analysis/workspace-hub/.git/worktrees/workspace-hub-issue-2403"
BRANCH_REF = "refs/heads/issue-2403-embeddings-spike"
PARENT_SHA = subprocess.check_output(
    ["git", f"--git-dir={WORKTREE_GITDIR}", "rev-parse", "HEAD"], text=True
).strip()

README_BLOB = "0fb1fb867f3fc946dc671923c68c2672f5f79da5"
DECISION_BLOB = "c1a064452ed7319b51a0ca70786eacf23dc4292d"


def git(*args: str, input_data: str | None = None) -> str:
    """Run a git command against the worktree's git-dir; return stdout."""
    cmd = ["git", f"--git-dir={WORKTREE_GITDIR}", *args]
    r = subprocess.run(cmd, input=input_data, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(f"FAIL: {' '.join(cmd)}\n{r.stderr}\n")
        sys.exit(r.returncode)
    return r.stdout


def ls_tree(tree_sha: str) -> list[tuple[str, str, str, str]]:
    """Return list of (mode, type, sha, name) entries."""
    out = git("ls-tree", tree_sha)
    entries = []
    for line in out.splitlines():
        meta, name = line.split("\t", 1)
        mode, typ, sha = meta.split()
        entries.append((mode, typ, sha, name))
    return entries


def mktree(entries: list[tuple[str, str, str, str]]) -> str:
    """Build a tree object from (mode, type, sha, name) entries."""
    body = "\n".join(f"{mode} {typ} {sha}\t{name}" for mode, typ, sha, name in entries)
    return git("mktree", input_data=body + "\n").strip()


def replace_entry(
    entries: list[tuple[str, str, str, str]],
    name: str,
    new_mode: str,
    new_type: str,
    new_sha: str,
) -> list[tuple[str, str, str, str]]:
    """Return entries with the named entry replaced (or appended if missing)."""
    result = [e for e in entries if e[3] != name]
    result.append((new_mode, new_type, new_sha, name))
    # Git trees are sorted; mktree will re-sort so order here doesn't matter.
    return result


def main() -> int:
    # Start at the root tree of the parent commit.
    root_tree = git("rev-parse", f"{PARENT_SHA}^{{tree}}").strip()

    # ── Path 1: docs/reports/embeddings-spike/README.md ────────────────────
    # Build leaf subtree (embeddings-spike) containing only README.md.
    emb_spike_tree = mktree([("100644", "blob", README_BLOB, "README.md")])

    # Descend to docs/reports and add/replace embeddings-spike entry.
    docs_entries = ls_tree(root_tree)
    docs_tree_sha = next(sha for mode, typ, sha, name in docs_entries if name == "docs")
    reports_entries = next(
        ls_tree(sha) for mode, typ, sha, name in ls_tree(docs_tree_sha)
        if name == "reports"
    )
    reports_entries = replace_entry(
        reports_entries, "embeddings-spike", "040000", "tree", emb_spike_tree
    )
    new_reports_tree = mktree(reports_entries)

    # ── Path 2: docs/document-intelligence/embeddings-model-selection.md ───
    docintel_entries = next(
        ls_tree(sha) for mode, typ, sha, name in ls_tree(docs_tree_sha)
        if name == "document-intelligence"
    )
    docintel_entries = replace_entry(
        docintel_entries,
        "embeddings-model-selection.md",
        "100644",
        "blob",
        DECISION_BLOB,
    )
    new_docintel_tree = mktree(docintel_entries)

    # ── Rebuild docs/ with updated reports/ and document-intelligence/ ─────
    docs_children = ls_tree(docs_tree_sha)
    docs_children = replace_entry(
        docs_children, "reports", "040000", "tree", new_reports_tree
    )
    docs_children = replace_entry(
        docs_children,
        "document-intelligence",
        "040000",
        "tree",
        new_docintel_tree,
    )
    new_docs_tree = mktree(docs_children)

    # ── Rebuild root tree with updated docs/ ───────────────────────────────
    root_entries = replace_entry(
        ls_tree(root_tree), "docs", "040000", "tree", new_docs_tree
    )
    new_root_tree = mktree(root_entries)

    # ── commit-tree + update-ref ───────────────────────────────────────────
    msg = (
        "docs(#2403): reference landed scaffold commit + reports dir README\n"
        "\n"
        "Scaffold re-verified on 2026-04-23 in the issue-2403 worktree:\n"
        "- 12/12 tests green via uv run pytest tests/knowledge/test_embeddings_spike.py\n"
        "- --scaffold-check CLI validates eval set (60 queries) and all 3 stub runners\n"
        "\n"
        "Changes here are documentation-only:\n"
        "- docs/document-intelligence/embeddings-model-selection.md: replace the\n"
        "  stale 'Scaffold landed at: commit pending this session.' header with\n"
        "  the actual landed SHA (405ea2dc7) and a 2026-04-23 re-verification note.\n"
        "- docs/reports/embeddings-spike/README.md: new placeholder that documents\n"
        "  per-model measurement report layout; makes the measurement output\n"
        "  directory exist in git (previously only referenced, not materialized).\n"
        "\n"
        "Scaffold runner/tests/eval-set are unchanged.\n"
    )
    new_commit = git(
        "commit-tree", new_root_tree, "-p", PARENT_SHA, "-m", msg
    ).strip()

    # Update branch ref
    git("update-ref", BRANCH_REF, new_commit, PARENT_SHA)
    print(f"commit {new_commit}")
    print(f"branch {BRANCH_REF} -> {new_commit}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
