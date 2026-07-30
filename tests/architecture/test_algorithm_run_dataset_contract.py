from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "docs/architecture/algorithm-run-dataset-contract.yaml"
MANUAL_PATH = ROOT / "docs/governance/2026-07-10-algorithm-run-dataset-decision-manual.html"
EVIDENCE_PATH = ROOT / "docs/reports/2026-07-10-3427-implementation-evidence.html"
DOCS_INDEX = ROOT / "docs/README.md"
DECISIONS = {f"D-{number:02d}" for number in range(1, 11)}
RECORD_TABLES = {
    "algorithm_version": "algorithm_versions",
    "run": "runs",
    "input": "inputs",
    "output": "outputs",
    "metric_definition": "metric_definitions",
    "metric_observation": "metric_observations",
    "artifact": "artifacts",
    "failure": "failures",
    "publication": "publications",
    "insight": "insights",
    "decision_brief": "decision_briefs",
}
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
DEPENDENCIES = {
    "identity": [], "artifacts": ["identity"], "inputs": ["identity", "artifacts"],
    "outputs_reports": ["identity", "artifacts"], "metrics": ["identity", "outputs_reports"],
    "publisher": ["identity", "artifacts", "inputs", "outputs_reports", "metrics"],
    "digitalmodel_pilot": ["publisher"], "worldenergydata_pilot": ["publisher"],
    "insights": ["metrics", "digitalmodel_pilot", "worldenergydata_pilot"],
}
PROMOTION_REQUIREMENTS = {
    ("emitted", "validated"): ["schema", "hashes", "provenance", "license", "legal", "sanitization", "clean_source"],
    ("validated", "replayed"): {
        "all_of": ["clean_environment_replay"],
        "one_of": {
            "succeeded": ["output_equality"],
            "reproducible_failure": ["failure_signature_equality", "curated_diagnostic_equality"],
        },
    },
    ("replayed", "draft_rendered"): ["mandatory_report_sections", "exact_candidate_run_set"],
    ("draft_rendered", "reviewed"): ["human_promotion_review", "adversarial_artifact_review"],
    ("reviewed", "hf_candidate"): ["complete_projection_commit", "object_integrity"],
    ("hf_candidate", "report_pinned"): ["exact_hf_revision", "source_report_commit"],
    ("report_pinned", "accepted"): ["verified_hf_revision", "verified_report_commit", "cross_system_verification"],
}
EXCLUSIONS = {
    "source_repository_algorithm_code_changes", "workflow_registry_changes",
    "source_repository_report_changes", "hugging_face_dataset_changes",
    "hugging_face_resource_changes", "credentials_or_tokens", "child_issue_implementation",
    "customer_api_implementation", "private_or_restricted_run_projection",
    "combined_cross_repository_domain_run_table", "per_run_html_reports",
}
REVIEWED_ARTIFACTS = (
    CONTRACT_PATH,
    MANUAL_PATH,
    EVIDENCE_PATH,
    DOCS_INDEX,
    Path(__file__),
)


class ManualParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.links: list[str] = []
        self.contract_versions: list[str] = []
        self.stack: list[str] = []
        self.structure_errors: list[str] = []
        self.counts = {"body": 0, "main": 0, "section": 0}
        self.records: set[str] = set()
        self.tables: set[str] = set()
        self.states: set[str] = set()
        self.exclusions: set[str] = set()
        self.relationships: set[str] = set()
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
        for attribute, target in (
            ("data-record", self.records), ("data-table", self.tables),
            ("data-state", self.states), ("data-exclusion", self.exclusions),
            ("data-relationship", self.relationships),
        ):
            if values.get(attribute):
                target.add(values[attribute] or "")
        if tag in self.counts:
            expected = {"body": None, "main": "body", "section": "main"}[tag]
            parent = self.stack[-1] if self.stack else None
            if parent != expected:
                self.structure_errors.append(f"{tag} parent is {parent}, expected {expected}")
            self.counts[tag] += 1
            self.stack.append(tag)
        if tag == "pre":
            self._pre_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag in self.counts:
            if not self.stack or self.stack[-1] != tag:
                self.structure_errors.append(f"unexpected closing tag: {tag}")
            else:
                self.stack.pop()
        if tag == "pre" and self._pre_text is not None:
            self.pre_blocks.append("".join(self._pre_text))
            self._pre_text = None

    def handle_data(self, data: str) -> None:
        self.text.append(data)
        if self._pre_text is not None:
            self._pre_text.append(data)


def load_contract() -> dict:
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
            assert dependency in nodes
            visit(dependency)
        active.remove(node)
        visited.add(node)

    for node in nodes:
        visit(node)


