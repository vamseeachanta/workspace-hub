"""Inventory pytest-shaped files independently, then audit observed collection.

The invariant and filename universe come from issue #3790 and
docs/plans/2026-08-03-issue-3790-hidden-test-files.md, sections R-A and OQ1.
Pytest hook and option contracts:
https://docs.pytest.org/en/stable/reference/reference.html#collection-hooks
https://docs.pytest.org/en/stable/reference/reference.html#confval-python_files

This module performs no test imports. Loading it as a pytest plugin observes the
collection pytest would ordinarily perform; the inventory-only CLI is inert.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from fnmatch import fnmatch
from pathlib import Path


class InventoryError(ValueError):
    """An incomplete inventory cannot establish collection coverage."""


def inventory(root: Path, extra_patterns=()) -> list[str]:
    """List on-disk candidates, ignoring no test directory or Git ignore rule.

    Only Git metadata is pruned. Environments and generated outputs should live
    outside the audited root. Symlinks fail explicitly rather than hiding files
    or following a link into an unrelated checkout.
    """
    root = Path(root)
    if not root.is_dir():
        raise InventoryError("inventory root is not a directory")
    # Both conventions are specified in the issue plan's OQ1, independently of
    # the configured python_files patterns (which may themselves hide tests).
    patterns = {"test_*.py", "*_test.py", *extra_patterns}

    def unreadable(_error):
        raise InventoryError("unreadable directory; inventory incomplete")

    candidates = []
    for directory, dirs, files in os.walk(root, followlinks=False, onerror=unreadable):
        base = Path(directory)
        dirs[:] = sorted(name for name in dirs if name != ".git")
        for name in dirs:
            path = base / name
            if path.is_symlink():
                raise InventoryError(f"symlink-directory: {path.relative_to(root).as_posix()}")
        for name in files:
            path = base / name
            relative = path.relative_to(root).as_posix()
            if not any(fnmatch(name, p) or fnmatch(relative, p) for p in patterns):
                continue
            if path.is_symlink():
                raise InventoryError(f"symlink-file: {relative}")
            candidates.append(relative)
    return sorted(candidates)


def pytest_addoption(parser):
    group = parser.getgroup("collection audit")
    group.addoption(
        "--audit-test-collection", metavar="REPORT", default=None,
        help="Audit all pytest-shaped files below rootdir and write a JSON report.",
    )


def pytest_configure(config):
    if config.getoption("audit_test_collection"):
        config.pluginmanager.register(CollectionAudit(config), "observed-collection-audit")


class CollectionAudit:
    """Observe real hooks; configuration comments never establish a disposition."""

    def __init__(self, config):
        self.config = config
        self.root = config.rootpath.resolve()
        self.destination = Path(config.getoption("audit_test_collection"))
        self.candidates = []
        self.items = {}
        self.deselected = {}
        self.skipped = {}
        self.failed = set()
        self.errors = set()
        self.markers = {}
        self.finished = False
        self.report = None
        # Pytest's marker-expression grammar uses identifiers and boolean
        # operators. Inspect actual deselected items; never infer a skip from
        # source text. See the reference's --markexpr and pytest_deselected.
        self.selection_markers = set(re.findall(
            r"[A-Za-z_]\w*", config.getoption("markexpr"),
        )) - {"and", "or", "not", "True", "False"}

    def relative(self, path):
        path = Path(path)
        if not path.is_absolute():
            path = self.root / path
        try:
            return path.resolve().relative_to(self.root).as_posix()
        except ValueError:
            self.errors.add("outside-root-collection")
            return None

    def pytest_sessionstart(self, session):
        try:
            self.candidates = inventory(self.root, self.config.getini("python_files"))
        except InventoryError as error:
            import pytest

            self.errors.add(str(error))
            self.write_report()
            pytest.exit("collection audit: inventory incomplete", returncode=pytest.ExitCode.TESTS_FAILED)

    def check_markers(self, item, names):
        path = self.relative(item.path)
        if path is None:
            return
        for mark in item.iter_markers():
            if mark.name not in names:
                continue
            reason = mark.kwargs.get("reason")
            # pytest.mark.skip accepts its reason as a positional argument;
            # skipif's positional argument is a condition, never a reason.
            if reason is None and mark.name == "skip" and mark.args:
                reason = mark.args[0]
            if not isinstance(reason, str) or not reason.strip():
                self.errors.add(f"missing-marker-reason: {path}: {mark.name}")
                continue
            registered = {
                entry.split(":", 1)[0].split("(", 1)[0].strip()
                for entry in self.config.getini("markers")
            }
            if mark.name not in registered:
                self.errors.add(f"unregistered-exclusion-marker: {path}: {mark.name}")
            self.markers.setdefault(path, set()).add((mark.name, reason.strip()))

    def pytest_itemcollected(self, item):
        path = self.relative(item.path)
        if path is not None:
            self.items[path] = self.items.get(path, 0) + 1
        self.check_markers(item, {"skip", "skipif"})

    def pytest_deselected(self, items):
        for item in items:
            path = self.relative(item.path)
            if path is not None:
                self.deselected[path] = self.deselected.get(path, 0) + 1
            self.check_markers(item, self.selection_markers)

    def pytest_collectreport(self, report):
        # Collector node IDs begin with the file path, including for module
        # skips where no pytest item is ever created. Root collectors use "".
        path_text = report.nodeid.split("::", 1)[0]
        if report.failed:
            self.errors.add("collection-error")
            if path_text:
                path = self.relative(path_text)
                if path is not None:
                    self.failed.add(path)
        if report.skipped and path_text:
            path = self.relative(path_text)
            if path is None:
                return
            reason = report.longrepr[-1] if isinstance(report.longrepr, tuple) else ""
            reason = reason.removeprefix("Skipped: ").strip()
            if reason == "Skipped":
                reason = ""
            if not reason:
                self.errors.add(f"missing-module-skip-reason: {path}")
            self.skipped[path] = reason

    def pytest_collection_finish(self, session):
        # Imports and hooks may generate new test-shaped files. Retain the
        # initial inventory and add any new candidates before claiming coverage.
        try:
            self.candidates = sorted(set(self.candidates) | set(
                inventory(self.root, self.config.getini("python_files")),
            ))
        except InventoryError as error:
            self.errors.add(str(error))
        self.finished = True

    def write_report(self):
        files = []
        # Include custom collectors' observed files even when they do not match
        # the configured patterns. Never reduce the inventory to the observed set.
        for path in sorted(set(self.candidates) | self.items.keys() | self.skipped.keys() | self.failed):
            if path in self.failed:
                status = "collection_error"
            elif path in self.items:
                status = "collected"
            elif self.skipped.get(path):
                status = "skipped"
            else:
                status = "not_collected"
            row = {
                "path": path, "status": status,
                "item_count": self.items.get(path, 0),
                "deselected_count": self.deselected.get(path, 0),
                "markers": [
                    {"name": name, "reason": reason}
                    for name, reason in sorted(self.markers.get(path, set()))
                ],
            }
            if path in self.skipped:
                row["reason"] = self.skipped[path]
            files.append(row)
        errors = set(self.errors)
        if not self.finished:
            errors.add("collection-incomplete")
        if not self.candidates:
            errors.add("empty-inventory")
        unresolved = any(row["status"] in {"not_collected", "collection_error"} for row in files)
        self.report = {
            "status": "FAIL" if errors or unresolved else "PASS",
            "files": files, "errors": sorted(errors),
        }
        self.destination.write_text(json.dumps(self.report, indent=2) + "\n", encoding="utf-8")

    def pytest_sessionfinish(self, session, exitstatus):
        import pytest

        self.write_report()
        # Preserve collection failures, interruptions, usage errors and failures
        # from execution. Only change a successful exit to signal a failed audit.
        if self.report["status"] == "FAIL" and exitstatus == pytest.ExitCode.OK:
            session.exitstatus = pytest.ExitCode.TESTS_FAILED

    def pytest_terminal_summary(self, terminalreporter):
        if self.report is None:
            return
        terminalreporter.write_sep("-", f"collection audit: {self.report['status']}")
        for row in self.report["files"]:
            if row["status"] in {"not_collected", "collection_error"}:
                terminalreporter.write_line(f"{row['status']}: {row['path']}")
        for error in self.report["errors"]:
            terminalreporter.write_line(error)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", required=True, type=Path, metavar="ROOT")
    args = parser.parse_args()
    try:
        files = inventory(args.inventory)
    except InventoryError as error:
        parser.exit(1, f"inventory failed: {error}\n")
    # Inventory-only mode establishes names, never collection or execution.
    print(json.dumps({
        "status": "NOT_EVALUATED",
        "files": [{"path": path, "status": "NOT_EVALUATED"} for path in files],
    }, indent=2))


if __name__ == "__main__":
    main()
