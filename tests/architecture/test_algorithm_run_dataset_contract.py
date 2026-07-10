from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "docs/architecture/algorithm-run-dataset-contract.yaml"
MANUAL_PATH = ROOT / "docs/governance/2026-07-10-algorithm-run-dataset-decision-manual.html"
DOCS_INDEX = ROOT / "docs/README.md"
DECISIONS = {f"D-{number:02d}" for number in range(1, 11)}
RECORDS = {
    "algorithm_version",
    "run",
    "input",
    "output",
    "metric_definition",
    "metric_observation",
    "artifact",
    "failure",
    "publication",
    "insight",
    "decision_brief",
}
MANDATORY_SECTIONS = {"inputs", "outputs"}
CHILDREN = {
    "identity": "https://github.com/vamseeachanta/workspace-hub/issues/3428",
    "artifacts": "https://github.com/vamseeachanta/workspace-hub/issues/3429",
    "inputs": "https://github.com/vamseeachanta/workspace-hub/issues/3430",
    "outputs_reports": "https://github.com/vamseeachanta/workspace-hub/issues/3431",
    "metrics": "https://github.com/vamseeachanta/workspace-hub/issues/3432",
    "publisher": "https://github.com/vamseeachanta/workspace-hub/issues/3433",
    "insights": "https://github.com/vamseeachanta/workspace-hub/issues/3434",
    "digitalmodel_pilot": "https://github.com/vamseeachanta/digitalmodel/issues/1505",
    "worldenergydata_pilot": "https://github.com/vamseeachanta/worldenergydata/issues/927",
}


class ManualParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.links: list[str] = []
        self.contract_versions: list[str] = []
        self.open_tags = {"body": 0, "main": 0, "section": 0}
        self.close_tags = {"body": 0, "main": 0, "section": 0}
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"] or "")
        if tag == "a" and values.get("href"):
            self.links.append(values["href"] or "")
        if values.get("data-contract-version"):
            self.contract_versions.append(values["data-contract-version"] or "")
        if tag in self.open_tags:
            self.open_tags[tag] += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self.close_tags:
            self.close_tags[tag] += 1

    def handle_data(self, data: str) -> None:
        self.text.append(data)


def load_contract() -> dict:
    assert CONTRACT_PATH.is_file(), f"missing contract: {CONTRACT_PATH}"
    contract = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(contract, dict)
    return contract


def parse_manual() -> ManualParser:
    parser = ManualParser()
    parser.feed(MANUAL_PATH.read_text(encoding="utf-8"))
    return parser


def assert_acyclic(nodes: dict[str, dict]) -> None:
    visited: set[str] = set()
    active: set[str] = set()

    def visit(node: str) -> None:
        assert node not in active, f"issue graph cycle at {node}"
        if node in visited:
            return
        active.add(node)
        for dependency in nodes[node]["blocked_by"]:
            assert dependency in nodes, f"unknown issue dependency: {dependency}"
            visit(dependency)
        active.remove(node)
        visited.add(node)

    for node in nodes:
        visit(node)


def test_contract_has_locked_decisions_and_records() -> None:
    contract = load_contract()

    assert contract["contract_version"] == "1.0.0"
    assert contract["status"] == "approved_parent_architecture"
    assert set(contract["decisions"]) == DECISIONS
    assert set(contract["records"]) == RECORDS
    assert all(record["owner"] for record in contract["records"].values())


def test_dataset_ownership_is_per_repository() -> None:
    datasets = load_contract()["dataset_ownership"]

    assert set(datasets["repositories"]) == {"digitalmodel", "worldenergydata"}
    assert datasets["repositories"]["digitalmodel"]["dataset"] == "aceengineer/digitalmodel-runs"
    assert datasets["repositories"]["worldenergydata"]["dataset"] == "aceengineer/worldenergydata-runs"
    assert datasets["catalog"]["contains_domain_run_records"] is False
    assert len({item["dataset"] for item in datasets["repositories"].values()}) == 2


def test_algorithm_and_run_identity_fail_closed() -> None:
    identity = load_contract()["identity"]
    algorithm = set(identity["algorithm_version_id"]["required_components"])
    run = set(identity["run_id"]["required_components"])

    assert identity["digest"] == "sha256"
    assert {
        "algorithm_id",
        "semantic_version",
        "clean_git_commit",
        "input_schema_version",
        "output_schema_version",
        "environment_digest",
    } == algorithm
    assert {"algorithm_version_id", "input_set_id", "execution_parameters", "seed"} == run
    assert {"output_set_id", "attempt_id", "retry_count", "publication_state"} <= set(
        identity["run_id"]["forbidden_components"]
    )
    assert identity["eligibility"]["dirty_source"] == "reject"
    assert identity["eligibility"]["unknown_revision"] == "reject"
    assert identity["eligibility"]["unpinned_schema"] == "reject"


def test_output_equality_policy_is_versioned() -> None:
    equality = load_contract()["identity"]["output_equality"]

    assert equality["default"] == "raw_bytes_sha256"
    assert equality["mismatch_action"] == "reject_without_mutation"
    assert set(equality["semantic_exception_requires"]) == {
        "canonicalizer_id",
        "canonicalizer_version",
        "raw_hash",
        "semantic_hash",
        "explicit_approval",
    }
    assert equality["undeclared_normalization"] == "presentation_only"


