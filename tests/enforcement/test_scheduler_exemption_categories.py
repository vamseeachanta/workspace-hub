"""Issue #3938 (2026): independent category/path/structure truth-table probes.

Expected results are obtained by hand: the original scheduler category may
suppress its inert literal; a different category must still find the same
line, and an executable statement must still be discovered in the original
category. The test injects a category only; it does not change a real rule.
"""

from dataclasses import replace

import pytest
import yaml
from test_scheduler_mutation_surfaces import load_checker
from testing.scanner_exemption_contract import ExemptionProbe, assert_exemption_contract

BODY = b'PATTERN = "crontab -"  # scheduler-mutation-forensic\n'
ORIGINAL_CATEGORY = "crontab-replace"


def test_new_category_does_not_inherit_forensic_exemption(monkeypatch):
    checker = load_checker()
    monkeypatch.setitem(checker.PRIMITIVE_PATTERNS, "new-rule-category", (rb"crontab",))
    found = checker.discover_mutation_surfaces({checker.CHECKER: BODY})
    assert found.primitives == {checker.CHECKER.decode(): {"new-rule-category"}}


def test_original_binding_inventory_requires_review_to_expand():
    checker = load_checker()
    # Independent original inventory, per issue #3938 (2026). Do not derive
    # expectations from either the production policies or detection table.
    categories = {
        "crontab-replace", "systemd-user-unit-write", "systemd-user-enable-disable",
        "windows-task-set", "windows-task-unregister-register",
    }
    paths = frozenset({
        b"scripts/enforcement/check-scheduler-mutation-surfaces.py",
        b"tests/enforcement/test_scheduler_mutation_surfaces.py",
        b"tests/enforcement/test_scheduler_mutation_hardening.py",
        b"scripts/enforcement/scheduler_mutation_attestations.py",
        b"scripts/enforcement/scheduler_mutation_discovery.py",
        b"scripts/enforcement/scheduler_mutation_wrapper_attestations.py",
    })
    assert len(checker.FORENSIC_POLICIES) == len(categories)
    assert {policy.rule_category for policy in checker.FORENSIC_POLICIES} == categories
    for policy in checker.FORENSIC_POLICIES:
        assert policy.context_id == "scheduler-mutation-forensic"
        assert policy.paths == paths
        assert policy.sentinel == b"scheduler-mutation-forensic"


@pytest.mark.parametrize("body", [
    b'PATTERN = "crontab -"; run("crontab -")  # scheduler-mutation-forensic\n',
    b'run("crontab -"); PATTERN = "crontab -"  # scheduler-mutation-forensic\n',
    b'if run("crontab -"): PATTERN = "crontab -"  # scheduler-mutation-forensic\n',
    b'obj.value = "crontab -"  # scheduler-mutation-forensic\n',
    b'PATTERN = transform("crontab -")  # scheduler-mutation-forensic\n',
    b'PATTERN = ("crontab -", set())  # scheduler-mutation-forensic\n',
    b'PATTERN = {"crontab -": set()}  # scheduler-mutation-forensic\n',
    b'PATTERN: run("crontab -") = "crontab -"  # scheduler-mutation-forensic\n',
    b'PATTERN = ("crontab -" + value)  # scheduler-mutation-forensic\n',
    b'PATTERN = "crontab -"  # scheduler-mutation-forensic-extra\n',
])
def test_executable_line_cannot_borrow_literal_exemption(body):
    checker = load_checker()
    found = checker.discover_mutation_surfaces({checker.CHECKER: body})
    assert found.primitives[checker.CHECKER.decode()] == {ORIGINAL_CATEGORY}


@pytest.mark.parametrize("body", [
    b'PATTERN = {\n    "replace": "crontab -",  # scheduler-mutation-forensic\n}\n',
    b'def example():\n    PATTERN = "crontab -"  # scheduler-mutation-forensic\n',
    'PATTERN = "synthetic λ crontab -"  # scheduler-mutation-forensic\n'.encode(),
    BODY.replace(b"\n", b"\r\n"),
])
def test_standalone_literal_structures_keep_original_exemption(body):
    checker = load_checker()
    assert checker.discover_mutation_surfaces({checker.CHECKER: body}).direct == set()


@pytest.mark.parametrize("body", [
    BODY + b"(\n",
    b'PATTERN = "crontab -"  # scheduler-mutation-forensic\n\xff',
])
def test_unparseable_blob_denies_suppression(body):
    checker = load_checker()
    assert checker.discover_mutation_surfaces({checker.CHECKER: body}).direct


def test_current_working_sources_do_not_exempt_new_paths_or_block_themselves():
    checker = load_checker()
    # Overlay uncommitted deliverables on the index snapshot without altering
    # Git metadata. The scanner must accept its actual proposed source bytes.
    records = checker.read_index_records(checker.ROOT)
    for relative in (
        "scripts/enforcement/check-scheduler-mutation-surfaces.py",
        "scripts/enforcement/scheduler_mutation_attestations.py",
        "scripts/enforcement/scanner_exemptions.py",
        "scripts/testing/scanner_exemption_contract.py",
        "tests/enforcement/test_scanner_exemptions.py",
        "tests/enforcement/test_scheduler_exemption_categories.py",
    ):
        records[relative.encode()] = (checker.ROOT / relative).read_bytes()
    discovered = checker.discover_mutation_surfaces(records)
    registry = yaml.safe_load(records[checker.REGISTRY])
    assert checker.validate_registry(registry, discovered, records).errors == []


def test_scheduler_uses_shared_exemption_contract(monkeypatch):
    checker = load_checker()
    monkeypatch.setitem(checker.PRIMITIVE_PATTERNS, "other-category", (rb"crontab",))
    good = ExemptionProbe("scheduler-mutation-forensic", ORIGINAL_CATEGORY,
                          checker.CHECKER, BODY, 1)

    def adapter(probe):
        # The scanner has one fixed context; unknown caller contexts cannot enroll.
        if probe.context_id != good.context_id:
            return False
        if not 1 <= probe.line_number <= len(probe.body.splitlines()):
            return False
        found = checker.discover_mutation_surfaces({probe.path: probe.body})
        return probe.rule_category not in found.primitives.get(probe.path.decode(), set())

    assert_exemption_contract(
        adapter, good, other_categories=("other-category",),
        other_paths=(b"scripts/production.py",),
        invalid_bodies=(
            BODY.replace(b"  # scheduler-mutation-forensic", b""),
            b'run("crontab -")  # scheduler-mutation-forensic\n',
            b'# scheduler-mutation-forensic\nPATTERN = "crontab -"\n',
        ),
    )
    assert adapter(replace(good, body=BODY + b'run("crontab -")\n')) is False


def test_exemption_helper_bytes_are_required_audit_digest_inputs():
    checker = load_checker()
    records = checker.read_index_records(checker.ROOT)
    registry = yaml.safe_load(records[checker.REGISTRY])
    source = b"scripts/enforcement/scanner_exemptions.py"
    before = checker.input_digest(
        records[checker.REGISTRY], checker.digest_record_union(registry, records)
    )
    changed = dict(records)
    changed[source] += b"\n# synthetic digest probe\n"
    after = checker.input_digest(
        changed[checker.REGISTRY], checker.digest_record_union(registry, changed)
    )
    assert after != before
    del changed[source]
    with pytest.raises(KeyError, match="digest source missing"):
        checker.digest_record_union(registry, changed)
