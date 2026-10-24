"""Source-pinned scheduler reader evidence for issue #3789.

This is a reviewed contract, not configurable permission. The relocation source
lists crontab and searches user and system unit files without scheduler writes.
The pin covers the whole script, including its remote command strings. Any byte
change requires renewed source review. Read-only describes scheduler effects
only; it makes no safety claim about other operations performed by the script.
"""
from __future__ import annotations

import hashlib
from typing import Any

READ_TARGETS = {
    "current-user-cron", "root-cron", "systemd-user", "systemd-system",
    "windows-current-user-task",
}

# Source: scripts/operations/relocate-to-bulk.sh, scheduler reference gates;
# issue #3789 (2026), read-only consumer acceptance criterion. SHA-256 is
# computed over the exact reviewed file bytes, not scheduler runtime state.
CONSUMER_CONTRACT = {
    "scripts/operations/relocate-to-bulk.sh": (
        "relocation-scheduler-reads-v1",
        "0489adabe56417db66f167c536068537154a8acc6c3a3f5b0a341d555c61f018",
        {"current-user-cron", "systemd-system", "systemd-user"},
    ),
}

CONSUMER_DIGEST_SOURCES = {
    b"scripts/enforcement/scheduler_mutation_consumers.py",
    b"tests/enforcement/test_scheduler_mutation_consumers.py",
    b"tests/enforcement/scheduler_contract_fixtures.py",
}


def validate_consumer_schema(path: str, row: dict[str, Any]) -> list[str]:
    required = {"path", "kind", "reads", "source_attestation"}
    errors = []
    if set(row) != required:
        errors.append(f"{path}: invalid read-only consumer schema")
    reads = row.get("reads")
    if (
        not isinstance(reads, list) or not reads
        or not all(isinstance(target, str) and target in READ_TARGETS for target in reads)
        or len(reads) != len({target for target in reads if isinstance(target, str)})
    ):
        errors.append(f"{path}: invalid read-only targets")
    if not isinstance(row.get("source_attestation"), str) or not row["source_attestation"]:
        errors.append(f"{path}: read-only source attestation required")
    return errors


def validate_consumer_source(path: str, row: dict[str, Any], records) -> list[str]:
    schema_errors = validate_consumer_schema(path, row)
    if schema_errors:
        return schema_errors
    expected = CONSUMER_CONTRACT.get(path)
    body = records.get(path.encode())
    if (
        expected is None or body is None
        or row["source_attestation"] != expected[0]
        or set(row["reads"]) != expected[2]
        or hashlib.sha256(body).hexdigest() != expected[1]
    ):
        return [f"{path}: read-only source attestation failed"]
    return []
