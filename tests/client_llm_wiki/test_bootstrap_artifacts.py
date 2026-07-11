"""Static guidance/template contract tests for issue #3449."""

from __future__ import annotations

from pathlib import Path

import yaml

from client_llm_wiki.bootstrap_schema import RegistryKind, load_registry
from client_llm_wiki.promotion_ledger import validate_structure


REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = REPO_ROOT / "templates" / "client-llm-wiki"
FACTORY = REPO_ROOT / ".claude" / "skills" / "coordination" / "client-llm-wiki-factory" / "SKILL.md"


def _template_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in sorted(TEMPLATE.rglob("*")) if path.is_file())


def test_public_registry_is_the_exact_schema_v02_relocated_stub():
    registry_path = REPO_ROOT / "config" / "client-wikis.yml"
    document = yaml.safe_load(registry_path.read_text(encoding="utf-8"))

    assert document == {
        "registry_version": "0.2",
        "relocated": True,
        "wikis": [],
    }
    assert load_registry(registry_path).kind is RegistryKind.PUBLIC_STUB


def test_template_is_path_neutral_and_example_ledger_stays_structural():
    text = _template_text()

    assert "<CLIENT_RAW_ROOT>" not in text
    assert not (TEMPLATE / "projects" / "_template-project" / "raw" / ".gitkeep").exists()
    ledger = yaml.safe_load((TEMPLATE / "ledgers" / "promotion-ledger.example.yml").read_text(encoding="utf-8"))
    assert ledger["entries"][0]["source_path"] is None
    validate_structure(ledger)


def test_project_instantiation_and_redaction_customization_are_post_bootstrap():
    text = FACTORY.read_text(encoding="utf-8")
    post_bootstrap = text.index("Post-bootstrap")

    assert text.index("project-folder instantiation") > post_bootstrap
    assert text.index("redaction customization") > post_bootstrap
