"""Read-only consumer contract regressions for issue #3789.

Expected classifications follow manual source inspection, not the checker:
relocation lists crontab and searches user and system unit files; the sentinel
installer copies unit files and enables timers. Neither is executed here.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import sys
from pathlib import Path

import pytest
import yaml
from scheduler_contract_fixtures import checkout_records

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts/enforcement/check-scheduler-mutation-surfaces.py"
READER = "scripts/operations/relocate-to-bulk.sh"
INSTALLER = "scripts/monitoring/bundle-sentinel-install/install.sh"
READS = ["current-user-cron", "systemd-system", "systemd-user"]


def contract():
    spec = importlib.util.spec_from_file_location("consumer_scheduler_checker", CHECKER)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    # The production transport remains index-only. Overlay only intended inputs
    # for this uncommitted-tree regression; never stage or execute a scheduler.
    records = checkout_records(checker, ROOT)
    registry = yaml.safe_load(records[checker.REGISTRY])
    return checker, records, registry


def validate(checker, records, registry):
    return checker.validate_registry(
        registry, checker.discover_mutation_surfaces(records), records
    )


def reader_row(registry):
    return next(row for row in registry["surfaces"] if row["path"] == READER)


def test_worked_example_reader_and_writer_have_distinct_statuses():
    """Hand classification from the two scripts, issue #3789 (2026).

    Input: relocation runs crontab listing and searches unit files; installer
    copies units and enables timers. Method: list scheduler effects by hand.
    Answer: reader has no scheduler write operation; installer has unit-write
    and enable-disable operations, with no attested transaction. Therefore the
    statuses are read-only and migration-required respectively.
    """
    checker, records, registry = contract()
    result = validate(checker, records, registry)
    assert result.errors == []
    row = reader_row(registry)
    assert row == {
        "path": READER,
        "kind": "read-only-consumer",
        "reads": READS,
        "source_attestation": "relocation-scheduler-reads-v1",
    }
    assert result.statuses[READER] == "read-only"
    installer = next(row for row in registry["surfaces"] if row["path"] == INSTALLER)
    assert {op["primitive"] for op in installer["operations"]} == {
        "systemd-user-unit-write", "systemd-user-enable-disable",
    }
    assert all(not any(op["transaction"].values()) for op in installer["operations"])
    assert all(op["attestations"] == [] for op in installer["operations"])
    assert result.statuses[INSTALLER] == "migration-required"
    assert installer["disposition_group"] == "bundle-integrity-sentinel"
    assert all(READER not in group["members"] for group in registry["disposition_groups"])


@pytest.mark.parametrize("extra", ["operations", "delegation", "disposition_group", "transaction", "attestations", "status"])
def test_read_only_schema_forbids_mutator_fields_and_authored_status(extra):
    checker, records, registry = contract()
    reader_row(registry)[extra] = []
    assert validate(checker, records, registry).errors


@pytest.mark.parametrize("reads", [None, [], "current-user-cron", ["invented"], ["systemd-user", "systemd-user"], [None], [{}]])
def test_read_targets_are_closed_nonempty_unique(reads):
    checker, records, registry = contract()
    reader_row(registry)["reads"] = reads
    assert validate(checker, records, registry).errors


@pytest.mark.parametrize("change", ["source_attestation", "reads", "path"])
def test_yaml_cannot_assert_an_unreviewed_reader(change):
    checker, records, registry = contract()
    row = reader_row(registry)
    row[change] = {"source_attestation": "invented", "reads": ["systemd-user"], "path": INSTALLER}[change]
    assert validate(checker, records, registry).errors


@pytest.mark.parametrize("suffix", [
    b"\nprintf x | crontab -\n",
    b"\nsystemctl --user enable added.timer\n",
    b'\nwriter=crontab; printf x | "$writer" -\n',
    b"\n# Even a comment changes the reviewed bytes.\n",
])
def test_any_consumer_source_change_invalidates_the_reviewed_pin(suffix):
    checker, records, registry = contract()
    records[READER.encode()] += suffix
    assert any("read-only source attestation failed" in error for error in validate(checker, records, registry).errors)


def test_removing_consumer_source_fails_closed():
    checker, records, registry = contract()
    del records[READER.encode()]
    assert validate(checker, records, registry).errors


def test_removing_consumer_registration_fails_closed():
    checker, records, registry = contract()
    registry["surfaces"].remove(reader_row(registry))
    assert any("read-only inventory mismatch" in error for error in validate(checker, records, registry).errors)


def test_conservative_candidate_discovery_is_retained_for_reviewed_reader():
    checker, records, registry = contract()
    discovered = checker.discover_mutation_surfaces(records)
    # Model a conservative scanner match without changing the reviewed bytes.
    # A source pin, rather than a YAML-only flag, qualifies the candidate.
    discovered.direct.add(READER)
    discovered.primitives[READER] = {"systemd-user-unit-write"}
    assert checker.validate_registry(registry, discovered, records).errors == []


def test_writer_cannot_be_relabelled_as_reader():
    checker, records, registry = contract()
    reader = copy.deepcopy(reader_row(registry))
    original = next(row for row in registry["surfaces"] if row["path"] == INSTALLER)
    original.clear()
    original.update(reader, path=INSTALLER)
    assert validate(checker, records, registry).errors


def test_unknown_indirection_cannot_inherit_read_only_status():
    checker, records, registry = contract()
    discovery = checker.discover_mutation_surfaces(records)
    discovery.unknown_edges.add(READER)
    assert any("unknown scheduler indirection" in error for error in checker.validate_registry(registry, discovery, records).errors)


def test_consumer_source_and_contract_are_digest_inputs():
    checker, records, registry = contract()
    selected = checker.digest_record_union(registry, records)
    for path in (READER, "scripts/enforcement/scheduler_mutation_consumers.py", "tests/enforcement/test_scheduler_mutation_consumers.py"):
        key = path.encode()
        assert key in selected
        changed = dict(selected)
        changed[key] += b"\n"
        assert checker.input_digest(records[checker.REGISTRY], selected) != checker.input_digest(records[checker.REGISTRY], changed)
    module = sys.modules["scheduler_mutation_consumers"]
    assert module.CONSUMER_CONTRACT[READER][1] == hashlib.sha256(records[READER.encode()]).hexdigest()


def test_read_only_audit_does_not_claim_resolved_mutation():
    checker, records, registry = contract()
    result = validate(checker, records, registry)
    rendered = checker.render_html(registry, checker.discover_mutation_surfaces(records), result, "example").decode()
    row = next(line for line in rendered.splitlines() if f'data-surface="{READER}"' in line)
    assert "read-only-consumer" in row and "read-only" in row
    assert "not applicable" in row
    assert "resolved" not in row and "Transaction gaps" not in row
    assert all(target in row for target in READS)
    assert "relocation-scheduler-reads-v1" in row


def test_disposition_membership_remains_pinned_and_exact():
    checker, records, registry = contract()
    group = next(group for group in registry["disposition_groups"] if group["group_id"] == "bundle-integrity-sentinel")
    group["members"].append(READER)
    assert any("disposition contract mismatch" in error for error in validate(checker, records, registry).errors)
