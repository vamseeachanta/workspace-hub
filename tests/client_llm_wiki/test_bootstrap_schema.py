"""Fail-closed registry schema tests for issue #3449."""

from __future__ import annotations

import pytest
import yaml

from client_llm_wiki.bootstrap_schema import (
    BootstrapMode,
    RegistryKind,
    RegistryOperationError,
    RegistryParseError,
    RegistryValidationError,
    get_entry,
    parse_registry,
)


def _entry(**overrides: object) -> dict[str, object]:
    entry: dict[str, object] = {
        "short_name": "example-co",
        "repo": "example-org/llm-wiki-example-co",
        "visibility": "PRIVATE",
        "posture": "client-private",
        "status": "planned",
        "raw_roots": [],
        "raw_source_status": "not-mounted",
        "ingestion_enabled": False,
    }
    entry.update(overrides)
    return entry


def _registry(
    entries: list[dict[str, object]] | None = None, **overrides: object
) -> str:
    doc: dict[str, object] = {
        "registry_version": "0.2",
        "wikis": entries if entries is not None else [_entry()],
    }
    doc.update(overrides)
    return yaml.safe_dump(doc, sort_keys=False)


@pytest.mark.parametrize(
    ("roots", "source_status", "mode"),
    [
        ([], "not-mounted", BootstrapMode.METADATA_ONLY),
        (["/authorized/source"], "mounted", BootstrapMode.SOURCE_REGISTERED_DISABLED),
    ],
)
def test_current_registry_classifies_only_disabled_modes(roots, source_status, mode):
    registry = parse_registry(
        _registry([_entry(raw_roots=roots, raw_source_status=source_status)])
    )

    assert registry.kind is RegistryKind.CURRENT
    assert get_entry(registry, "example-co").mode is mode


@pytest.mark.parametrize(
    ("roots", "source_status"),
    [
        ([], "not-mounted"),
        (["/authorized/source"], "mounted"),
        ([], "mounted"),
        (["/authorized/source"], "not-mounted"),
    ],
)
def test_every_enabled_ingestion_state_is_rejected(roots, source_status):
    text = _registry(
        [
            _entry(
                raw_roots=roots,
                raw_source_status=source_status,
                ingestion_enabled=True,
            )
        ]
    )

    with pytest.raises(RegistryValidationError, match="ingestion_enabled"):
        parse_registry(text)


@pytest.mark.parametrize(
    ("roots", "source_status"),
    [([], "mounted"), (["/authorized/source"], "not-mounted")],
)
def test_disabled_state_rejects_root_status_mismatches(roots, source_status):
    with pytest.raises(RegistryValidationError, match="raw_source_status"):
        parse_registry(
            _registry(
                [
                    _entry(
                        raw_roots=roots,
                        raw_source_status=source_status,
                    )
                ]
            )
        )


@pytest.mark.parametrize("value", [0.2, "0.1", 1, None, True])
def test_current_version_requires_exact_string(value):
    with pytest.raises(RegistryValidationError, match="registry_version"):
        parse_registry(_registry(registry_version=value))


def test_duplicate_yaml_keys_are_rejected_before_mapping_validation():
    text = """registry_version: "0.2"
wikis:
  - short_name: example-co
    short_name: shadow-name
"""

    with pytest.raises(RegistryParseError, match="duplicate"):
        parse_registry(text)


@pytest.mark.parametrize(
    "text",
    [
        "wikis: []\n",
        "- registry_version\n- '0.2'\n",
        "registry_version: '0.2'\nwikis: not-a-sequence\n",
        "registry_version: ['unterminated'\n",
    ],
)
def test_missing_or_malformed_document_shapes_fail_closed(text):
    with pytest.raises((RegistryParseError, RegistryValidationError)):
        parse_registry(text)


def test_exact_public_stub_is_audit_only():
    text = yaml.safe_dump(
        {"registry_version": "0.2", "relocated": True, "wikis": []},
        sort_keys=False,
    )
    registry = parse_registry(text)

    assert registry.kind is RegistryKind.PUBLIC_STUB
    with pytest.raises(RegistryOperationError):
        get_entry(registry, "example-co")


@pytest.mark.parametrize(
    "doc",
    [
        {"registry_version": "0.2", "wikis": []},
        {"registry_version": "0.2", "relocated": True, "wikis": [_entry()]},
        {
            "registry_version": "0.2",
            "relocated": True,
            "wikis": [],
            "authority": "unexpected",
        },
    ],
)
def test_stub_lookalikes_fail_closed(doc):
    with pytest.raises(RegistryValidationError):
        parse_registry(yaml.safe_dump(doc, sort_keys=False))


@pytest.mark.parametrize("relocated", [1, "true", None, {}, []])
def test_authoritative_registry_rejects_malformed_relocated_values(relocated):
    with pytest.raises(RegistryValidationError, match="relocated"):
        parse_registry(_registry(relocated=relocated))


