#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Provider-routing resolver (#2970 / F3).

A SINGLE machine-readable provider-routing policy so every machine/agent routes
AI providers identically. Pure resolver + thin CLI.

Resolution contract (this ORDER is the contract — get it exactly right):

  1. SEED   start from policy['roles'][task_type] (ordered provider list).
            Unknown task_type -> ValueError (fail closed).
  2. PRUNE  apply HARD constraints from policy['machine_overrides'][machine]
            given `attrs`. A provider whose disallow condition matches the attrs
            is REMOVED from the candidate list.
  3. RANK   if a scorecard with 'recommended_provider_order' is provided,
            reorder the SURVIVORS to follow that order. Providers not in the
            scorecard keep their relative policy order, appended after. The
            scorecard can ONLY reorder among survivors — it can NEVER re-add a
            provider pruned in step 2.

Policy file:    config/ai-tools/provider-routing-policy.yaml
Scorecard file: config/ai-tools/provider-routing-scorecard.json (optional)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY_PATH = REPO_ROOT / "config" / "ai-tools" / "provider-routing-policy.yaml"
DEFAULT_SCORECARD_PATH = REPO_ROOT / "config" / "ai-tools" / "provider-routing-scorecard.json"


def load_policy(path: Path | str = DEFAULT_POLICY_PATH) -> dict:
    """Load the routing policy YAML."""
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"policy file {path} did not parse to a mapping")
    return data


def load_scorecard(path: Path | str = DEFAULT_SCORECARD_PATH) -> dict | None:
    """Load the load-balancing scorecard JSON, or None if absent."""
    p = Path(path)
    if not p.exists():
        return None
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _constraint_matches(disallow_attrs: Any, attrs: dict) -> bool:
    """A hard constraint fires (prunes the provider) when its disallow condition
    matches the call attrs.

    disallow_attrs is a list of "key=value" strings. The constraint fires IFF
    EVERY key=value is present-and-equal in attrs (logical AND). An empty or
    absent list = UNCONDITIONAL disallow (always fires).
    """
    if not disallow_attrs:
        return True  # unconditional disallow
    if not isinstance(disallow_attrs, (list, tuple)):
        raise ValueError(
            f"disallow_attrs must be a list of 'key=value' strings, got {disallow_attrs!r}"
        )
    for clause in disallow_attrs:
        if "=" not in clause:
            raise ValueError(f"malformed disallow_attrs clause (need key=value): {clause!r}")
        key, _, want = clause.partition("=")
        key, want = key.strip(), want.strip()
        if key not in attrs:
            return False
        # Compare as strings so 'authoring_weight=heavy' matches attrs={'authoring_weight':'heavy'}
        # and bool-ish 'needs_large_context=true' matches True/'true'.
        if str(attrs[key]).strip().lower() != want.lower():
            return False
    return True


def route(
    task_type: str,
    machine: str,
    attrs: dict | None = None,
    policy: dict | None = None,
    scorecard: dict | None = None,
) -> list[str]:
    """Resolve the ordered provider list for a task on a machine.

    See module docstring for the SEED -> PRUNE -> RANK contract.

    Args:
        task_type: a key in policy['roles'] (e.g. 'review', 'implement').
        machine:   machine id; looked up in policy['machine_overrides'].
        attrs:     typed task attributes (e.g. {'authoring_weight': 'heavy'}).
        policy:    parsed policy dict; loaded from the default path if None.
        scorecard: parsed scorecard dict (with 'recommended_provider_order');
                   load-balancing reorders survivors only. If None, no rerank.

    Returns:
        Ordered list of provider names. May be empty if every candidate was
        pruned by a hard constraint.

    Raises:
        ValueError: unknown task_type (fail closed), or malformed policy.
    """
    attrs = attrs or {}
    if policy is None:
        policy = load_policy()

    roles = policy.get("roles") or {}
    if task_type not in roles:
        known = ", ".join(sorted(roles)) or "(none)"
        raise ValueError(
            f"unknown task_type {task_type!r}; known task types: {known}"
        )

    # 1. SEED
    candidates: list[str] = list(roles[task_type])

    # 2. PRUNE — hard machine constraints matched against attrs
    overrides = (policy.get("machine_overrides") or {}).get(machine) or {}
    pruned: list[str] = []
    for provider in candidates:
        constraint = overrides.get(provider)
        if constraint is not None and _constraint_matches(
            constraint.get("disallow_attrs"), attrs
        ):
            continue  # hard-pruned
        pruned.append(provider)

    # 3. RANK — scorecard reorders survivors only; never re-adds a pruned provider
    if scorecard:
        order = scorecard.get("recommended_provider_order") or []
        rank = {prov: i for i, prov in enumerate(order)}
        # Stable sort: providers in the scorecard come first in scorecard order;
        # providers absent from the scorecard keep their relative policy order,
        # appended after (large sentinel rank, ties broken by original index).
        big = len(rank)
        pruned = sorted(
            enumerate(pruned),
            key=lambda pair: (rank.get(pair[1], big), pair[0]),
        )
        pruned = [prov for _, prov in pruned]

    return pruned


def _parse_attr(items: list[str] | None) -> dict:
    """Parse --attr key=value pairs into a dict (string values)."""
    out: dict[str, str] = {}
    for item in items or []:
        if "=" not in item:
            raise SystemExit(f"--attr must be key=value, got: {item!r}")
        key, _, val = item.partition("=")
        out[key.strip()] = val.strip()
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Resolve the ordered AI-provider list for a task on a machine."
    )
    parser.add_argument("task_type", help="task type (key in policy roles), e.g. review")
    parser.add_argument("machine", help="machine id, e.g. ace-linux-1")
    parser.add_argument(
        "--attr",
        action="append",
        metavar="key=value",
        help="typed task attribute (repeatable), e.g. --attr authoring_weight=heavy",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON instead of plain text")
    parser.add_argument(
        "--policy", default=str(DEFAULT_POLICY_PATH), help="path to policy YAML"
    )
    parser.add_argument(
        "--scorecard",
        default=str(DEFAULT_SCORECARD_PATH),
        help="path to scorecard JSON (skipped if missing)",
    )
    args = parser.parse_args(argv)

    attrs = _parse_attr(args.attr)
    policy = load_policy(args.policy)
    scorecard = load_scorecard(args.scorecard)

    try:
        providers = route(args.task_type, args.machine, attrs, policy=policy, scorecard=scorecard)
    except ValueError as exc:
        parser.error(str(exc))
        return 2  # unreachable; parser.error exits

    if args.json:
        print(
            json.dumps(
                {
                    "task_type": args.task_type,
                    "machine": args.machine,
                    "attrs": attrs,
                    "providers": providers,
                    "scorecard_applied": scorecard is not None,
                },
                indent=2,
            )
        )
    else:
        print(" ".join(providers))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
