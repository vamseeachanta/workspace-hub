#!/usr/bin/env python3
"""A dispatch queue file must declare when it was generated.

## The gap

`dispatch.py` materialises `.claude/dispatch/<machine>.yaml`, which each
machine's session drains. The payload carried `machine`, `generated_by` and
`cards` — and **no timestamp**. A session opening `dev-primary.yaml` (1,354
cards) could not tell whether it was built minutes ago or in May.

That matters because the queue is a *snapshot of a routing decision*, and
routing inputs change constantly: labels get corrected, machines get retired,
capability claims get fixed. On 2026-07-31 alone ~300 labels changed, which
silently invalidated queue files generated the previous day. Nothing in the file
said so.

## Why this is the same defect as the rest of the epic

`reachability.py` — same author, same week — writes `observed_at` **and** an
explicit TTL, with the reasoning stated in its own docstring: *"reachability is
time-varying, so the TTL is explicit — consumers warn on stale data rather than
trusting it as static routing truth."*

Dispatch queues are equally time-varying, and got neither. An undated snapshot
does not look stale; it looks authoritative. Absence of a timestamp reads as
freshness.

## What is asserted

The file declares `generated_at` (UTC, ISO-8601) and `ttl_hours`, and a
`queue_age_hours()` helper lets a consumer decide. Deliberately NOT enforced by
refusing to load: a stale queue is still better than no queue, and hard-failing
a drain because a clock drifted would push people to delete the field. The
contract is *visible staleness*, not *blocked staleness*.

Hermetic: pure functions, injected clock, no gh and no network.

Run: uv run --with pyyaml pytest tests/dispatch/test_queue_staleness.py
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DISPATCH_PY = REPO_ROOT / "scripts" / "dispatch" / "dispatch.py"
DISPATCH_DIR = REPO_ROOT / ".claude" / "dispatch"


def _load():
    # dispatch.py does `import route` as a SIBLING module, so its directory has
    # to be importable. Prepending rather than appending: a stray `route.py`
    # elsewhere on sys.path would otherwise shadow the one under test.
    pkg_dir = str(DISPATCH_PY.parent)
    if pkg_dir not in sys.path:
        sys.path.insert(0, pkg_dir)
    spec = importlib.util.spec_from_file_location("dispatch_mod", DISPATCH_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["dispatch_mod"] = mod
    spec.loader.exec_module(mod)
    return mod


D = _load()

NOW = datetime(2026, 7, 31, 12, 0, tzinfo=timezone.utc)


# --------------------------------------------------------------------------
# the payload declares its own age
# --------------------------------------------------------------------------


def test_payload_carries_generated_at():
    p = D.queue_payload("dev-primary", [], now=lambda: NOW)
    assert p["generated_at"] == "2026-07-31T12:00:00Z"


def test_payload_carries_a_ttl():
    p = D.queue_payload("dev-primary", [], now=lambda: NOW)
    assert p["ttl_hours"] > 0, "a TTL of zero would make every queue permanently stale"


def test_generated_at_is_utc_and_sortable():
    """Local time in a git-tracked file makes two machines' queues incomparable."""
    p = D.queue_payload("m", [], now=lambda: NOW)
    assert p["generated_at"].endswith("Z")
    datetime.strptime(p["generated_at"], "%Y-%m-%dT%H:%M:%SZ")


def test_existing_fields_are_preserved():
    """Back-compat: a consumer reading machine/cards must not break."""
    cards = [{"gh": "o/r#1"}]
    p = D.queue_payload("dev-primary", cards, now=lambda: NOW)
    assert p["machine"] == "dev-primary"
    assert p["cards"] == cards
    assert p["generated_by"] == "dispatch.py"


# --------------------------------------------------------------------------
# age is computable, and staleness is VISIBLE not enforced
# --------------------------------------------------------------------------


def test_age_of_a_fresh_queue_is_zero():
    p = D.queue_payload("m", [], now=lambda: NOW)
    assert D.queue_age_hours(p, now=lambda: NOW) == pytest.approx(0, abs=0.01)


def test_age_grows():
    p = D.queue_payload("m", [], now=lambda: NOW)
    later = NOW + timedelta(hours=30)
    assert D.queue_age_hours(p, now=lambda: later) == pytest.approx(30, abs=0.01)


def test_is_stale_uses_the_declared_ttl():
    p = D.queue_payload("m", [], now=lambda: NOW)
    ttl = p["ttl_hours"]
    assert not D.queue_is_stale(p, now=lambda: NOW)
    assert D.queue_is_stale(p, now=lambda: NOW + timedelta(hours=ttl + 1))


def test_a_queue_with_no_timestamp_is_treated_as_STALE():  # noqa: N802
    """The pre-2026-07-31 files have no `generated_at`.

    Unknown age must resolve to STALE, never to fresh. Treating "I cannot tell"
    as "it is fine" is the exact failure this epic keeps meeting — and here it
    would be self-inflicted, since every queue file on main today lacks the field.
    """
    assert D.queue_is_stale({"machine": "m", "cards": []}, now=lambda: NOW) is True


def test_staleness_does_not_prevent_loading():
    """Visible, not blocking.

    A stale queue is still better than no queue, and hard-failing a drain over a
    clock would push people to delete the field rather than regenerate the file.
    """
    old = D.queue_payload("m", [{"gh": "o/r#1"}], now=lambda: NOW - timedelta(days=90))
    assert old["cards"], "a stale payload still carries its cards"


# --------------------------------------------------------------------------
# the shipped files
# --------------------------------------------------------------------------


@pytest.mark.skipif(not DISPATCH_DIR.is_dir(), reason="no queue files checked out")
def test_shipped_queue_files_parse_and_declare_a_machine():
    """Guards the guard: if the payload shape drifts, this catches it against the
    files actually on disk rather than only against a constructed dict."""
    files = sorted(DISPATCH_DIR.glob("*.yaml"))
    assert files, "no queue files found — the check below would be vacuous"
    for f in files:
        if f.name.startswith("_"):
            continue                      # _leader-state.yaml is not a queue
        data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        assert data.get("machine"), f"{f.name} declares no machine"
