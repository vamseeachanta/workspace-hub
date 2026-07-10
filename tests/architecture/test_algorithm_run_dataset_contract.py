from __future__ import annotations

import json
import subprocess
from html.parser import HTMLParser
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "docs/architecture/algorithm-run-dataset-contract.yaml"
MANUAL_PATH = ROOT / "docs/governance/2026-07-10-algorithm-run-dataset-decision-manual.html"
DOCS_INDEX = ROOT / "docs/README.md"
VISUAL_EVIDENCE_PATH = ROOT / "docs/reports/2026-07-10-3427-implementation-evidence.html"
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
        self.tag_stack: list[str] = []
        self.structure_errors: list[str] = []
        self.pre_blocks: list[str] = []
        self._pre_text: list[str] | None = None
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"] or "")
        if tag == "a" and values.get("href"):
            self.links.append(values["href"] or "")
        if values.get("data-contract-version"):
            self.contract_versions.append(values["data-contract-version"] or "")
        if tag in {"body", "main", "section"}:
            self.tag_stack.append(tag)
        if tag == "pre":
            self._pre_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag in {"body", "main", "section"}:
            if not self.tag_stack or self.tag_stack[-1] != tag:
                self.structure_errors.append(f"unexpected closing tag: {tag}")
            else:
                self.tag_stack.pop()
        if tag == "pre" and self._pre_text is not None:
            self.pre_blocks.append("".join(self._pre_text))
            self._pre_text = None

    def handle_data(self, data: str) -> None:
        self.text.append(data)
        if self._pre_text is not None:
            self._pre_text.append(data)


def load_contract() -> dict:
    assert CONTRACT_PATH.is_file(), f"missing contract: {CONTRACT_PATH}"
    contract = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(contract, dict)
    return contract


def parse_manual() -> ManualParser:
    parser = ManualParser()
    parser.feed(MANUAL_PATH.read_text(encoding="utf-8"))
    parser.close()
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
    assert all(record["residency"] for record in contract["records"].values())
    assert set(contract["exclusions"]) == {
        "source_repository_algorithm_code_changes",
        "child_issue_implementation",
        "customer_api_implementation",
        "credentials_or_tokens",
        "private_or_restricted_run_projection",
        "combined_cross_repository_domain_run_table",
        "per_run_html_reports",
    }


def test_dataset_ownership_is_per_repository() -> None:
    datasets = load_contract()["dataset_ownership"]
    assert set(datasets["repositories"]) == {"digitalmodel", "worldenergydata"}
    assert datasets["namespace"] == {
        "candidate": "aceengineer",
        "normatively_locked": False,
        "authenticated_namespace_preflight_required": True,
        "settled_by": "publisher",
    }
    targets = [item["dataset_template"] for item in datasets["repositories"].values()]
    assert targets == ["{hf_org}/digitalmodel-runs", "{hf_org}/worldenergydata-runs"]
    assert all(not item["contains_source_repository"] for item in datasets["repositories"].values())
    assert datasets["catalog"]["contains_domain_run_records"] is False
    assert set(datasets["catalog"]["fields"]) == {
        "repository", "dataset", "supported_contract_versions",
        "last_verified_revision", "report_index",
    }
    assert len(set(targets)) == 2


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
    assert {
        "output_set_id", "attempt_id", "retry_count", "publication_state",
        "tenant_id", "customer_id", "request_id", "session_id", "user_id",
    } <= set(
        identity["run_id"]["forbidden_components"]
    )
    eligibility = identity["eligibility"]
    assert set(eligibility) == {
        "dirty_source", "unknown_revision", "unpinned_schema",
        "missing_environment_digest", "implicit_seed", "implicit_execution_default",
    }
    assert set(eligibility.values()) == {"reject"}
    valid_fixture = {condition: False for condition in eligibility}
    assert not any(valid_fixture.values())
    for condition in eligibility:
        invalid_fixture = valid_fixture | {condition: True}
        assert eligibility[condition] == "reject"
        assert [name for name, active in invalid_fixture.items() if active] == [condition]


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
    assert set(failures["normalization_requires"]) == {
        "failure_phase", "failure_code", "failure_signature",
        "curated_diagnostic_digests", "replay_evidence",
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
    assert promotion["states"] == [
        "emitted", "validated", "replayed", "draft_rendered", "reviewed",
        "hf_candidate", "report_pinned", "accepted", "rejected",
    ]
    assert set(transitions[("report_pinned", "accepted")]["requires"]) == {
        "verified_hf_revision",
        "verified_report_commit",
        "cross_system_verification",
    }
    assert promotion["run_records_mutate_on_acceptance"] is False
    assert promotion["acceptance_record"] == "append_only_publication"
    assert promotion["rejection_from_any_nonterminal_state"] is True
    assert promotion["orphan_candidate_recovery"] == {
        "action": "resume",
        "owner": "publisher",
        "resume_from": "hf_candidate",
        "rejection_disposition": "append_rejected_disposition",
    }


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
        "tests/workflow_api/goldens/buckling_parametric.json",
        "tests/workflow_api/goldens/ffs_metal_loss.json",
        "tests/workflow_api/goldens/mooring_mbl.json",
        "tests/workflow_api/goldens/wall_thickness.json",
    }
    assert compatibility["customer_api"]["separate_approval_gate"] is True
    assert compatibility["customer_api"]["private_identity_must_not_alias_public_run_id"] is True


