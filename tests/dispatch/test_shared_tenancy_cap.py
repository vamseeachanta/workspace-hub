#!/usr/bin/env python3
"""A shared host's concurrency cap is a courtesy constraint, not a tuning knob.

`licensed-win-1` is multi-tenant: interactive sessions belonging to OTHER PEOPLE
run on it at the same time as anything we dispatch. Saturating it degrades their
work, and they have no visibility into why it got slow.

Until now that fact lived only in the operator's head. The routing config said
`capacity: heavy` — which is an honest description of the hardware and, read on
its own, invites precisely the wrong conclusion: a large mostly-idle box sitting
behind a cap of 2 looks like a bottleneck somebody forgot to remove.

**Capacity and permission-to-use-capacity are different facts.** The config
carried the first and not the second, so the second could be optimised away by
someone acting entirely reasonably on what the file told them.

These tests make the second fact enforceable. A comment explains; a test refuses.

Hermetic: reads the committed YAML. No network, no gh, no git.

Run: uv run --with pyyaml pytest tests/dispatch/test_shared_tenancy_cap.py
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
RULES = REPO_ROOT / ".claude" / "memory" / "kanban" / "routing-rules.yaml"

#: The ceiling a multi-tenant host may not exceed without an explicit owner
#: decision. Deliberately a constant here rather than a value read back out of
#: the config: a limit that reads its own bound from the thing it is bounding
#: cannot fail.
SHARED_TENANCY_MAX_WIP = 2


@pytest.fixture(scope="module")
def rules() -> dict:
    return yaml.safe_load(RULES.read_text(encoding="utf-8"))


def shared_hosts(rules: dict) -> dict:
    return {name: m for name, m in (rules.get("machines") or {}).items()
            if isinstance(m, dict) and m.get("shared_tenancy")}


def test_at_least_one_host_is_declared_shared(rules):
    """Guard against the flag being dropped and this file passing vacuously.

    Every assertion below iterates the shared hosts. With the set empty they all
    pass and the suite reports green while enforcing nothing — the exact
    absence-of-signal failure this epic keeps meeting.
    """
    assert shared_hosts(rules), (
        "no machine declares shared_tenancy — either the flag was removed or "
        "this whole file is now a no-op that still reports green")


def test_a_shared_host_is_capped(rules):
    """The cap must EXIST. Falling through to the default is not the same thing.

    `wip_caps.per_machine.default` is 1, so an unlisted shared host would happen
    to be capped correctly today — and would silently stop being capped the day
    the default changed, for reasons having nothing to do with this host.
    """
    caps = (rules.get("wip_caps") or {}).get("per_machine") or {}
    for name in shared_hosts(rules):
        assert name in caps, (
            f"{name} is multi-tenant but has no explicit wip cap; it must not "
            f"depend on the global default staying low for unrelated reasons")


def test_a_shared_host_cap_is_not_raised(rules):
    """The actual guard. Raising the cap now fails here, with the reason attached.

    Not a performance regression test — the failure mode is other people's
    interactive sessions degrading on a box they share with us, which no metric
    of ours would ever show.
    """
    caps = (rules.get("wip_caps") or {}).get("per_machine") or {}
    for name in shared_hosts(rules):
        assert caps[name] <= SHARED_TENANCY_MAX_WIP, (
            f"{name} caps at {caps[name]}, above the shared-tenancy ceiling of "
            f"{SHARED_TENANCY_MAX_WIP}. This host runs other people's sessions. "
            f"Raising it is an owner decision, not a tuning change.")


def test_capacity_alone_does_not_imply_it_is_ours_to_use(rules):
    """`capacity: heavy` and `shared_tenancy: true` must be able to coexist.

    Pins the distinction the config previously could not express. If a future
    edit "resolves the contradiction" by downgrading capacity to something small,
    the licence/capacity routing regresses to the failure this fixed in #3718 —
    batch work sent to a host that cannot carry it. The two fields answer
    different questions and both answers are true.
    """
    shared = shared_hosts(rules)
    assert any(m.get("capacity") == "heavy" for m in shared.values()), (
        "no shared host is still declared heavy — if capacity was lowered to "
        "express the sharing constraint, that is the wrong lever: it re-breaks "
        "capability routing to encode a courtesy limit that wip_caps already "
        "carries")


def test_the_constraint_is_not_only_a_comment(rules):
    """Prose in the YAML is not machine-readable; a stripped comment is silent.

    The flag is what this suite reads. If someone deletes it and leaves the
    explanatory comment behind, the file still LOOKS governed while nothing
    enforces it — so the emptiness check above is the real backstop and this
    records why it exists.
    """
    assert "shared_tenancy" in RULES.read_text(encoding="utf-8")
