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


def test_factory_uses_only_contract_driven_bootstrap_order():
    text = FACTORY.read_text(encoding="utf-8")
    forbidden = (
        "<CLIENT_RAW_ROOT>",
        "RAW=",
        "cp -a",
        "sed -i",
    )
    for token in forbidden:
        assert token not in text

    validate_at = text.index("validate-registry")
    classify_at = text.index(" classify ", validate_at)
    status_gate = text.index('test "$STATUS" = "planned"', classify_at)
    create_at = text.index("gh repo create")
    first_verify = text.index("verify-private-repo", create_at)
    clone_at = text.index("git clone", first_verify)
    render_at = text.index("client_llm_wiki.bootstrap_contract render ", clone_at)
    second_verify = text.index("verify-private-repo", first_verify + 1)
    push_at = text.index(" push origin", second_verify)
    registry_update = text.index("local_working_clone", push_at)
    checker_at = text.index("check-client-wiki-registry.sh", registry_update)

    assert validate_at < classify_at < status_gate < create_at < first_verify
    assert first_verify < clone_at < render_at < second_verify
    assert second_verify < push_at < registry_update < checker_at
    assert "WIKI_SIBLING_REGISTRY_PATH" in text
    assert "--private" in text

    deny_list = yaml.safe_load((REPO_ROOT / ".legal-deny-list.yaml").read_text(encoding="utf-8"))
    for entries in deny_list.values():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict) or "pattern" not in entry:
                continue
            pattern = entry["pattern"]
            haystack = text if entry.get("case_sensitive", True) else text.casefold()
            needle = pattern if entry.get("case_sensitive", True) else pattern.casefold()
            assert needle not in haystack


def test_project_instantiation_and_redaction_customization_are_post_bootstrap():
    text = FACTORY.read_text(encoding="utf-8")
    post_bootstrap = text.index("Post-bootstrap")

    assert text.index("project-folder instantiation") > post_bootstrap
    assert text.index("redaction customization") > post_bootstrap


def test_factory_captures_manifest_outside_the_empty_target():
    text = FACTORY.read_text(encoding="utf-8")

    assert "set -euo pipefail" in text
    assert 'MANIFEST="$TARGET/' not in text
    assert 'MANIFEST_TMP="$(mktemp)"' in text
    assert 'tee "$MANIFEST_TMP"' in text
