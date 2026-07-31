#!/usr/bin/env python3
"""`needs:cross-review` marks a PHASE requirement — it must not reassign the provider.

## What happened

`routing-rules.yaml` carried a rule matching `gh_label: needs:cross-review` →
`assign: {provider: codex}`. **The label did not exist in any repo**, so the rule
had never fired. A dead rule with a live effect waiting behind it.

Because the label had no way to be applied, "both providers should touch this"
had no expressible form — and users said it the only way left, with **two `lane:`
labels on one issue**. 21 open issues across three repos carried
`lane:claude + lane:codex`, and `existing_label_value()` (route.py:68) returns
the FIRST match, so which provider won depended on GitHub's API ordering.

Timeline evidence: on every sampled issue both labels were applied **in the same
minute by the same person** — one deliberate act meaning "both", not an
afterthought.

## Why the rule had to change before the label could be used

Creating the label ACTIVATES the rule, and rule beats `lane:` in route.py's
precedence (`ai:` > rule > `lane:`). So migrating those 21 issues to
`lane:claude + needs:cross-review` would have silently rerouted all 21 to codex —
overriding a human's explicit lane choice with a rule they never saw.

The two ideas were conflated:

    "this issue IS a cross-review task"       → an ASSIGNMENT (who does it)
    "this work NEEDS a second-provider review" → a PHASE (what must happen
                                                  before it can close)

`needs:` is the vocabulary of a requirement, not a routing target. The repo's own
policy agrees — cross-review is Claude + Codex + Agy with *Claude orchestrating*,
i.e. a review is something added to work, not a reassignment of it.

Hermetic: parses the shipped YAML. No gh, no network.

Run: uv run --with pyyaml pytest tests/dispatch/test_cross_review_is_a_phase.py
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
RULES_PATH = REPO_ROOT / ".claude" / "memory" / "kanban" / "routing-rules.yaml"

PHASE_LABELS = {"needs:cross-review"}


@pytest.fixture(scope="module")
def rules() -> dict:
    return yaml.safe_load(RULES_PATH.read_text(encoding="utf-8"))


def test_no_rule_assigns_a_provider_from_a_phase_label(rules):
    """The regression this file exists for.

    A `needs:` label describes a requirement on the work. Letting it pick the
    worker means a human's `lane:` choice is silently overridden by a rule that
    is invisible at the point of labelling.
    """
    offenders = []
    for rule in rules.get("rules") or []:
        label = (rule.get("match") or {}).get("gh_label")
        if label in PHASE_LABELS and (rule.get("assign") or {}).get("provider"):
            offenders.append(f"{label} -> provider {(rule['assign'])['provider']}")
    assert not offenders, (
        "phase labels must not reassign the provider: " + "; ".join(offenders)
    )


def test_no_rule_assigns_a_machine_from_a_phase_label(rules):
    """Same argument, other axis — a review requirement is not a host choice."""
    offenders = []
    for rule in rules.get("rules") or []:
        label = (rule.get("match") or {}).get("gh_label")
        if label in PHASE_LABELS and (rule.get("assign") or {}).get("machine"):
            offenders.append(label)
    assert not offenders, f"phase labels must not assign a machine: {offenders}"


def test_a_needs_prefixed_label_is_never_a_routing_target(rules):
    """Generalised: the whole `needs:` namespace is requirements, not routing.

    Stated as a namespace rule rather than a list of one, so the next `needs:*`
    label added does not have to rediscover this. Naming a class is what keeps a
    fix from being a one-off patch.
    """
    offenders = []
    for rule in rules.get("rules") or []:
        label = (rule.get("match") or {}).get("gh_label") or ""
        if label.startswith("needs:") and (rule.get("assign") or {}):
            assign = rule["assign"]
            if assign.get("provider") or assign.get("machine"):
                offenders.append(f"{label} -> {assign}")
    assert not offenders, (
        "`needs:` labels state a requirement and must not route: " + "; ".join(offenders)
    )


def test_the_check_is_not_vacuous(rules):
    """If `rules:` were renamed or emptied, every assertion above would pass.

    Absence of findings must not be reachable through absence of input — the
    failure mode this whole session keeps meeting.
    """
    rs = rules.get("rules")
    assert isinstance(rs, list) and rs, "no rules parsed"
    assert any((r.get("match") or {}).get("gh_label") for r in rs), (
        "no gh_label rule present — the checks above would inspect nothing"
    )