def evaluate_identity(policy: dict, fixture: dict[str, bool]) -> str:
    return "reject" if any(fixture.get(name) and action == "reject" for name, action in policy.items()) else "accept"


def evaluate_input(policy: dict, fixture: dict) -> str:
    missing = any(not fixture.get(name) for name in policy["required_evidence"])
    rejected = any(fixture.get(name, False) for name in policy["rejection_reasons"])
    return "reject" if missing or rejected else "accept"


def replay_satisfied(requirement: dict, outcome: str, evidence: set[str]) -> bool:
    required = set(requirement["all_of"] + requirement["one_of"][outcome])
    return required <= evidence


def test_contract_has_locked_decisions_and_records() -> None:
    contract = load_contract()
    assert contract["contract_version"] == "1.0.0"
    assert contract["status"] == "approved_parent_architecture"
    assert set(contract["decisions"]) == DECISIONS
    assert set(contract["records"]) == set(RECORD_TABLES)
    assert {name: row["dataset_table"] for name, row in contract["records"].items()} == RECORD_TABLES
    assert all(row["owner"] and row["residency"] for row in contract["records"].values())
    assert set(contract["exclusions"]) == EXCLUSIONS


def test_dataset_ownership_is_per_repository() -> None:
    datasets = load_contract()["dataset_ownership"]
    assert set(datasets["repositories"]) == {"digitalmodel", "worldenergydata"}
    assert datasets["namespace"] == {"candidate": "aceengineer", "normatively_locked": False, "authenticated_namespace_preflight_required": True, "settled_by": "publisher"}
    targets = [item["dataset_template"] for item in datasets["repositories"].values()]
    assert targets == ["{hf_org}/digitalmodel-runs", "{hf_org}/worldenergydata-runs"]
    assert all(not item["contains_source_repository"] for item in datasets["repositories"].values())
    assert datasets["catalog"]["contains_domain_run_records"] is False


def test_algorithm_and_run_identity_fail_closed() -> None:
    identity = load_contract()["identity"]
    assert set(identity["algorithm_version_id"]["required_components"]) == {"algorithm_id", "semantic_version", "clean_git_commit", "input_schema_version", "output_schema_version", "environment_digest"}
    assert set(identity["input_record_id"]["required_components"]) == {"role", "native_schema_version", "source_snapshot", "transformation_id", "artifact_sha256", "redistribution_rights", "complete_replay_location"}
    assert {"run_id", "algorithm_version_id", "attempt_id", "publication_state", "tenant_id", "customer_id", "request_id", "session_id", "user_id"} <= set(identity["input_record_id"]["forbidden_components"])
    assert set(identity["run_id"]["required_components"]) == {"algorithm_version_id", "input_set_id", "execution_parameters", "seed"}
    assert {"output_set_id", "attempt_id", "retry_count", "publication_state", "tenant_id", "customer_id", "request_id", "api_request_id", "session_id", "user_id"} <= set(identity["run_id"]["forbidden_components"])
    policy = identity["eligibility"]
    valid = {name: False for name in policy}
    assert evaluate_identity(policy, valid) == "accept"
    for condition in policy:
        assert evaluate_identity(policy, valid | {condition: True}) == "reject"


def test_input_membership_is_owned_without_aliasing_input_identity() -> None:
    membership = load_contract()["identity"]["run_input_membership"]
    assert membership == {"owner": "dedicated_hf_dataset", "residency": "dedicated_hf_dataset", "dataset_table": "run_input_memberships", "identity": "membership_id", "required_components": ["run_id", "role", "input_record_id"]}


def test_output_equality_policy_is_versioned() -> None:
    equality = load_contract()["identity"]["output_equality"]
    assert equality["default"] == "raw_bytes_sha256"
    assert equality["mismatch_action"] == "reject_without_mutation"
    assert set(equality["semantic_exception_requires"]) == {"canonicalizer_id", "canonicalizer_version", "raw_hash", "semantic_hash", "explicit_approval"}
    assert equality["undeclared_normalization"] == "presentation_only"


def test_public_input_admission_is_strict() -> None:
    policy = load_contract()["public_input_policy"]
    valid = {name: "present" for name in policy["required_evidence"]}
    valid.update({name: False for name in policy["rejection_reasons"]})
    assert evaluate_input(policy, valid) == "accept"
    for name in policy["required_evidence"]:
        assert evaluate_input(policy, valid | {name: None}) == "reject"
    for name in policy["rejection_reasons"]:
        assert evaluate_input(policy, valid | {name: True}) == "reject"
    assert policy["absolute_local_paths"] == "forbidden"


