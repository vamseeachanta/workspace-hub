"""Synthetic exposure contract tests; no private registry is required."""

import json
from copy import deepcopy

import pytest

from src.workspace_hub.exposure import ExposureError, RegistryRecord, Surface, expose


def record_data():
    return {
        "id": "V-0107",
        "client_id": "C-0004",
        "fields": {
            "name": {
                "value": "Synthetic Hull Zephyr",
                "codename": "bulk carrier A",
                "exposure_class": "public",
                "kind": "name",
            },
            "region": {"value": "broad coastal region", "exposure_class": "public"},
            "capacity": {"value": 25000, "exposure_class": "public"},
            "design": {"value": {"draft_m": 8.5}, "exposure_class": "client"},
            "notes": {"value": "synthetic internal note", "exposure_class": "internal"},
            "credential": {
                "value": "synthetic-placeholder",
                "exposure_class": "public",
                "kind": "secret",
            },
            "contact": {
                "value": "synthetic contact detail",
                "exposure_class": "public",
                "kind": "contact",
            },
        },
        "singling_out": {"reviewed": True, "combinations": []},
    }


def record():
    return RegistryRecord.from_dict(record_data())


@pytest.mark.parametrize("surface", list(Surface))
def test_every_surface(surface):
    result = expose(
        record(), surface, client_id="C-0004" if surface == Surface.CLIENT else None
    )
    if surface == Surface.INTERNAL:
        assert result["id"] == "V-0107"
        assert result["fields"]["name"] == "Synthetic Hull Zephyr"
        assert set(result["fields"]) == set(record_data()["fields"])
    elif surface == Surface.CLIENT:
        assert result == {
            "fields": {
                "name": "Synthetic Hull Zephyr",
                "region": "broad coastal region",
                "capacity": 25000,
                "design": {"draft_m": 8.5},
            }
        }
    else:
        assert result == {
            "fields": {
                "name": "bulk carrier A",
                "region": "broad coastal region",
                "capacity": 25000,
            }
        }


def test_other_client_gets_codenames_and_no_client_fields():
    assert expose(record(), Surface.CLIENT, client_id="C-0005") == expose(
        record(), Surface.PUBLIC_REPOSITORY
    )


def test_field_ownership_overrides_record_owner():
    data = record_data()
    data["fields"]["name"]["client_id"] = "C-0005"
    data["fields"]["design"]["client_id"] = "C-0005"
    result = expose(RegistryRecord.from_dict(data), "client", client_id="C-0004")
    assert result["fields"]["name"] == "bulk carrier A"
    assert "design" not in result["fields"]


@pytest.mark.parametrize("surface", [s for s in Surface if s != Surface.INTERNAL])
def test_refuses_surviving_identifying_combinations(surface):
    data = record_data()
    data["singling_out"]["combinations"] = [["region", "capacity"]]
    with pytest.raises(ExposureError, match="singling-out"):
        expose(RegistryRecord.from_dict(data), surface, client_id="C-0004")


def test_identifying_combination_removed_by_class_does_not_refuse():
    data = record_data()
    data["singling_out"]["combinations"] = [["region", "notes"]]
    assert "notes" not in expose(RegistryRecord.from_dict(data), "newsletter")["fields"]


@pytest.mark.parametrize("review", [None, {"reviewed": False, "combinations": []}])
def test_unreviewed_record_refuses_outward_output(review):
    data = record_data()
    if review is None:
        del data["singling_out"]
    else:
        data["singling_out"] = review
    parsed = RegistryRecord.from_dict(data)
    assert expose(parsed, "internal")
    with pytest.raises(ExposureError):
        expose(parsed, "public_website")


def test_missing_client_recipient_refuses():
    with pytest.raises(ExposureError):
        expose(record(), "client")


def test_unknown_surface_refuses():
    with pytest.raises(ExposureError):
        expose(record(), "unknown")


@pytest.mark.parametrize(
    "value", ["Synthetic Hull Zephyr", {"caption": ["SYNTHETIC HULL ZEPHYR"]}]
)
def test_names_cannot_leak_through_free_text_or_nested_values(value):
    data = record_data()
    data["fields"]["region"]["value"] = value
    with pytest.raises(ExposureError):
        expose(RegistryRecord.from_dict(data), "newsletter")


@pytest.mark.parametrize(
    "mutation",
    [
        lambda d: d["fields"]["region"].update(exposure_class="unknown"),
        lambda d: d["fields"]["region"].pop("exposure_class"),
        lambda d: d["fields"]["name"].pop("codename"),
        lambda d: d["fields"]["name"].update(codename="Synthetic Hull Zephyr"),
        lambda d: d["fields"]["region"].update(kind="unknown"),
        lambda d: d["fields"]["region"].update(value=float("nan")),
        lambda d: d["fields"]["region"].update(value=object()),
        lambda d: d["singling_out"].update(reviewed="true"),
        lambda d: d["singling_out"].update(combinations=[["missing"]]),
        lambda d: d.update(extra="unclassified"),
    ],
)
def test_invalid_records_fail_closed(mutation):
    data = record_data()
    mutation(data)
    with pytest.raises(ExposureError):
        RegistryRecord.from_dict(data)


def test_projection_does_not_mutate_or_share_nested_input():
    data = record_data()
    before = deepcopy(data)
    parsed = RegistryRecord.from_dict(data)
    result = expose(parsed, "client", client_id="C-0004")
    result["fields"]["design"]["draft_m"] = 100
    assert data == before
    assert expose(parsed, "client", client_id="C-0004")["fields"]["design"] == {
        "draft_m": 8.5
    }


def test_json_serializable_output():
    assert json.loads(json.dumps(expose(record(), "newsletter"))) == expose(
        record(), "newsletter"
    )


@pytest.mark.parametrize("field_name", ["credential", "contact"])
@pytest.mark.parametrize("surface", ["client", "newsletter"])
def test_sensitive_values_cannot_leak_through_other_fields(field_name, surface):
    data = record_data()
    data["fields"]["region"]["value"] = data["fields"][field_name]["value"]
    with pytest.raises(ExposureError):
        expose(RegistryRecord.from_dict(data), surface, client_id="C-0004")


def test_unicode_and_separator_variants_cannot_leak():
    data = record_data()
    data["fields"]["region"]["value"] = "Ｓｙｎｔｈｅｔｉｃ-Hull-Zephyr"
    with pytest.raises(ExposureError):
        expose(RegistryRecord.from_dict(data), "newsletter")


def test_direct_constructor_cannot_bypass_validation():
    with pytest.raises(ExposureError):
        expose(RegistryRecord('{"fields":{}}'), "newsletter")


def test_source_mutation_cannot_change_snapshot():
    data = record_data()
    parsed = RegistryRecord.from_dict(data)
    data["fields"]["region"]["value"] = "Synthetic Hull Zephyr"
    assert expose(parsed, "newsletter")["fields"]["region"] == "broad coastal region"
