"""Regression test: update-model-ids.sh must not rewrite OTHER copies of itself.

The script walks submodules and sibling worktrees, where the same file exists at a
different absolute path. The original guard compared realpath against BASH_SOURCE, so it
protected only the copy being executed and rewrote every other one -- turning each
'old|new' mapping pair into 'new|new'.

Measured on ace-linux-1 2026-07-30: 10 of 10 workspace-hub worktrees held an identically
corrupted copy. Every mapping in them is an identity no-op, so the script still exits 0
while detecting no drift -- indistinguishable from a fleet with no stale model IDs.
"""
import os
import shutil

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCRIPT = os.path.join(REPO, "scripts", "maintenance", "update-model-ids.sh")


def _guard_form() -> str:
    """Read which comparison the script's self-exclusion actually uses.

    Deliberately DERIVED from source rather than restated. An earlier draft of this
    test hardcoded the fixed condition, so the behavioural cases exercised the test
    helper and passed against the buggy script -- they proved nothing. Deriving the
    form means a revert to path-equality changes what the cases below observe.
    """
    for line in open(SCRIPT, encoding="utf-8").read().splitlines():
        s = line.strip()
        if s.startswith("if [[") and "BASH_SOURCE[0]" in s and '"$file"' in s:
            if "basename" in s:
                return "basename"
            if "realpath" in s:
                return "realpath"
            raise AssertionError(f"unrecognised self-exclusion comparison: {s}")
    raise AssertionError(
        "self-exclusion guard not found in update-model-ids.sh -- the condition "
        "moved or changed shape; update this detector rather than deleting the test"
    )


def _guard_skips(candidate: str) -> bool:
    """Apply the semantics of whichever comparison the script currently uses."""
    form = _guard_form()
    if form == "basename":
        return os.path.basename(candidate) == os.path.basename(SCRIPT)
    return os.path.realpath(candidate) == os.path.realpath(SCRIPT)


def test_guard_skips_the_executing_copy():
    assert _guard_skips(SCRIPT)


def test_guard_skips_a_copy_at_a_different_path(tmp_path):
    """The actual defect: a copy in another worktree must NOT be rewritten."""
    other = tmp_path / "worktree" / "scripts" / "maintenance"
    other.mkdir(parents=True)
    copy = other / "update-model-ids.sh"
    shutil.copyfile(SCRIPT, copy)
    assert _guard_skips(str(copy)), (
        "a copy of the script at a different absolute path was NOT skipped -- "
        "the script will rewrite its own mapping table into identity no-ops"
    )


def test_guard_does_not_skip_unrelated_files(tmp_path):
    """The fix must not become a blanket skip that silently does nothing."""
    ordinary = tmp_path / "some-doc.md"
    ordinary.write_text("claude-sonnet-4-5\n")
    assert not _guard_skips(str(ordinary))


def test_script_source_does_not_use_realpath_self_comparison():
    """Pin the fix at the source level.

    basename equality is what makes the guard checkout-independent; a realpath
    comparison against BASH_SOURCE reintroduces the defect while still looking
    like a self-exclusion guard.
    """
    src = open(SCRIPT, encoding="utf-8").read()
    assert 'realpath "${BASH_SOURCE[0]}"' not in src, (
        "self-exclusion reverted to realpath comparison -- protects only the "
        "executing copy, see this test's module docstring"
    )
    assert 'basename "${BASH_SOURCE[0]}"' in src


def test_committed_mapping_table_is_not_all_identity():
    """Detect the corrupted state directly.

    If every pair is 'x|x' the script is a silent no-op: it runs, finds nothing to
    replace, and exits 0 -- which reads exactly like a clean fleet.
    """
    src = open(SCRIPT, encoding="utf-8").read()
    pairs = []
    for line in src.splitlines():
        line = line.strip()
        if line.startswith("'") and "|" in line and line.endswith("'"):
            body = line.strip("'")
            if body.count("|") == 1:
                pairs.append(tuple(body.split("|")))
    assert pairs, "no mapping pairs found -- table shape changed, update this test"
    non_identity = [p for p in pairs if p[0] != p[1]]
    assert non_identity, (
        f"all {len(pairs)} mappings are identity no-ops (x|x) -- the script has "
        "rewritten its own table and can no longer detect any drift"
    )
