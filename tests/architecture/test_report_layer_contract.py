from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator
import yaml

ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "docs/architecture"
CONTRACT_PATH = ARCH / "report-layer-contract.md"
TAXONOMY_DOC_PATH = ARCH / "report-output-taxonomy.md"
GATES_PATH = ARCH / "report-publication-gates.md"
EVIDENCE_DOC_PATH = ARCH / "report-evidence-bundle-schema.md"
SCHEMA_PATH = ARCH / "report-evidence-bundle.schema.yaml"
ROUTING_DOC_PATH = ARCH / "report-derived-learning-routing.md"
FOLLOW_UP_BACKLOG_PATH = ARCH / "report-follow-up-issue-backlog.md"
CONTENT_PIPELINE_PATH = ROOT / "docs/content-pipeline/README.md"
EVIDENCE_FIXTURE_PATH = ROOT / "tests/fixtures/architecture/report_evidence_bundle.yaml"
RESIDENCY_CASES_PATH = ROOT / "tests/fixtures/architecture/report_residency_cases.yaml"
TAXONOMY_FIXTURE_PATH = ROOT / "tests/fixtures/architecture/report_output_taxonomy.yaml"

REQUIRED_REPORT_LEVELS = {"R-L1", "R-L2", "R-L3", "R-L4", "R-L5", "R-L6"}
REQUIRED_ARTIFACT_TYPES = {
    "raw_output",
    "evidence_bundle",
    "internal_report",
    "client_facing_html",
    "limited_pdf",
    "chatbot_query_surface",
    "public_page",
    "report_derived_learning",
}
OUTPUT_RESIDENCY_ENUM = {
    "public_llm_wiki",
    "domain_private_corpus",
    "registered_client_private_corpus",
    "ignored_internal_run_artifact",
    "no_preserve",
}
REQUIRED_PUBLIC_PROMOTION_GATES = {"provenance", "license", "legal", "sanitization", "owner-review"}
PUBLISHED_CLAIM_BINDINGS = {
    "source_manifest",
    "command_manifest",
    "validation_result",
    "legal_scan",
    "checksum",
    "review_verdict",
    "output_residency",
    "promotion_decision",
}


def load_yaml(path: Path) -> dict:
    assert path.exists(), f"Missing required file: {path}"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{path} must contain a YAML mapping"
    return data


def test_report_levels_are_defined_in_contract():
    text = CONTRACT_PATH.read_text(encoding="utf-8")
    for level in REQUIRED_REPORT_LEVELS:
        assert level in text
    assert "report-derived" in text
    assert "output_residency" in text
    assert "HTML-first" in text


def test_raw_outputs_not_deliverables_by_default():
    taxonomy = load_yaml(TAXONOMY_FIXTURE_PATH)["artifacts"]
    raw_rows = [row for row in taxonomy if row["artifact_type"] == "raw_output"]
    assert raw_rows
    for row in raw_rows:
        assert row["deliverable_by_default"] is False
        assert row["default_output_residency"] == "ignored_internal_run_artifact"


def test_html_default_pdf_limited():
    taxonomy = load_yaml(TAXONOMY_FIXTURE_PATH)["artifacts"]
    html = next(row for row in taxonomy if row["artifact_type"] == "client_facing_html")
    pdf = next(row for row in taxonomy if row["artifact_type"] == "limited_pdf")
    assert html["preferred_format"] == "html"
    assert html["deliverable_by_default"] is True
    assert pdf["preferred_format"] == "pdf"
    assert pdf["requires_exception_reason"] is True
    assert pdf["exception_reason"]


def test_report_evidence_bundle_fixture_validates_against_schema():
    schema = load_yaml(SCHEMA_PATH)
    bundle = load_yaml(EVIDENCE_FIXTURE_PATH)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(bundle)