def test_legacy_numeric_version_is_audit_only():
    legacy_entry = {
        "short_name": "example-co",
        "repo": "example-org/llm-wiki-example-co",
        "visibility": "PRIVATE",
        "posture": "client-private",
        "status": "planned",
        "raw_roots": ["/authorized/legacy-source/"],
    }
    text = yaml.safe_dump({"registry_version": 0.1, "wikis": [legacy_entry]})
    registry = parse_registry(text)

    assert registry.kind is RegistryKind.LEGACY_AUDIT
    assert registry.warnings
    with pytest.raises(RegistryOperationError):
        get_entry(registry, "example-co")


def test_legacy_numeric_version_rejects_empty_raw_roots():
    legacy_entry = {
        "short_name": "example-co",
        "repo": "example-org/llm-wiki-example-co",
        "visibility": "PRIVATE",
        "posture": "client-private",
        "status": "planned",
        "raw_roots": [],
    }

    with pytest.raises(RegistryValidationError, match="raw_roots"):
        parse_registry(
            yaml.safe_dump({"registry_version": 0.1, "wikis": [legacy_entry]})
        )


@pytest.mark.parametrize("field", ["raw_source_status", "ingestion_enabled"])
def test_legacy_numeric_version_rejects_current_state_fields(field):
    legacy_entry = {
        "short_name": "example-co",
        "repo": "example-org/llm-wiki-example-co",
        "visibility": "PRIVATE",
        "posture": "client-private",
        "status": "planned",
        "raw_roots": ["/authorized/legacy-source/"],
        field: "not-mounted" if field == "raw_source_status" else False,
    }

    with pytest.raises(RegistryValidationError, match=field):
        parse_registry(
            yaml.safe_dump({"registry_version": 0.1, "wikis": [legacy_entry]})
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("short_name", None),
        ("repo", 7),
        ("visibility", "PUBLIC"),
        ("posture", "public"),
        ("status", "unknown"),
        ("raw_roots", "not-a-list"),
        ("raw_roots", [7]),
    ],
)
def test_legacy_audit_still_requires_historical_row_shape(field, value):
    row = {
        "short_name": "example-co",
        "repo": "example-org/llm-wiki-example-co",
        "visibility": "PRIVATE",
        "posture": "client-private",
        "status": "planned",
        "raw_roots": ["/authorized/legacy-source/"],
    }
    row[field] = value

    with pytest.raises(RegistryValidationError):
        parse_registry(yaml.safe_dump({"registry_version": 0.1, "wikis": [row]}))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("short_name", "Example Co"),
        ("short_name", "example_co"),
        ("short_name", "éxample"),
        ("repo", "https://example.invalid/repo"),
        ("repo", "bad_owner/llm-wiki-example-co"),
        ("repo", "-owner/llm-wiki-example-co"),
        ("repo", "owner--name/llm-wiki-example-co"),
        ("repo", f"{'a' * 40}/llm-wiki-example-co"),
        ("repo", "example-org/other-name"),
        ("repo", "example-org/llm-wiki-example-co.git"),
        ("visibility", "PUBLIC"),
        ("posture", "public"),
        ("status", "unknown"),
        ("raw_roots", "not-a-list"),
        ("raw_source_status", "unknown"),
        ("ingestion_enabled", 0),
        ("ingestion_enabled", "false"),
        ("ingestion_enabled", None),
    ],
)
def test_current_entry_rejects_invalid_identity_types_and_enums(field, value):
    with pytest.raises(RegistryValidationError):
        parse_registry(_registry([_entry(**{field: value})]))


@pytest.mark.parametrize(
    "root",
    [
        "relative/source",
        "/authorized/source/",
        "/authorized/../escape",
        "/authorized//source",
        "/",
        "/authorized/\x00source",
    ],
)
def test_source_registered_roots_reject_noncanonical_or_unsafe_paths(root):
    entry = _entry(
        raw_roots=[root],
        raw_source_status="mounted",
    )

    with pytest.raises(RegistryValidationError, match="raw_roots"):
        parse_registry(_registry([entry]))


def test_duplicate_roots_and_short_names_are_rejected():
    duplicate_roots = _entry(
        raw_roots=["/authorized/source", "/authorized/source"],
        raw_source_status="mounted",
    )
    with pytest.raises(RegistryValidationError, match="duplicate raw_roots"):
        parse_registry(_registry([duplicate_roots]))

    with pytest.raises(RegistryValidationError, match="duplicate short_name"):
        parse_registry(
            _registry(
                [
                    _entry(),
                    _entry(repo="second-org/llm-wiki-example-co"),
                ]
            )
        )


def test_missing_required_fields_fail_closed():
    for field in (
        "short_name",
        "repo",
        "visibility",
        "posture",
        "status",
        "raw_roots",
        "raw_source_status",
        "ingestion_enabled",
    ):
        entry = _entry()
        del entry[field]
        with pytest.raises(RegistryValidationError, match=field):
            parse_registry(_registry([entry]))


def test_unknown_entry_fields_are_allowed_without_conferring_authority():
    registry = parse_registry(_registry([_entry(notes="historical context")]))

    assert get_entry(registry, "example-co").mode is BootstrapMode.METADATA_ONLY


def test_get_entry_fails_for_missing_identity():
    registry = parse_registry(_registry())

    with pytest.raises(RegistryOperationError, match="not found"):
        get_entry(registry, "missing")
