"""Repository-root pytest hooks: the tracked test quarantine.

``tests/quarantine.txt`` lists tests that already fail on ``main``. Each one is
marked ``xfail(strict=False)``: it still runs and is reported as XFAIL (or
XPASS once fixed), but it cannot turn a run red. One entry per line::

    <node id>  # <reason> (#<tracking issue>)

A node id without a ``[parameter]`` suffix covers every parametrization; a bare
file path covers every test in that file. Remove an entry when its test is fixed;
the tracking issue lists every entry. A listed *file* that fails to import is
reported as skipped rather than as a collection error; a module that needs an
optional package should still skip itself with ``pytest.importorskip``.
"""
from __future__ import annotations

from pathlib import Path

import pytest

QUARANTINE_FILE = Path(__file__).resolve().parent / "tests" / "quarantine.txt"


def load_quarantine(path: Path = QUARANTINE_FILE) -> dict[str, str]:
    """Return ``{node id: reason}`` from the quarantine file (empty if absent)."""
    entries: dict[str, str] = {}
    if not path.is_file():
        return entries
    for raw in path.read_text(encoding="utf-8").splitlines():
        node, _, reason = raw.partition("#")
        node = node.strip()
        if node:
            entries[node] = reason.strip() or "quarantined: fails on main"
    return entries


def quarantine_reason(nodeid: str, entries: dict[str, str]) -> str | None:
    """Match an exact id, a parametrization of a listed id, or a listed file."""
    if nodeid in entries:
        return entries[nodeid]
    base = nodeid.split("[", 1)[0]
    if base in entries:
        return entries[base]
    path = nodeid.split("::", 1)[0]
    return entries.get(path)


def _repo_nodeid(config, path, nodeid: str) -> str:
    """Node id relative to the repository root, whatever directory pytest ran in."""
    try:
        rel = Path(str(path)).resolve().relative_to(Path(str(config.rootpath)).resolve()).as_posix()
    except ValueError:
        return nodeid
    return rel + nodeid[nodeid.index("::"):] if "::" in nodeid else rel


@pytest.hookimpl(hookwrapper=True)
def pytest_make_collect_report(collector):
    """A quarantined *file* that fails to import is reported as skipped, not as an error."""
    outcome = yield
    report = outcome.get_result()
    if not report.failed or not isinstance(collector, pytest.Module):
        return
    entries = load_quarantine()
    path = _repo_nodeid(collector.config, collector.path, collector.nodeid)
    reason = entries.get(path)
    if reason:
        report.outcome = "skipped"
        report.longrepr = (str(collector.path), 0, f"Skipped: quarantine (collection): {reason}")


def pytest_collection_modifyitems(config, items):
    entries = load_quarantine()
    if not entries:
        return
    for item in items:
        reason = quarantine_reason(_repo_nodeid(config, item.path, item.nodeid), entries)
        if reason:
            item.add_marker(pytest.mark.xfail(reason=f"quarantine: {reason}", strict=False))