def test_report_evidence_bundle_fails_closed_for_public_claim_without_full_gates():
    schema = load_yaml(SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    bundle = load_yaml(EVIDENCE_FIXTURE_PATH)
    public = deepcopy(bundle)
    public["output_residency"] = "public_llm_wiki"
    public["published_claims"][0]["output_residency"] = "public_llm_wiki"
    public["published_claims"][0]["promotion_gates"] = ["legal"]
    assert list(validator.iter_errors(public)), "public claims must require the full promotion gate set"

    top_public = deepcopy(bundle)
    top_public["output_residency"] = "public_llm_wiki"
    top_public["published_claims"][0]["output_residency"] = "registered_client_private_corpus"
    top_public["published_claims"][0]["promotion_gates"] = ["legal"]
    assert list(validator.iter_errors(top_public)), "public bundles must require every claim to carry full gates"

    missing_binding = deepcopy(bundle)
    bindings = missing_binding["published_claims"][0]["bindings"]
    bindings.remove("promotion_decision")
    bindings.append("source_manifest")
    assert list(validator.iter_errors(missing_binding)), "claim bindings must include every required evidence binding"

    invalid_legal = deepcopy(bundle)
    invalid_legal["legal_scan"]["result"] = "maybe"
    assert list(validator.iter_errors(invalid_legal)), "legal scan result must use the closed evidence vocabulary"

    limited_pdf = deepcopy(bundle)
    limited_pdf["artifact_type"] = "limited_pdf"
    assert list(validator.iter_errors(limited_pdf)), "limited PDF bundles must carry an exception reason"
    limited_pdf["exception_reason"] = "Client contract requires a static filing copy."
    validator.validate(limited_pdf)


def test_client_public_requires_evidence_bundle():
    bundle = load_yaml(EVIDENCE_FIXTURE_PATH)
    for claim in bundle["published_claims"]:
        bindings = set(claim["bindings"])
        assert PUBLISHED_CLAIM_BINDINGS <= bindings
        assert claim["legal_scan"]["command"] == "scripts/legal/legal-sanity-scan.sh --diff-only"
        assert claim["sanitization_gate"] in {"pass", "required-before-publication"}


def test_chatbot_inherits_corpus_posture():
    cases = load_yaml(RESIDENCY_CASES_PATH)["cases"]
    assert any(case["artifact_type"] == "chatbot_query_surface" for case in cases)
    for case in cases:
        if case["artifact_type"] == "chatbot_query_surface":
            more_public = case["output_publicity_rank"] > case["corpus_publicity_rank"]
            if more_public:
                assert case["expected"] == "reject"
            if case["expected"] == "allow":
                assert case["freshness_disclosure"]
                assert case["corpus_scope_disclosure"]


def test_report_derived_learning_routes_by_output_residency():
    cases = load_yaml(RESIDENCY_CASES_PATH)["cases"]
    routing_text = ROUTING_DOC_PATH.read_text(encoding="utf-8")
    for destination in OUTPUT_RESIDENCY_ENUM:
        assert destination in routing_text
    for case in cases:
        if case["artifact_type"] == "report_derived_learning" and case["expected"] == "allow":
            assert case["output_residency"] in OUTPUT_RESIDENCY_ENUM
            assert case["target_corpus"]
            assert REQUIRED_PUBLIC_PROMOTION_GATES <= set(case["promotion_gates"])


def test_report_taxonomy_seed_artifacts():
    taxonomy = load_yaml(TAXONOMY_FIXTURE_PATH)["artifacts"]
    actual = {row["artifact_type"] for row in taxonomy}
    assert REQUIRED_ARTIFACT_TYPES <= actual
    text = TAXONOMY_DOC_PATH.read_text(encoding="utf-8")
    for artifact_type in REQUIRED_ARTIFACT_TYPES:
        assert artifact_type in text


def test_evidence_bundle_claim_binding():
    schema = load_yaml(SCHEMA_PATH)
    bundle = load_yaml(EVIDENCE_FIXTURE_PATH)
    enum_values = set(schema["properties"]["output_residency"]["enum"])
    assert schema["additionalProperties"] is False
    assert OUTPUT_RESIDENCY_ENUM == enum_values
    assert set(schema["properties"]["artifact_type"]["enum"]) == REQUIRED_ARTIFACT_TYPES
    claim_schema = schema["properties"]["published_claims"]["items"]
    assert claim_schema["additionalProperties"] is False
    assert PUBLISHED_CLAIM_BINDINGS <= set(claim_schema["required"])
    assert "source_class" in claim_schema["required"]
    assert "sanitization_gate" in claim_schema["required"]
    assert "promotion_gates" in claim_schema["required"]
    assert set(claim_schema["properties"]["output_residency"]["enum"]) == OUTPUT_RESIDENCY_ENUM
    assert set(claim_schema["properties"]["promotion_gates"]["items"]["enum"]) == REQUIRED_PUBLIC_PROMOTION_GATES
    for value in OUTPUT_RESIDENCY_ENUM:
        assert value in schema["registry_backing"]
    for claim in bundle["published_claims"]:
        assert claim["output_residency"] in OUTPUT_RESIDENCY_ENUM
        assert PUBLISHED_CLAIM_BINDINGS <= set(claim["bindings"])
        assert claim["source_class"]
        assert claim["promotion_decision"]
        if claim["output_residency"] == "public_llm_wiki":
            assert REQUIRED_PUBLIC_PROMOTION_GATES <= set(claim["promotion_gates"])


def test_publication_gates_use_canonical_legal_scan():
    text = GATES_PATH.read_text(encoding="utf-8")
    assert "scripts/legal/legal-sanity-scan.sh --diff-only" in text
    assert ".legal-deny-list.yaml" in text
    assert "parallel denylist" not in text.lower()
    for gate in REQUIRED_PUBLIC_PROMOTION_GATES:
        assert gate in text


def test_content_pipeline_has_bounded_report_crosslink():
    text = CONTENT_PIPELINE_PATH.read_text(encoding="utf-8")
    assert "docs/architecture/report-publication-gates.md" in text
    assert "report-derived learning" in text


def test_follow_up_issue_backlog_present():
    text = FOLLOW_UP_BACKLOG_PATH.read_text(encoding="utf-8")
    for phrase in [
        "gh issue create",
        "report validator",
        "artifact index",
        "publication pipeline",
        "#2729",
    ]:
        assert phrase in text
    for body_file in [
        "docs/architecture/follow-up-bodies/report-validator.md",
        "docs/architecture/follow-up-bodies/report-artifact-index.md",
        "docs/architecture/follow-up-bodies/report-publication-pipeline.md",
    ]:
        assert (ROOT / body_file).exists(), f"Missing follow-up issue body: {body_file}"
