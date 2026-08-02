#!/usr/bin/env python3
"""A tracked queue file must not carry raw GitHub issue titles.

## The gap

`dispatch.py` materialises `.claude/dispatch/<machine>.yaml` and **commits it**.
`workspace-hub` is a PUBLIC repo. The card carried `title` verbatim from the
routed issue, and the routed set spans workspace-hub, digitalmodel and deckhand
— repos whose issue titles include client identifiers.

CI's Client-PII Gate blocks on exactly this (PR #3765): ten-plus hits in
`dev-primary.yaml`, two in `multi.yaml`. The values are withheld from the log by
design, which is itself the point — the leak is real but unquotable, so the fix
cannot be "redact the ones we can see". The generator must stop emitting the
field at all.

`scripts/legal/legal-sanity-scan.sh` passing locally proves nothing here: it
runs without the private redaction map, which is a CI secret. A local pass is
the absence of a signal, not a clean result.

## What must NOT change

`route.py` keeps fetching titles. They feed `--detail` console output and
`--json`, which are ephemeral and local — never tracked. #3763/#3767 had just
repaired that fetch after every card shipped with an empty title; narrowing the
fetch to "fix" the leak would re-break it. The boundary is **serialisation**,
not retrieval.

## Why the field is OMITTED, not blanked

#3763's failure mode was 1341/1341 cards with `title: ""`. If redaction shipped
as a blank or a placeholder string, a redacted queue and a broken pipeline would
be byte-identical on disk. So the card carries no title-shaped field at all, and
the payload declares the omission once (`title_policy`) so a reader can tell
"deliberately absent" from "generator dropped it".

The card stays identifiable without it: `gh`, `repo`, `url`, `domain`,
`provider`, `dispatch_status`, `wip_eligible`, `routed_by`. A draining session
fetches the title from GitHub at drain time, where it is ephemeral.

## What is asserted

The PROPERTY — no substring of a routed title survives into the serialised
YAML — not merely that a key named `title` is gone. A rename to `summary`, a
nested `meta:` blob, or a truncated prefix would all pass a key-absence check
and still leak.

Hermetic: injected proposals, injected clock, no gh and no network.

Run: uv run --with pyyaml pytest tests/dispatch/test_queue_omits_issue_titles.py
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DISPATCH_PY = REPO_ROOT / "scripts" / "dispatch" / "dispatch.py"
ROUTE_PY = REPO_ROOT / "scripts" / "dispatch" / "route.py"


def _load():
    # dispatch.py does `import route` as a SIBLING module, so its directory has
    # to be importable. Prepending rather than appending: a stray `route.py`
    # elsewhere on sys.path would otherwise shadow the one under test.
    pkg_dir = str(DISPATCH_PY.parent)
    if pkg_dir not in sys.path:
        sys.path.insert(0, pkg_dir)
    spec = importlib.util.spec_from_file_location("dispatch_notitle", DISPATCH_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["dispatch_notitle"] = mod
    spec.loader.exec_module(mod)
    return mod


D = _load()

NOW = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)

# Long enough that a 12-character window is unambiguous, and shaped like a real
# issue title so a truncating leak (`title[:60]`, `title[:20]`) still trips the
# window scan below. Deliberately synthetic — no real identifier goes in a test.
SENTINEL_TITLE = "Refit programme for ZZQX-9 marine terminal berth 4"
WINDOW = 12


def _windows(text: str, size: int = WINDOW) -> list[str]:
    """Every contiguous slice of `text`, so a partial leak is caught too."""
    return [text[i:i + size] for i in range(len(text) - size + 1)]


def _proposal(**kw):
    base = {
        "key": "gh:owner/name#4242",
        "repo": "owner/name",
        "domain": "subsea",
        "provider": "codex",
        "title": SENTINEL_TITLE,
        "url": "https://github.com/owner/name/issues/4242",
        "machine": "dev-primary",
        "slot": "active-eligible",
        "routed_by": "rule",
    }
    base.update(kw)
    return base


def _dump(payload) -> str:
    """Serialise exactly as `cmd_build` does, so the assertion covers the bytes
    that actually reach the tracked file rather than an in-memory dict."""
    return yaml.safe_dump(payload, sort_keys=False, width=100)


def _values(obj):
    """Every scalar in a nested structure — keys are ignored on purpose.

    A leak that renames the field, nests it, or stuffs it into a list is still a
    leak. Only the VALUES matter.
    """
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _values(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _values(v)
    else:
        yield obj


# --------------------------------------------------------------------------
# the property: no routed title reaches the tracked bytes
# --------------------------------------------------------------------------


def test_no_fragment_of_a_routed_title_reaches_the_serialised_queue():
    """The whole property, on the serialised form.

    Not `"title" not in card`: a rename to `summary`, a nested `meta:` blob, or
    a truncated prefix would all satisfy a key-absence check and still publish
    the identifier to a public repo.
    """
    payload = D.queue_payload(
        "dev-primary", D.build_queues([_proposal()])["dev-primary"], now=lambda: NOW)
    text = _dump(payload)
    leaked = [w for w in _windows(SENTINEL_TITLE) if w in text]
    assert not leaked, (
        f"routed issue title reached the tracked YAML via {leaked[:3]!r}\n{text}")


def test_no_card_value_equals_the_title_under_any_key():
    """Same property at the object level, so the failure names the offending value."""
    cards = D.build_queues([_proposal()])["dev-primary"]
    for v in _values(cards):
        assert not (isinstance(v, str) and SENTINEL_TITLE[:WINDOW] in v), (
            f"a card value carries the routed title: {v!r}")


@pytest.mark.parametrize("title", [
    SENTINEL_TITLE,
    "x" * 300,                                   # longer than route.py's [:60]
    "Ünïcøde tïtle wíth ZZQX-9 accénts",         # non-ASCII must not slip through
    "title: with: colons: and #hash",            # YAML-punctuating title
])
def test_the_property_holds_for_any_title_shape(title):
    cards = D.build_queues([_proposal(title=title)])["dev-primary"]
    text = _dump(D.queue_payload("dev-primary", cards, now=lambda: NOW))
    assert not any(w in text for w in _windows(title)), (
        f"title shape {title[:30]!r} leaked into the queue file")


def test_the_whole_write_path_is_clean(tmp_path, monkeypatch):
    """End-to-end through `cmd_build(write=True)` onto disk.

    The unit assertions above cover the two functions; this covers the command
    that actually produces the tracked file, so a leak reintroduced between them
    (a post-processing step, a second serialiser) is still caught.
    """
    out = tmp_path / "dispatch"
    monkeypatch.setattr(D, "ROOT", tmp_path)
    monkeypatch.setattr(D, "DISPATCH_DIR", out)
    monkeypatch.setattr(D.route, "propose", lambda args: [_proposal()])

    D.cmd_build(write=True)

    written = out / "dev-primary.yaml"
    assert written.is_file(), "cmd_build wrote no queue file"
    text = written.read_text(encoding="utf-8")
    assert not any(w in text for w in _windows(SENTINEL_TITLE)), (
        f"routed title reached the file on disk:\n{text}")


# --------------------------------------------------------------------------
# absence must be DELIBERATE, not indistinguishable from breakage
# --------------------------------------------------------------------------


def test_no_card_carries_a_title_shaped_field():
    """A blank or placeholder title is the shape a *failed* fetch produces.

    #3763 shipped 1341/1341 cards with `title: ""`. Emitting `""` or a
    `"<redacted>"` stand-in would make an intentionally-redacted queue
    indistinguishable from that outage, so the field is gone entirely.
    """
    cards = D.build_queues([_proposal()])["dev-primary"]
    for card in cards:
        offenders = [k for k in card if "title" in k.lower() or "summary" in k.lower()]
        assert not offenders, f"card still carries a title-shaped field: {offenders}"


def test_the_payload_declares_that_titles_are_omitted():
    """The counterpart to the test above.

    With no per-card field, a reader cannot otherwise tell "redacted by policy"
    from "the generator forgot" — which is precisely the ambiguity #3763 turned
    into a silent 1341-card outage. One payload-level declaration resolves it
    without repeating a placeholder 1341 times in a tracked file.
    """
    payload = D.queue_payload("dev-primary", [], now=lambda: NOW)
    policy = payload.get("title_policy")
    assert policy, "the queue payload does not declare its title policy"
    assert "omit" in str(policy).lower(), (
        f"title_policy must state that titles are omitted, got {policy!r}")


# --------------------------------------------------------------------------
# the card stays identifiable, and route.py keeps fetching
# --------------------------------------------------------------------------


def test_the_card_is_still_identifiable_without_a_title():
    """Dropping the title must not cost the fields a drain actually routes on."""
    card = D.build_queues([_proposal()])["dev-primary"][0]
    assert card["gh"] == "owner/name#4242"
    assert card["repo"] == "owner/name"
    assert card["url"] == "https://github.com/owner/name/issues/4242"
    assert card["domain"] == "subsea"
    assert card["provider"] == "codex"
    assert card["dispatch_status"] == "ready"
    assert card["wip_eligible"] is True
    assert card["routed_by"] == "rule"


def test_build_queues_does_not_mutate_the_proposal():
    """`--detail` and `--json` read the same proposal objects.

    Redacting by `del p["title"]` in place would strip the console output too —
    a silent re-break of #3763 that no queue-file assertion would catch.
    """
    p = _proposal()
    D.build_queues([p])
    assert p["title"] == SENTINEL_TITLE, (
        "build_queues mutated its input; the ephemeral surfaces lose their titles")


def test_route_still_carries_the_title_into_its_proposals():
    """The fix belongs at serialisation, not retrieval.

    Guards against a future "simplification" that removes the title from
    `route.py` because nothing tracked consumes it — which would re-break the
    `--detail`/`--json` surfaces #3767 had just repaired.
    """
    spec = importlib.util.spec_from_file_location("route_notitle", ROUTE_PY)
    R = importlib.util.module_from_spec(spec)
    sys.modules["route_notitle"] = R
    spec.loader.exec_module(R)
    card = R.issue_to_card({"number": 1, "state": "OPEN", "title": SENTINEL_TITLE,
                            "labels": [{"name": "domain:subsea"}]}, "owner/name")
    assert card["title"] == SENTINEL_TITLE, (
        "route.py stopped carrying titles; --detail and --json go blank again")
