"""Regression guard for #2972 — the cron build path silently lost its yaml dep.

`build-equality-matrix.py` is invoked from weekly cron as a STANDALONE script
(`uv run --script ...`), not inside a project env, so its third-party deps MUST be
declared in a PEP-723 inline-metadata block. Without it the cron build dies with
ModuleNotFoundError while the exit-1 is buried in an unread dated log (the #2972 bug).

These checks are static + deterministic (no network/uv) so they guard the regression
in any CI without flaking on dependency resolution.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "readiness" / "build-equality-matrix.py"
WRAPPER = REPO / "scripts" / "readiness" / "equality-matrix-cron.sh"


def _pep723_deps(text: str) -> list[str]:
    block = re.search(r"^# /// script\s*$(.*?)^# ///\s*$", text, re.M | re.S)
    assert block, "no PEP-723 `# /// script` block in build-equality-matrix.py"
    dm = re.search(r"dependencies\s*=\s*\[(.*?)\]", block.group(1), re.S)
    assert dm, "no `dependencies` key in the PEP-723 block"
    return re.findall(r'"([^"]+)"', dm.group(1))


def test_script_declares_pyyaml():
    deps = _pep723_deps(SCRIPT.read_text())
    assert any(d.lower().startswith("pyyaml") for d in deps), f"pyyaml not declared: {deps}"


def test_docstring_runline_uses_uv_script():
    # the in-file run instruction must match the cron path that resolves PEP-723 deps
    assert "uv run --script" in SCRIPT.read_text(), "run-line must use `uv run --script`"


def test_cron_wrapper_fails_loud():
    t = WRAPPER.read_text()
    assert "notify.sh" in t, "wrapper must emit a JSONL notification on failure"
    assert "exit 1" in t, "wrapper must exit non-zero on failure"
