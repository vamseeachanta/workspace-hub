"""Static guidance/template contract tests for issue #3449."""

from __future__ import annotations

from pathlib import Path
import re

import yaml

from client_llm_wiki.bootstrap_schema import RegistryKind, load_registry
from client_llm_wiki.promotion_ledger import validate_structure


REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = REPO_ROOT / "templates" / "client-llm-wiki"
FACTORY = (
    REPO_ROOT
    / ".claude"
    / "skills"
    / "coordination"
    / "client-llm-wiki-factory"
    / "SKILL.md"
)


def _template_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(TEMPLATE.rglob("*"))
        if path.is_file()
    )


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
    assert not (
        TEMPLATE / "projects" / "_template-project" / "raw" / ".gitkeep"
    ).exists()
    ledger = yaml.safe_load(
        (TEMPLATE / "ledgers" / "promotion-ledger.example.yml").read_text(
            encoding="utf-8"
        )
    )
    assert ledger["entries"][0]["source_path"] is None
    validate_structure(ledger)


def test_project_instantiation_and_redaction_customization_are_post_bootstrap():
    text = FACTORY.read_text(encoding="utf-8")
    post_bootstrap = text.index("Post-bootstrap")

    assert text.index("project-folder instantiation") > post_bootstrap
    assert text.index("redaction customization") > post_bootstrap


def test_factory_static_security_tokens_and_deny_list():
    text = FACTORY.read_text(encoding="utf-8")
    for token in ("<CLIENT_RAW_ROOT>", "RAW=", "cp -a", "sed -i"):
        assert token not in text
    deny_list = yaml.safe_load(
        (REPO_ROOT / ".legal-deny-list.yaml").read_text(encoding="utf-8")
    )
    for entries in deny_list.values():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict) or "pattern" not in entry:
                continue
            text_value = text if entry.get("case_sensitive", True) else text.casefold()
            pattern = entry["pattern"]
            pattern = (
                pattern if entry.get("case_sensitive", True) else pattern.casefold()
            )
            assert pattern not in text_value


def test_factory_static_authorization_and_mutation_order():
    text = FACTORY.read_text(encoding="utf-8")
    start = text.index("# FACTORY_WORKFLOW_V2")
    validate = text.index("validate-registry", start)
    classify = text.index(" classify ", validate)
    status = text.index('test "$STATUS" = "planned"', classify)
    create = text.index(" create-private-repo ", status)
    attest_first = text.index("verify-private-repo", create)
    clone = text.index(" clone-private-repo ", attest_first)
    checker = text.index("check-client-wiki-registry.sh", clone)
    render = text.index(" render ", checker)
    finalize = text.index("finalize-scaffold", render)
    attest_final = text.index("verify-private-repo", finalize)
    update = text.index('"$REGISTRY_UPDATE_TOOL"', attest_final)

    assert validate < classify < status < create < attest_first < clone < checker
    assert checker < render < finalize < attest_final < update
    assert "WIKI_SIBLING_REGISTRY_PATH" in text
    assert "Create the remote as private" in text
    assert "Both operational commands pin github.com" in text


def test_factory_has_no_direct_operational_git_or_gh_children():
    text = FACTORY.read_text(encoding="utf-8")
    assert "env -u GH_HOST" not in text
    assert "gh repo create" not in text
    assert not re.search(r"(?m)^git clone ", text)
