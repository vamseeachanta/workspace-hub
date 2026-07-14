"""Synthetic fixtures for rule-authority tests; contains no private values."""

from __future__ import annotations

import base64
from copy import deepcopy

REVISION = "123e4567-e89b-42d3-a456-426614174000"
OLD_REVISION = "223e4567-e89b-42d3-a456-426614174000"
RULE_ID = "323e4567-e89b-42d3-a456-426614174000"
KEY = bytes(range(32))
KEY_B64 = base64.b64encode(KEY).decode("ascii")

REGISTRY = {
    "authority_revision": REVISION,
    "generation": 2,
    "rules": [{
        "match_mode": "exact-bytes",
        "rule_id": RULE_ID,
        "severity": "block",
        "target": "both",
    }],
    "schema_id": "legal-rule-registry-v1",
}

POLICY = {
    "authority_revision": REVISION,
    "forensic_prefixes": ["docs/forensic/"],
    "generation": 2,
    "limits": {
        "max_blob_bytes": 1024,
        "max_entries": 100,
        "max_findings": 10,
        "max_request_bytes": 4096,
    },
    "schema_id": "legal-rule-policy-v1",
}

PRIVATE_MAP = {
    "authority_revision": REVISION,
    "generation": 2,
    "rules": [{
        "pattern_b64": base64.b64encode(b"synthetic-block-token").decode("ascii"),
        "rule_id": RULE_ID,
    }],
    "schema_id": "legal-rule-map-v1",
}


def changed(value, **updates):
    """Return a deep-copied fixture with top-level updates."""
    result = deepcopy(value)
    result.update(updates)
    return result