def test_failed_runs_are_analysis_ineligible() -> None:
    failures = load_contract()["failure_policy"]
    assert failures["reproducible_failures_may_publish"] is True
    assert failures["transient_infrastructure_failures_may_publish"] is False
    assert set(failures["eligible_surfaces"]) == {"run_health", "diagnostics"}
    assert set(failures["forbidden_surfaces"]) == {"metric_observations", "insights", "decision_briefs"}
    assert set(failures["normalization_requires"]) == {"failure_phase", "failure_code", "failure_signature", "curated_diagnostic_digests", "replay_evidence"}


def test_metrics_are_algorithm_scoped() -> None:
    metrics = load_contract()["metrics"]
    assert metrics["scope"] == "single_algorithm"
    assert metrics["definition_owner_cardinality"] == 1
    assert metrics["cross_algorithm_equivalence"] == "forbidden_in_phase_1"
    assert metrics["eligible_run_statuses"] == ["succeeded_validated_reproducible"]


def test_promotion_state_machine_has_no_gate_bypass() -> None:
    promotion = load_contract()["promotion"]
    edges = [(edge["from"], edge["to"]) for edge in promotion["transitions"]]
    assert len(edges) == len(set(edges))
    assert {edge: row["requires"] for edge, row in zip(edges, promotion["transitions"])} == PROMOTION_REQUIREMENTS
    assert promotion["states"] == ["emitted", "validated", "replayed", "draft_rendered", "reviewed", "hf_candidate", "report_pinned", "accepted", "rejected"]
    assert not ({"accepted", "rejected"} & {source for source, _ in edges})
    assert promotion["rejection_from_any_nonterminal_state"] is True
    assert promotion["run_records_mutate_on_acceptance"] is False
    assert promotion["acceptance_record"] == "append_only_publication"
    assert promotion["orphan_candidate_recovery"] == {"action": "resume", "owner": "publisher", "resume_from": "hf_candidate", "rejection_disposition": "append_rejected_disposition"}


def test_success_and_reproducible_failure_replay_paths_are_executable() -> None:
    requirement = PROMOTION_REQUIREMENTS[("validated", "replayed")]
    assert replay_satisfied(requirement, "succeeded", {"clean_environment_replay", "output_equality"})
    assert replay_satisfied(requirement, "reproducible_failure", {"clean_environment_replay", "failure_signature_equality", "curated_diagnostic_equality"})
    assert not replay_satisfied(requirement, "succeeded", {"clean_environment_replay"})
    assert not replay_satisfied(requirement, "reproducible_failure", {"clean_environment_replay", "failure_signature_equality"})


def test_report_and_compatibility_contracts_are_exact() -> None:
    contract = load_contract()
    report = contract["report"]
    compatibility = contract["compatibility"]
    assert report["mandatory_sections"] == ["inputs", "outputs"]
    assert report["format"] == "html" and report["cardinality"] == "one_rolling_report_per_algorithm"
    assert report["dataset_reference"] == "exact_hugging_face_revision" and report["moving_revision_allowed"] is False
    assert compatibility["result_envelope"]["strict_identity_alias"] is False
    assert compatibility["result_envelope"]["input_hash_alias"] is False
    assert compatibility["workflow_manifest"]["freshness_required"] is True
    assert set(compatibility["digitalmodel"]["surfaces"]) == {"runner", "provenance_adapter", "golden_harness", "tests/workflow_api/goldens/buckling_parametric.json", "tests/workflow_api/goldens/ffs_metal_loss.json", "tests/workflow_api/goldens/mooring_mbl.json", "tests/workflow_api/goldens/wall_thickness.json"}
    assert compatibility["customer_api"]["separate_approval_gate"] is True
    assert compatibility["customer_api"]["private_identity_must_not_alias_public_run_id"] is True


def test_ecosystem_observation_resolves_and_partitions_registered_repositories() -> None:
    propagation = load_contract()["ecosystem_propagation"]
    manifest = json.loads((ROOT / "docs/registry/workflow-manifest.json").read_text())
    registered = {row["repo"] for row in manifest["repos"]}
    observation = propagation["manifest_observation_2026_07_10"]
    assert set(propagation["observed_registered_repositories"]) == registered
    assert set(observation["resolved"]) == registered
    assert set(observation["drifted"]) == {"assetutilities", "worldenergydata"}
    assert set(observation["unchanged"]) == {"digitalmodel", "assethold"}
    assert observation["missing"] == []
    assert set(observation["drifted"]) | set(observation["unchanged"]) == registered
    assert propagation["repository_contract_redefinition"] is False