def test_public_input_admission_is_strict() -> None:
    policy = load_contract()["public_input_policy"]

    assert set(policy["required_evidence"]) == {
        "redistribution_rights",
        "schema_version",
        "snapshot_pin",
        "content_hash",
        "complete_replay_location",
    }
    assert {
        "restricted",
        "pointer_only",
        "ambiguous_license",
        "mutable_unpinned",
        "unhashed",
        "schema_invalid",
        "incomplete",
    } <= set(policy["rejection_reasons"])
    assert policy["absolute_local_paths"] == "forbidden"


def test_failed_runs_are_analysis_ineligible() -> None:
    failures = load_contract()["failure_policy"]

    assert failures["reproducible_failures_may_publish"] is True
    assert failures["transient_infrastructure_failures_may_publish"] is False
    assert set(failures["eligible_surfaces"]) == {"run_health", "diagnostics"}
    assert set(failures["forbidden_surfaces"]) == {
        "metric_observations",
        "insights",
        "decision_briefs",
    }


def test_metrics_are_algorithm_scoped() -> None:
    metrics = load_contract()["metrics"]

    assert metrics["scope"] == "single_algorithm"
    assert metrics["definition_owner_cardinality"] == 1
    assert metrics["cross_algorithm_equivalence"] == "forbidden_in_phase_1"
    assert metrics["eligible_run_statuses"] == ["succeeded_validated_reproducible"]


def test_promotion_state_machine_has_no_gate_bypass() -> None:
    promotion = load_contract()["promotion"]
    transitions = {(edge["from"], edge["to"]): edge for edge in promotion["transitions"]}

    expected = [
        ("emitted", "validated"),
        ("validated", "replayed"),
        ("replayed", "draft_rendered"),
        ("draft_rendered", "reviewed"),
        ("reviewed", "hf_candidate"),
        ("hf_candidate", "report_pinned"),
        ("report_pinned", "accepted"),
    ]
    assert list(transitions) == expected
    assert set(transitions[("report_pinned", "accepted")]["requires"]) == {
        "verified_hf_revision",
        "verified_report_commit",
        "cross_system_verification",
    }
    assert promotion["run_records_mutate_on_acceptance"] is False
    assert promotion["acceptance_record"] == "append_only_publication"
    assert promotion["orphan_candidate_recovery"] in {"resume", "append_rejected_disposition"}


def test_report_contract_has_mandatory_sections_and_exact_revision() -> None:
    report = load_contract()["report"]

    assert set(report["mandatory_sections"]) == MANDATORY_SECTIONS
    assert report["format"] == "html"
    assert report["cardinality"] == "one_rolling_report_per_algorithm"
    assert report["history"] == "source_repository_git"
    assert report["dataset_reference"] == "exact_hugging_face_revision"
    assert report["moving_revision_allowed"] is False


def test_result_envelope_crosswalk_does_not_alias_identity() -> None:
    compatibility = load_contract()["compatibility"]
    envelope = compatibility["result_envelope"]
    digitalmodel = compatibility["digitalmodel"]

    assert envelope["role"] == "execution_evidence_input"
    assert envelope["strict_identity_alias"] is False
    assert envelope["input_hash_alias"] is False
    assert compatibility["workflow_manifest"]["freshness_required"] is True
    assert compatibility["workflow_manifest"]["integer_version_is_semver"] is False
    assert set(digitalmodel["surfaces"]) == {
        "runner",
        "provenance_adapter",
        "golden_harness",
        "golden_fixture_1",
        "golden_fixture_2",
        "golden_fixture_3",
        "golden_fixture_4",
    }


def test_ecosystem_propagation_uses_shared_contract_and_thin_adapters() -> None:
    propagation = load_contract()["ecosystem_propagation"]
    manifest = yaml.safe_load(
        (ROOT / "docs/registry/workflow-manifest.json").read_text(encoding="utf-8")
    )
    registered = {row["repo"] for row in manifest["repos"]}

    assert set(propagation["observed_registered_repositories"]) == registered
    assert propagation["shared_schema_authority"] == "workspace-hub"
    assert propagation["adapter_style"] == "thin_repository_adapter"
    assert propagation["conformance_tests"] == "required"
    assert propagation["repository_contract_redefinition"] is False
    assert propagation["fresh_manifest_required_before_adoption"] is True


def test_issue_graph_is_complete_acyclic_and_independently_gated() -> None:
    issues = load_contract()["issue_graph"]

    assert set(issues) == set(CHILDREN)
    assert {key: value["url"] for key, value in issues.items()} == CHILDREN
    assert all(value["own_approval_gate"] is True for value in issues.values())
    assert all(value["parent_approval_inherited"] is False for value in issues.values())
    assert all(
        record["issue_owner"] in CHILDREN.values()
        for record in load_contract()["records"].values()
    )
    assert_acyclic(issues)


def test_html_manual_matches_contract() -> None:
    contract = load_contract()
    parser = parse_manual()
    text = " ".join(parser.text)

    assert parser.open_tags == parser.close_tags
    assert len(parser.ids) == len(set(parser.ids))
    assert {"decisions", "architecture", "identity", "records", "dataset", "report", "promotion", "compatibility", "issues"} <= set(parser.ids)
    assert parser.contract_versions == [contract["contract_version"]]
    assert "Approved parent architecture contract" in text
    assert "Ungated draft planning artifact" not in text
    for decision in DECISIONS:
        assert decision in text
    for url in CHILDREN.values():
        assert url in parser.links


def test_documentation_index_links_contract_and_manual() -> None:
    text = DOCS_INDEX.read_text(encoding="utf-8")

    assert "architecture/algorithm-run-dataset-contract.yaml" in text
    assert "governance/2026-07-10-algorithm-run-dataset-decision-manual.html" in text
