"""
Subdirectory-scoped conftest for scripts/data/llm-wiki/tests/markdown_qa/.

This conftest applies ONLY to tests under markdown_qa/.  Sibling tests under
scripts/data/llm-wiki/tests/ (e.g. test_resolve_wiki_path.py) are NOT affected
by the socket disable or the session-finish hook.

v6 NOTE: markdown_qa/ does NOT have __init__.py.  pytest's rootdir-walk
discovers this conftest and adds markdown_qa/ to sys.path during collection,
so the bare sibling imports below resolve to files in this same directory.
This is the same mechanism test_resolve_wiki_path.py uses (manual sys.path
insert at lines 22-26) to escape the hyphenated llm-wiki/ ancestor.
"""

import os
import sys
import json
from pathlib import Path

import pytest

# Ensure this directory is on sys.path so sibling bare imports work even when
# pytest is invoked with an explicit path and rootdir-walk hasn't fired yet.
_THIS_DIR = Path(__file__).parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from fixtures_sampling import (  # noqa: E402
    check_floor_occupancy,
    write_report,
    write_per_topic_artifact,  # re-exported for the test module
)

# v5: env-seam spelled into source; v6: unchanged.
ARTIFACTS_DIR = Path(os.environ.get(
    "MARKDOWN_QA_ARTIFACTS_DIR",
    str(Path(__file__).parent / ".artifacts" / "per-topic"),
))

# v6: sentinel path proves pytest_sessionfinish actually fires (test #15).
SENTINEL_PATH = Path(os.environ.get(
    "MARKDOWN_QA_SESSIONFINISH_SENTINEL",
    str(ARTIFACTS_DIR.parent / ".sessionfinish-fired"),
))


def pytest_sessionfinish(session, exitstatus):
    # Write sentinel UNCONDITIONALLY at hook entry so test #15 can prove the hook
    # registered and ran even on narrow -k runs that collect zero per-topic tests.
    SENTINEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    SENTINEL_PATH.write_text("fired")

    # Guard: only process when per-topic artifacts exist.
    if not ARTIFACTS_DIR.exists():
        return
    per_topic = [json.loads(p.read_text()) for p in ARTIFACTS_DIR.glob("*.json")]
    if not per_topic:
        return

    violations = check_floor_occupancy(per_topic)
    write_report("conversion-quality-report.json", per_topic, violations)
    if violations:
        session.exitstatus = 1
        print("FLOOR-OCCUPANCY VIOLATIONS:", violations, file=sys.stderr)


@pytest.fixture(scope="session", autouse=True)
def _disable_network():
    # Activation only; active probe lives in test_no_network_access (test #13).
    # Scoped to markdown_qa/ via subdirectory conftest — sibling tests unaffected.
    from pytest_socket import disable_socket
    disable_socket(allow_unix_socket=False)
    yield