def test_issue_graph_is_complete_acyclic_and_independently_gated() -> None:
    issues = load_contract()["issue_graph"]
    assert set(issues) == set(CHILDREN)
    assert {key: row["url"] for key, row in issues.items()} == CHILDREN
    assert {key: row["blocked_by"] for key, row in issues.items()} == DEPENDENCIES
    assert all(row["own_approval_gate"] is True for row in issues.values())
    assert all(row["parent_approval_inherited"] is False for row in issues.values())
    assert issues["publisher"]["related_dependencies"] == ["https://github.com/vamseeachanta/workspace-hub/issues/2975", "https://github.com/vamseeachanta/workspace-hub/issues/3013"]
    assert_acyclic(issues)


def test_html_manual_matches_contract_structurally() -> None:
    contract = load_contract()
    parser = parse_manual()
    manual = MANUAL_PATH.read_text(encoding="utf-8")
    assert parser.structure_errors == [] and parser.stack == []
    assert parser.counts["body"] == 1 and parser.counts["main"] == 1 and parser.counts["section"] > 0
    assert len(parser.ids) == len(set(parser.ids))
    assert {"decisions", "architecture", "identity", "records", "dataset", "report", "promotion", "compatibility", "issues"} <= set(parser.ids)
    assert parser.contract_versions == [contract["contract_version"]]
    assert parser.records == set(RECORD_TABLES)
    assert parser.tables == set(RECORD_TABLES.values()) | {"run_input_memberships"}
    assert parser.relationships == {"run_input_membership"}
    assert parser.states == set(contract["promotion"]["states"])
    assert parser.exclusions == EXCLUSIONS
    input_example = next(block for block in parser.pre_blocks if '"record_type": "input"' in block)
    assert '"run_id"' not in input_example
    assert manual.count("<td>Mandatory section</td>") == 2
    assert "{hf_org}/digitalmodel-runs" in " ".join(parser.text)
    for url in CHILDREN.values():
        assert url in parser.links


def test_legal_scan_passes_on_nonempty_artifact_set(tmp_path: Path) -> None:
    sandbox = tmp_path / "repo"
    legal_dir = sandbox / "scripts/legal"
    legal_dir.mkdir(parents=True)
    shutil.copy2(ROOT / "scripts/legal/legal-sanity-scan.sh", legal_dir)
    shutil.copy2(ROOT / ".legal-deny-list.yaml", sandbox)
    subprocess.run(["git", "init", "-q"], cwd=sandbox, check=True)
    subprocess.run(["git", "add", "."], cwd=sandbox, check=True)
    subprocess.run(["git", "-c", "user.name=contract-test", "-c", "user.email=test@example.invalid", "commit", "-qm", "baseline"], cwd=sandbox, check=True)
    expected = set()
    for source in REVIEWED_ARTIFACTS:
        relative = source.relative_to(ROOT)
        destination = sandbox / "reviewed" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        expected.add((Path("reviewed") / relative).as_posix())
    subprocess.run(["git", "add", "-N", "reviewed"], cwd=sandbox, check=True)
    changed = subprocess.check_output(["git", "diff", "--name-only", "HEAD"], cwd=sandbox, text=True).splitlines()
    assert set(changed) == expected and changed
    completed = subprocess.run([str(legal_dir / "legal-sanity-scan.sh"), "--diff-only", "--quiet"], cwd=sandbox, capture_output=True, text=True, check=False)
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_targeted_absolute_path_guard_passes() -> None:
    paths = [str(path.relative_to(ROOT)) for path in REVIEWED_ARTIFACTS]
    completed = subprocess.run([str(ROOT / "scripts/enforcement/check-no-abs-paths.sh"), *paths], cwd=ROOT, capture_output=True, text=True, check=False)
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_visual_inspection_evidence_is_bound_to_manual() -> None:
    evidence = EVIDENCE_PATH.read_text(encoding="utf-8")
    manual_digest = hashlib.sha256(MANUAL_PATH.read_bytes()).hexdigest()
    assert f'data-manual-sha256="{manual_digest}"' in evidence
    assert "Full-document desktop" in evidence and "Full-document mobile" in evidence
    for section in ("decisions", "architecture", "identity", "records", "dataset", "report", "promotion", "compatibility", "issues"):
        assert f'data-section="{section}"' in evidence
    assert "PASS" in evidence and "PNG SHA-256" in evidence


def test_documentation_index_links_contract_and_manual() -> None:
    text = DOCS_INDEX.read_text(encoding="utf-8")
    assert "architecture/algorithm-run-dataset-contract.yaml" in text
    assert "governance/2026-07-10-algorithm-run-dataset-decision-manual.html" in text