def test_ecosystem_propagation_uses_shared_contract_and_thin_adapters() -> None:
    propagation = load_contract()["ecosystem_propagation"]
    manifest = json.loads(
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
    manual_html = MANUAL_PATH.read_text(encoding="utf-8")
    text = " ".join(parser.text)
    assert parser.structure_errors == []
    assert parser.tag_stack == []
    assert len(parser.ids) == len(set(parser.ids))
    assert {"decisions", "architecture", "identity", "records", "dataset", "report", "promotion", "compatibility", "issues"} <= set(parser.ids)
    assert parser.contract_versions == [contract["contract_version"]]
    assert "Approved parent architecture contract" in text
    assert "Ungated draft planning artifact" not in text
    for decision in DECISIONS:
        assert decision in text
    for record in RECORDS:
        assert record.replace("_", " ").title() in text
    for state in contract["promotion"]["states"]:
        assert state.replace("_", " ") in text.lower()
    assert '<tr><td>Inputs</td><td>' in manual_html
    assert '<tr><td>Outputs</td><td>' in manual_html
    assert manual_html.count("<td>Mandatory section</td>") == 2
    input_example = next(block for block in parser.pre_blocks if '"record_type": "input"' in block)
    assert '"run_id"' not in input_example
    assert any('"record_type": "run_input_membership"' in block for block in parser.pre_blocks)
    assert "{hf_org}/digitalmodel-runs" in text
    assert "aceengineer" in text and "non-normative" in text
    for url in CHILDREN.values():
        assert url in parser.links


def test_legal_scan_passes() -> None:
    completed = subprocess.run(
        [str(ROOT / "scripts/legal/legal-sanity-scan.sh"), "--diff-only", "--quiet"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_visual_inspection_evidence_is_durable() -> None:
    evidence = VISUAL_EVIDENCE_PATH.read_text(encoding="utf-8")
    assert "1440 x 1000" in evidence
    assert "390 x 844" in evidence
    assert "70996003ff5a0cf0facb5482bb2c9f32dc26339f6d35978c49332f86d9a97b92" in evidence
    assert "9507c8fefcc3902d693d90d6fa5689f3df33deb59d59135c23b4667f6a86543f" in evidence
    assert "PASS" in evidence


def test_documentation_index_links_contract_and_manual() -> None:
    text = DOCS_INDEX.read_text(encoding="utf-8")

    assert "architecture/algorithm-run-dataset-contract.yaml" in text
    assert "governance/2026-07-10-algorithm-run-dataset-decision-manual.html" in text
