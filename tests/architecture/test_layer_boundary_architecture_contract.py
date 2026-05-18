from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = ROOT / "tests/fixtures/architecture/layer_boundary_matrix.yaml"
CONTRACT_PATH = ROOT / "docs/architecture/data-execution-report-layer-contract.md"
MARKDOWN_MATRIX_PATH = ROOT / "docs/architecture/source-layer-classification-matrix.md"

REQUIRED_COLUMNS = {
    "source_class",
    "owner",
    "canonical_path",
    "layer",
    "level",
    "allowed_artifacts",
    "forbidden_artifacts",
    "retention_expectations",
    "publication_rules",
    "public_posture",
    "promotion_gate",
    "input_residency",
    "output_residency",
    "report_chatbot_eligibility",
}

SEED_SOURCE_CLASSES = {
    "workspace_control_plane_data",
    "tier1_repo_ecosystem_data",
    "tier2_publication_strategy_repos",
    "public_collection_data",
    "engineering_reference_data",
    "mounted_standards_literature",
    "client_project_data",
    "llm_wiki_raw_private_staging",
    "llm_wiki_public_content",
    "execution_artifacts",
    "report_artifacts",
}

PRIVATE_POSTURES = {"private", "restricted", "client-private", "local-private"}
PUBLIC_DESTINATIONS = {"public llm-wiki", "public chatbot", "public report", "client report"}
PUBLIC_DEFAULT_FORBIDDEN_DESTINATIONS = {"public llm-wiki", "public chatbot", "public report"}
RENDERED_MARKDOWN_COLUMNS = [
    "source_class",
    "owner",
    "canonical_path",
    "layer",
    "level",
    "public_posture",
    "promotion_gate",
    "input_residency",
    "output_residency",
    "report_chatbot_eligibility",
]


def load_matrix() -> list[dict]:
    assert MATRIX_PATH.exists(), f"Missing layer boundary fixture: {MATRIX_PATH}"
    data = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "Matrix fixture must be a mapping with a sources list"
    sources = data.get("sources")
    assert isinstance(sources, list) and sources, "Matrix fixture must define non-empty sources"
    return sources


def test_source_matrix_has_required_columns():
    for row in load_matrix():
        missing = REQUIRED_COLUMNS - set(row)
        assert not missing, f"{row.get('source_class', '<unknown>')} missing columns: {sorted(missing)}"


def test_known_sources_are_classified():
    actual = {row["source_class"] for row in load_matrix()}
    assert SEED_SOURCE_CLASSES <= actual


def test_private_sources_not_public_eligible_by_default():
    for row in load_matrix():
        posture = str(row["public_posture"]).lower()
        eligibility = str(row["report_chatbot_eligibility"]).lower()
        promotion_gate = str(row["promotion_gate"]).lower()
        publication_rules = str(row["publication_rules"]).lower()
        forbidden_artifacts = str(row["forbidden_artifacts"]).lower()
        if posture in PRIVATE_POSTURES:
            for destination in PUBLIC_DEFAULT_FORBIDDEN_DESTINATIONS:
                assert destination not in eligibility, (
                    f"{row['source_class']} must fail closed and avoid default {destination} eligibility"
                )
                assert destination in publication_rules or destination in forbidden_artifacts or "public" in publication_rules, (
                    f"{row['source_class']} must explicitly govern public publication in rules/artifacts"
                )
            for destination in PUBLIC_DESTINATIONS:
                assert not (
                    destination in eligibility and "gate" not in promotion_gate
                ), f"{row['source_class']} exposes {destination} without an explicit gate"


def test_public_eligibility_requires_explicit_gate_for_all_postures():
    for row in load_matrix():
        eligibility = str(row["report_chatbot_eligibility"]).lower()
        promotion_gate = str(row["promotion_gate"]).lower()
        for destination in PUBLIC_DESTINATIONS:
            if destination in eligibility:
                assert "gate" in promotion_gate, f"{row['source_class']} exposes {destination} without a gate"


def test_layer_transitions_are_explicit():
    assert CONTRACT_PATH.exists(), f"Missing architecture contract: {CONTRACT_PATH}"
    text = CONTRACT_PATH.read_text(encoding="utf-8")
    required_phrases = [
        "inputs -> execution -> reports/chatbots -> curated output learnings -> corpus tier",
        "A-DATA",
        "A-EXEC",
        "A-REPORT",
        "A-CURATED-LEARNING",
        "document-intelligence L-levels",
        "source_id",
        "input_residency",
        "output_residency",
        "promotion gate",
        "legal",
        "sanitization",
    ]
    for phrase in required_phrases:
        assert phrase in text, f"Contract missing required phrase: {phrase}"


def parse_markdown_matrix_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line.startswith("| ") or line.startswith("|---") or "Source class" in line:
            continue
        cells = [cell.strip().replace("\\|", "|") for cell in line.strip("|").split("|")]
        if cells:
            rows[cells[0]] = cells
    return rows


def test_markdown_matrix_is_generated_from_fixture_classes():
    assert MARKDOWN_MATRIX_PATH.exists(), f"Missing markdown matrix: {MARKDOWN_MATRIX_PATH}"
    text = MARKDOWN_MATRIX_PATH.read_text(encoding="utf-8")
    assert "reduced rendering" in text
    markdown_rows = parse_markdown_matrix_rows(text)
    for row in load_matrix():
        source_class = row["source_class"]
        assert source_class in markdown_rows, f"Markdown matrix missing row for {source_class}"
        rendered = markdown_rows[source_class]
        assert len(rendered) == len(RENDERED_MARKDOWN_COLUMNS), (
            f"Markdown row for {source_class} has {len(rendered)} columns; "
            f"expected {len(RENDERED_MARKDOWN_COLUMNS)}"
        )
        expected = [str(row[column]) for column in RENDERED_MARKDOWN_COLUMNS]
        assert rendered == expected, f"Markdown row drift for {source_class}"
