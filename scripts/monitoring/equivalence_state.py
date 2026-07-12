#!/usr/bin/env python3
"""equivalence_state.py — share per-machine fingerprints via a dedicated git ref.

Mirrors the proven ``dispatch_leader.py`` GitLeaderStateStore idiom: state lives in
a dedicated ref (``equivalence-state``) written with git plumbing (hash-object /
mktree / commit-tree) and pushed with ``--force-with-lease`` — so it never churns
``main``. The ref's tree holds one ``<role>.json`` blob per box.

Part of the machine-equivalence drift sentinel (#3059, epic #3058).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

DEFAULT_REF = "equivalence-state"


class StoreUnavailable(RuntimeError):
    pass


def _git(repo, *args, _input=None, _env=None):
    env = {**os.environ, **_env} if _env else None
    return subprocess.run(["git", "-C", repo, *args], input=_input,
                          capture_output=True, text=True, env=env)


# The equivalence-state ref is a disconnected plumbing-built chain: the
# pre-push hook can never attribute its diff (no merge-base with main) and
# gates every publish as a new-branch RUN_ALL — a 60+ min full-suite run that
# keeps the ref from ever landing (#3500, sub-case of #3198). Push with the
# hook's audited soft bypass; each use is logged to pre-push-bypass.jsonl.
_PUSH_ENV = {"GIT_PRE_PUSH_SKIP": "1"}


def _fetch_tip(repo, remote, ref):
    """Return the commit SHA of the remote ref, or None if it doesn't exist yet."""
    ls = _git(repo, "ls-remote", "--exit-code", remote, ref)
    if ls.returncode == 2:
        return None
    if ls.returncode != 0:
        raise StoreUnavailable(f"git ls-remote failed: {ls.stderr.strip()[:200]}")
    tracking = f"refs/equivalence-tracking/{ref}"
    f = _git(repo, "fetch", "--quiet", remote, f"+{ref}:{tracking}")
    if f.returncode != 0:
        raise StoreUnavailable(f"git fetch failed: {f.stderr.strip()[:200]}")
    rev = _git(repo, "rev-parse", "--verify", "--quiet", tracking)
    return rev.stdout.strip() or None


def _tree_entries(repo, parent):
    """name -> blob sha for each top-level *.json in the ref tree."""
    if parent is None:
        return {}
    ls = _git(repo, "ls-tree", parent)
    out = {}
    for line in ls.stdout.splitlines():
        meta, _, name = line.partition("\t")
        parts = meta.split()
        if len(parts) == 3 and parts[1] == "blob" and name.endswith(".json"):
            out[name] = parts[2]
    return out


def collect(repo, *, remote="origin", ref=DEFAULT_REF):
    """Return list of fingerprint dicts currently published by all boxes."""
    parent = _fetch_tip(repo, remote, ref)
    fps = []
    for name, sha in _tree_entries(repo, parent).items():
        show = _git(repo, "cat-file", "-p", sha)
        if show.returncode == 0:
            try:
                fps.append(json.loads(show.stdout))
            except ValueError:
                pass
    return fps


def publish(repo, role, content, *, remote="origin", ref=DEFAULT_REF, retries=3):
    """Publish this box's fingerprint as <role>.json into the ref. CAS with retry."""
    name = f"{role}.json"
    for _ in range(retries):
        parent = _fetch_tip(repo, remote, ref)
        entries = _tree_entries(repo, parent)
        h = _git(repo, "hash-object", "-w", "--stdin", _input=content)
        if h.returncode != 0:
            raise StoreUnavailable(f"hash-object failed: {h.stderr.strip()[:200]}")
        entries[name] = h.stdout.strip()
        mktree_in = "".join(f"100644 blob {sha}\t{n}\n" for n, sha in sorted(entries.items()))
        mk = _git(repo, "mktree", _input=mktree_in)
        if mk.returncode != 0:
            raise StoreUnavailable(f"mktree failed: {mk.stderr.strip()[:200]}")
        tree = mk.stdout.strip()
        commit_args = ["commit-tree", tree, "-m", f"chore(equivalence): {role} fingerprint"]
        if parent:
            commit_args += ["-p", parent]
        c = _git(repo, *commit_args)
        if c.returncode != 0:
            raise StoreUnavailable(f"commit-tree failed: {c.stderr.strip()[:200]}")
        commit = c.stdout.strip()
        if parent:
            push = _git(repo, "push", remote, f"{commit}:refs/heads/{ref}",
                        f"--force-with-lease=refs/heads/{ref}:{parent}",
                        _env=_PUSH_ENV)
        else:
            push = _git(repo, "push", remote, f"{commit}:refs/heads/{ref}",
                        _env=_PUSH_ENV)
        if push.returncode == 0:
            return True
        blob = (push.stdout + push.stderr).lower()
        if not any(s in blob for s in ("rejected", "non-fast-forward", "stale info",
                                       "fetch first", "already exists")):
            raise StoreUnavailable(f"push failed: {push.stderr.strip()[:200]}")
        # else: lost the race, retry from a fresh tip
    return False


def main(argv=None):
    ap = argparse.ArgumentParser(description="Publish/collect equivalence fingerprints via git ref")
    ap.add_argument("cmd", choices=["publish", "collect"])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--role", help="role for publish (e.g. full, contribute)")
    ap.add_argument("--file", help="fingerprint JSON file to publish")
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--ref", default=DEFAULT_REF)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "publish":
            if not a.role or not a.file:
                ap.error("publish requires --role and --file")
            content = open(a.file).read()
            ok = publish(a.repo, a.role, content, remote=a.remote, ref=a.ref)
            print("published" if ok else "publish lost CAS race after retries", file=sys.stderr)
            return 0 if ok else 1
        fps = collect(a.repo, remote=a.remote, ref=a.ref)
        print(json.dumps(fps, indent=1))
        return 0
    except StoreUnavailable as e:
        print(f"equivalence-state unavailable: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
