"""The public field-development corpus is out of scope for the client-name scan.

WHY THIS CARVE-OUT EXISTS
-------------------------
`.legal-deny-list.yaml` blocks a set of Gulf of Mexico field and project names
because they were CLIENT ENGAGEMENT names under /mnt/ace. Those same strings are
also the PUBLIC names of the fields, and public field-development analysis is
work this ecosystem does deliberately — the hits live in a scan of public
SubseaIQ data and a GoM field-development dataset.

Exact-string matching cannot tell provenance apart: a field name taken from a
client folder is a leak; the same name in a scan of public data is the subject
matter. Scanning the public corpus therefore yields only false positives, and a
gate that is mostly noise stops being read.

Owner decision 2026-08-03: the world-energy field-development corpus is wholly
public, vendors are verified from public sources, and the scan does not apply
there.

WHY THE SECOND TEST MATTERS MORE
--------------------------------
Narrowing a legal gate is safe only if the narrowing is BOUNDED. The genuine
findings this scan exists for — the copyrighted-vendor and named-author entries
recorded under the #1773 incident — live in docs/plans, docs/session-handoffs
and scripts/, NOT in the field-development corpus. The carve-out must drop the
public-data false positives and leave those blocking.
`test_pattern_outside_the_carveout_still_blocks` is the guard against a future
"just add one more path" that quietly disables that protection.

NOTE ON THIS FILE'S OWN CONTENT
-------------------------------
Deny-listed strings are read from the deny list AT RUNTIME and never written
literally here. An earlier draft spelled them out and added 22 fresh violations
to the very scan it tests — the enforcement artifact tripping its own check.
Reading them at runtime also means this test follows deny-list edits instead of
drifting from them.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DENY_LIST = REPO_ROOT / ".legal-deny-list.yaml"
SCANNER = REPO_ROOT / "scripts" / "legal" / "legal-sanity-scan.sh"

# The corpus the owner ruled out of scope.
PUBLIC_FIELD_CORPUS = ["data/field-development", "docs/field-development"]

# Paths carrying the genuine #1773 findings — these must stay in scope.
MUST_STAY_IN_SCOPE = ["docs/plans", "docs/session-handoffs", "scripts"]


def _a_denied_pattern() -> str:
    """Any blocking pattern, read from the deny list rather than hardcoded.

    Which one does not matter: the behaviour under test is "excluded path is not
    reported, other path is", not the semantics of a particular name.
    """
    for line in DENY_LIST.read_text().splitlines():
        m = re.match(r'\s*-\s*pattern:\s*"([^"]+)"', line)
        if m:
            return m.group(1)
    pytest.fail("no pattern entries found in .legal-deny-list.yaml")


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """A throwaway workspace carrying the REAL deny list and scanner.

    The real deny list is the artifact under test — a fixture copy would test a
    fiction. The tree itself is fake, so no real repo is ever scanned.
    """
    ws = tmp_path / "workspace-hub"
    (ws / "scripts" / "legal").mkdir(parents=True)
    shutil.copy(SCANNER, ws / "scripts" / "legal" / "legal-sanity-scan.sh")
    shutil.copy(DENY_LIST, ws / ".legal-deny-list.yaml")
    subprocess.run(["git", "init", "-q"], cwd=ws, check=True)
    return ws


def _write(ws: Path, rel: str, text: str) -> None:
    p = ws / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def _scan(ws: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", "scripts/legal/legal-sanity-scan.sh"],
        cwd=ws, capture_output=True, text=True, timeout=180,
    )


@pytest.mark.parametrize("corpus", PUBLIC_FIELD_CORPUS)
def test_denied_pattern_inside_the_public_corpus_does_not_block(
    workspace: Path, corpus: str
) -> None:
    _write(workspace, f"{corpus}/public-scan.md", f"{_a_denied_pattern()}\n")
    result = _scan(workspace)
    combined = result.stdout + result.stderr
    assert "public-scan.md" not in combined, (
        f"{corpus} is public field data and must be out of scope, but the scan "
        f"reported it:\n{combined[-2000:]}"
    )
    assert result.returncode == 0, (
        f"a workspace whose only matches are inside the public corpus must "
        f"pass; rc={result.returncode}\n{combined[-2000:]}"
    )


def test_pattern_outside_the_carveout_still_blocks(workspace: Path) -> None:
    """The carve-out must not leak into paths that carry real findings (#1773)."""
    pattern = _a_denied_pattern()
    _write(workspace, "data/field-development/public-scan.md", f"{pattern}\n")
    _write(workspace, "docs/plans/some-plan.md", f"{pattern}\n")
    result = _scan(workspace)
    combined = result.stdout + result.stderr
    assert "some-plan.md" in combined, (
        f"a denied pattern outside the public corpus MUST still be reported:\n"
        f"{combined[-2000:]}"
    )
    assert result.returncode != 0, "a genuine hit must fail the scan"
    assert "public-scan.md" not in combined, (
        "the public corpus must stay out of scope even when the scan fails for "
        "an unrelated, genuine reason"
    )


@pytest.mark.parametrize("path", MUST_STAY_IN_SCOPE)
def test_exclusions_do_not_swallow_in_scope_paths(path: str) -> None:
    """Config-shape guard: no exclusion entry may cover a must-scan path.

    Cheap and independent of scanner behaviour — it catches an over-broad glob
    (e.g. `docs/`) at review time, before the protection is gone.
    """
    text = DENY_LIST.read_text()
    in_exclusions = text.split("exclusions:", 1)[1] if "exclusions:" in text else ""
    for line in in_exclusions.splitlines():
        entry = line.strip().lstrip("-").strip().strip('"').strip("'")
        if not entry or entry.startswith("#"):
            continue
        prefix = entry.rstrip("*/")
        assert not prefix or not path.startswith(prefix), (
            f"exclusion {entry!r} would remove {path!r} from the scan; that path "
            f"carries genuine vendor/author findings (#1773)"
        )


def test_this_guard_does_not_trip_the_scan_it_guards() -> None:
    """No deny-listed literal may appear in this file.

    An enforcement artifact that trips its own check adds noise to the signal it
    exists to protect. An earlier draft of this file did exactly that.
    """
    own_text = Path(__file__).read_text()
    patterns = re.findall(r'\s*-\s*pattern:\s*"([^"]+)"', DENY_LIST.read_text())
    assert patterns, "deny list yielded no patterns to check against"
    hits = [p for p in patterns if p in own_text]
    assert not hits, (
        f"this test file contains deny-listed literals {hits}; read them from "
        f"the deny list at runtime instead"
    )
