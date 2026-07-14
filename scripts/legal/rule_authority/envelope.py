"""Canonical CI envelope decoder with no-overwrite private output."""

from __future__ import annotations

import base64
from pathlib import Path

from .codec import AuthorityError, parse_canonical


FIELDS = {"anchor", "key", "ledger", "manifest", "map", "schema_id"}


def materialize(data, out_dir):
    value = parse_canonical(data, 32768)
    if (
        not isinstance(value, dict)
        or set(value) != FIELDS
        or value["schema_id"] != "legal-rule-ci-envelope-v1"
    ):
        raise AuthorityError("schema")
    output = Path(out_dir)
    for field in ("anchor", "ledger", "manifest", "map", "key"):
        encoded = value[field]
        try:
            decoded = base64.b64decode(encoded, validate=True)
        except Exception as exc:
            raise AuthorityError("schema") from exc
        if base64.b64encode(decoded).decode("ascii") != encoded:
            raise AuthorityError("schema")
        suffix = "b64" if field == "key" else "json"
        with (output / f"{field}.{suffix}").open("xb") as stream:
            stream.write(decoded)
