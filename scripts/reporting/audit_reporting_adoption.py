"""Read-only consistency audit for reporting-convention evidence.

Basis: engineering-reporting-conventions-proposed.html, sections 1, 9 and 10,
revision P6 (2026). Contract: docs/standards/reporting-adoption-evidence.md.
A verified snapshot or receipt does not establish installation or human use.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath

# Status vocabulary is copied from the reporting proposal, section 10 (P6).
STATUSES = (
    "not inspected", "unreachable", "saved", "revision-verified",
    "queued", "acknowledged", "adopted",
)
STORAGE = {"saved", "revision-verified", "adopted"}
DELIVERY = {"queued", "acknowledged", "adopted"}
GAPS = {"not inspected", "unreachable"}


def parse_json(text: str) -> dict:
    """Reject duplicate keys and nonfinite literals before information is lost."""
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def nonfinite(_):
        raise ValueError("nonfinite JSON literal")

    try:
        return json.loads(text, object_pairs_hook=pairs, parse_constant=nonfinite)
    except json.JSONDecodeError:
        raise ValueError("invalid JSON") from None


def _keys(value, required, optional, field):
    if not isinstance(value, dict):
        raise TypeError(f"{field}: expected object")
    if not required <= value.keys() or value.keys() - required - optional:
        raise ValueError(f"{field}: missing or unknown fields")


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field}: expected nonempty text")
    return value


def _time(value, field):
    _text(value, field)
    if not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})",
        value,
    ):
        raise ValueError(f"{field}: expected timestamp with timezone")
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise ValueError(f"{field}: invalid timestamp") from None


def _read(root: Path, value) -> bytes:
    _text(value, "path")
    path = PurePosixPath(value)
    if (
        path.is_absolute() or ".." in path.parts or ":" in value
        or "\\" in value or path.as_posix() != value or value == "."
    ):
        raise ValueError("path: expected normalized root-relative file")
    try:
        resolved = (root / value).resolve(strict=True)
        if not resolved.is_relative_to(root) or not resolved.is_file():
            raise ValueError("path: file outside evidence root or not a file")
        return resolved.read_bytes()
    except (OSError, RuntimeError):
        # Diagnostics must not repeat private paths or file contents.
        raise ValueError("path: evidence file unavailable") from None


def _digest(content: bytes, expected):
    # SHA-256 representation follows hashlib.sha256().hexdigest(); no tolerance.
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError("digest: expected lowercase SHA-256")
    if hashlib.sha256(content).hexdigest() != expected:
        raise ValueError("digest: bytes differ from pinned standard")


def verify(manifest: dict, root: Path, as_of: str) -> dict:
    """Check local evidence only; input claims never become authenticated adoption."""
    root = Path(root).resolve()
    _keys(manifest, {"standard", "observed_at", "targets"}, set(), "manifest")
    observed = _time(manifest["observed_at"], "observed_at")
    if observed > _time(as_of, "as_of"):
        raise ValueError("observed_at: future observation")
    standard = manifest["standard"]
    _keys(standard, {"path", "revision", "sha256"}, set(), "standard")
    _text(standard["revision"], "revision")
    _digest(_read(root, standard["path"]), standard["sha256"])
    targets = manifest["targets"]
    if not isinstance(targets, list) or not targets:
        raise ValueError("targets: expected nonempty enumerated inventory")

    seen = set()
    results = []
    counts = {"targets": len(targets), "snapshots_verified": 0, "receipts_verified": 0}
    state_counts = dict.fromkeys(STATUSES, 0)
    for target in targets:
        _keys(target, {"id", "status"}, {"artifact", "receipt", "reason"}, "target")
        identity = _text(target["id"], "target id")
        if not re.fullmatch(r"target-[a-z0-9]+", identity) or identity in seen:
            raise ValueError("target id: expected unique neutral alias")
        seen.add(identity)
        status = _text(target["status"], "status")
        if status not in STATUSES:
            raise ValueError("status: outside reporting vocabulary")
        state_counts[status] += 1
        if status in GAPS:
            _text(target.get("reason"), "reason")
            if "artifact" in target or "receipt" in target:
                raise ValueError("target: gap cannot carry inspected evidence")
        elif "reason" in target:
            _text(target["reason"], "reason")
        if status in STORAGE and "artifact" not in target:
            raise ValueError("artifact: required for storage claim")
        if status in DELIVERY and "receipt" not in target:
            raise ValueError("receipt: required for delivery claim")
        if status not in DELIVERY and "receipt" in target:
            raise ValueError("receipt: not applicable to reported status")

        snapshot = receipt_check = "NOT_EVALUATED"
        if "artifact" in target:
            _digest(_read(root, target["artifact"]), standard["sha256"])
            snapshot = "VERIFIED"
            counts["snapshots_verified"] += 1
        if "receipt" in target:
            try:
                receipt = parse_json(_read(root, target["receipt"]).decode("utf-8"))
                _keys(
                    receipt, {"target", "status", "revision", "sha256", "observed_at"},
                    set(), "receipt",
                )
                expected = {
                    "target": identity, "status": status,
                    "revision": standard["revision"], "sha256": standard["sha256"],
                }
                if any(receipt[key] != value for key, value in expected.items()):
                    raise ValueError("receipt: target, status or standard mismatch")
                if _time(receipt["observed_at"], "receipt observed_at") > observed:
                    raise ValueError("receipt: observation after inventory")
            except UnicodeError:
                raise ValueError("receipt: invalid UTF-8") from None
            receipt_check = "VERIFIED"
            counts["receipts_verified"] += 1
        results.append({
            "id": identity, "reported_status": status, "snapshot": snapshot,
            "receipt": receipt_check, "adoption": "NOT_EVALUATED",
        })
    return {
        "counts": counts, "reported_states": state_counts, "targets": results,
        "ecosystem_adoption": "NOT_EVALUATED",
        "limits": "Local byte and receipt consistency only; inventory completeness, "
                  "receipt authenticity, installation and current use require independent evidence.",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", required=True, type=Path, help="Explicit local evidence root")
    parser.add_argument("--as-of", required=True, help="Timestamp with timezone")
    args = parser.parse_args(argv)
    try:
        manifest = parse_json(args.manifest.read_text(encoding="utf-8"))
        result = verify(manifest, args.root, args.as_of)
    except (OSError, UnicodeError):
        print("ERROR: input unavailable or invalid UTF-8", file=sys.stderr)
        return 1
    except (TypeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
