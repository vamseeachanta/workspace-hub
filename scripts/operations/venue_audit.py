#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""venue_audit.py — parity verifier for the Telegram venue contract (#2971, F4).

Checks that a deckhand venue config conforms to the cross-repo venue-consistency
contract at ``docs/ops/telegram-venue-contract.md``. The contract specifies
machine-independent, exactly-once delivery; this verifier is the read-only
conformance gate for it.

Design
------
- PURE core: ``verify(deckhand_config: dict, contract_version: int) -> list[dict]``
  takes plain dicts and returns a list of gaps. No I/O, no network, no ssh.
- FAIL CLOSED: a missing required field, a non-conformant value, OR a deckhand
  config that declares a contract_version *older* than the current contract
  version is a gap. A config that declares no version is a gap.
- READ-ONLY venue function: per the contract (§1) parity is not lease-gated and
  may run on any host.

CLI
---
``--config <path>`` points at a deckhand venue YAML. If absent, the CLI prints a
clear message and exits non-zero WITHOUT attempting ssh or any remote fetch —
this verifier never hard-requires reaching the deckhand host.

Exit codes
----------
0  — no gaps (conformant)
1  — one or more gaps (non-conformant / fail-closed)
2  — usage / load error (no config provided, file missing, parse error)
"""
from __future__ import annotations

import argparse
import sys
from typing import Any

# The contract version this verifier knows about. Keep in lockstep with
# `contract_version:` in docs/ops/telegram-venue-contract.md.
CURRENT_CONTRACT_VERSION = 1


def required_contract_fields() -> dict:
    """Schema the deckhand venue config MUST satisfy (derived from the contract).

    Returns a dict describing each required field: where it lives in the deckhand
    config (a dotted path), a human description, and (where applicable) the
    constraint the value must meet. This is the machine-readable summary of the
    "Conformance summary" section of the contract doc.

    Schema shape (per entry)::

        "<dotted.path>": {
            "detail": <why it is required / what it must be>,
            # optional constraints used by verify():
            "min_version": <int>,          # value must be an int >= this
            "must_equal": <value>,         # value must == this
            "must_not_contain": [<str>],   # str value must not contain these tokens
            "present": True,               # field must merely exist (non-empty)
        }
    """
    return {
        "venue_contract.contract_version": {
            "detail": (
                "deckhand must pin the venue contract version it implements; "
                f"must be an integer >= {CURRENT_CONTRACT_VERSION} (fail closed on "
                "older/unknown)"
            ),
            "min_version": CURRENT_CONTRACT_VERSION,
        },
        "venue_contract.idempotency.scheme": {
            "detail": (
                "idempotency key must be the composite 'client-ref + message-type "
                "+ monotonic-seq', NOT a raw content hash"
            ),
            "must_equal": "client-ref+message-type+monotonic-seq",
            "must_not_contain": ["content-hash", "content_hash", "contenthash"],
        },
        "venue_contract.dead_letter.target": {
            "detail": (
                "bounded retries terminate to a dead-letter target with an "
                "operator alert (JSONL via scripts/notify.sh)"
            ),
            "present": True,
        },
        "venue_contract.audit.pii_safe": {
            "detail": (
                "audit rows store host/when/scope/idempotency-key/result ONLY; "
                "config must declare pii_safe: true"
            ),
            "must_equal": True,
        },
        "venue_contract.escalation.label_swap": {
            "detail": (
                "escalation idempotency via GitHub label swap "
                "'needs-mirror -> mirrored' (durable mirror-state marker)"
            ),
            "must_equal": "needs-mirror->mirrored",
        },
    }


_MISSING = object()


def _get_path(config: dict, dotted: str) -> Any:
    """Walk a dotted path into nested dicts; return _MISSING if any hop absent."""
    cur: Any = config
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return _MISSING
        cur = cur[part]
    return cur


def _is_empty(value: Any) -> bool:
    """A field counts as absent if it is None or an empty string/collection."""
    if value is None:
        return True
    if isinstance(value, (str, list, dict, tuple, set)) and len(value) == 0:
        return True
    return False


def verify(deckhand_config: dict, contract_version: int) -> list[dict]:
    """Return the list of conformance gaps. Empty list == conformant.

    PURE: takes a plain dict (the loaded deckhand config) and the current
    contract version. Each gap is ``{"field": <dotted.path>, "detail": <why>}``.

    FAIL CLOSED:
      * a required field that is missing/empty is a gap;
      * a value that violates its constraint is a gap;
      * specifically, a declared ``contract_version`` < ``contract_version`` (the
        current contract version passed in) is a gap.
    """
    if not isinstance(deckhand_config, dict):
        return [
            {
                "field": "<root>",
                "detail": (
                    "deckhand config must be a mapping/dict; got "
                    f"{type(deckhand_config).__name__}"
                ),
            }
        ]

    gaps: list[dict] = []
    schema = required_contract_fields()

    for field, spec in schema.items():
        value = _get_path(deckhand_config, field)

        if value is _MISSING or _is_empty(value):
            gaps.append({"field": field, "detail": f"missing required field: {spec['detail']}"})
            continue

        # contract_version: fail closed on older/unknown.
        if "min_version" in spec:
            floor = contract_version  # current contract version is authoritative
            if not isinstance(value, int) or isinstance(value, bool):
                gaps.append(
                    {
                        "field": field,
                        "detail": (
                            f"contract_version must be an integer; got {value!r}"
                        ),
                    }
                )
                continue
            if value < floor:
                gaps.append(
                    {
                        "field": field,
                        "detail": (
                            f"declared contract_version {value} is older than "
                            f"current {floor} (fail closed)"
                        ),
                    }
                )
                continue

        if "must_equal" in spec and value != spec["must_equal"]:
            gaps.append(
                {
                    "field": field,
                    "detail": (
                        f"expected {spec['must_equal']!r}, got {value!r} — "
                        f"{spec['detail']}"
                    ),
                }
            )
            continue

        if "must_not_contain" in spec and isinstance(value, str):
            lowered = value.lower()
            bad = [tok for tok in spec["must_not_contain"] if tok in lowered]
            if bad:
                gaps.append(
                    {
                        "field": field,
                        "detail": (
                            f"value {value!r} contains forbidden token(s) {bad} — "
                            f"{spec['detail']}"
                        ),
                    }
                )
                continue

    return gaps


def _load_config(path: str) -> dict:
    """Load a YAML deckhand config from ``path``. Raises on failure."""
    import yaml  # imported lazily so importing the module needs no yaml

    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"top-level YAML in {path} is not a mapping")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Parity verifier for the Telegram venue contract (#2971, F4). "
            "Read-only; never reaches the deckhand host."
        )
    )
    parser.add_argument(
        "--config",
        metavar="PATH",
        help=(
            "path to a deckhand venue YAML (e.g. a copy of "
            "config/deckhand/policy.yml). If omitted, no remote fetch is "
            "attempted."
        ),
    )
    args = parser.parse_args(argv)

    if not args.config:
        print(
            "venue_audit: no --config provided.\n"
            "  This verifier does NOT ssh into the deckhand host. Provide a local\n"
            "  copy of the deckhand venue config, e.g.:\n"
            "    venue_audit.py --config /path/to/deckhand/policy.yml\n"
            f"  Current contract version: {CURRENT_CONTRACT_VERSION} "
            "(see docs/ops/telegram-venue-contract.md).",
            file=sys.stderr,
        )
        return 2

    try:
        config = _load_config(args.config)
    except FileNotFoundError:
        print(f"venue_audit: config not found: {args.config}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 - surface any load/parse error clearly
        print(f"venue_audit: failed to load {args.config}: {exc}", file=sys.stderr)
        return 2

    gaps = verify(config, CURRENT_CONTRACT_VERSION)

    if not gaps:
        print(
            f"venue_audit: CONFORMANT — {args.config} satisfies venue contract "
            f"v{CURRENT_CONTRACT_VERSION}."
        )
        return 0

    print(
        f"venue_audit: {len(gaps)} GAP(S) — {args.config} does NOT conform to "
        f"venue contract v{CURRENT_CONTRACT_VERSION}:",
        file=sys.stderr,
    )
    for gap in gaps:
        print(f"  [{gap['field']}] {gap['detail']}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
