from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: str):
    with (ROOT / path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def test_email_queue_state_schema_defines_required_sections():
    schema = load_yaml("docs/design/email-queue-state-schema.yaml")

    assert schema["version"] == 1
    assert set(schema["schemas"]) >= {
        "queue_state_entry",
        "queue_learning_log_entry",
        "queue_state_snapshot",
        "queue_state_snapshot_meta",
    }

    state_required = set(schema["schemas"]["queue_state_entry"]["required"])
    assert {
        "account_id",
        "thread_id",
        "from_state",
        "to_state",
        "ts_utc",
        "writer_identity",
    } <= state_required

    writer_required = set(
        schema["schemas"]["queue_state_entry"]["properties"]["writer_identity"][
            "required"
        ]
    )
    assert {"process_name", "pid", "hostname", "boot_id"} <= writer_required


def test_snapshot_schema_uses_account_thread_composite_key():
    schema = load_yaml("docs/design/email-queue-state-schema.yaml")
    snapshot = schema["schemas"]["queue_state_snapshot"]

    assert snapshot["type"] == "object"
    assert snapshot["additionalProperties"]["required"][:2] == [
        "account_id",
        "thread_id",
    ]
    assert snapshot["key_format"] == "{account_id}::{thread_id}"


def test_spam_rules_yaml_contains_letstok_contract():
    rules = load_yaml("scripts/email/spam-detection-rules.yaml")
    rule_by_id = {rule["id"]: rule for rule in rules["rules"]}

    letstok = rule_by_id["letstok_web_form_abuse"]
    assert letstok["classification"] == "spam"
    assert letstok["action_for_unmapped_sender"] == "DELETE"
    assert letstok["state_tracking"] == "skip"
    assert "fatigue analysis" in " ".join(letstok["contains_any"]).lower()
    assert "offshore engineering" in " ".join(letstok["contains_any"]).lower()


def test_cre_listing_schema_covers_required_fields_and_senders():
    schema = load_yaml("scripts/email/extraction-schemas/cre-listing-v1.yaml")

    assert schema["schema_id"] == "cre-listing-v1"
    assert schema["target_path"] == "assethold/data/cre-listings"
    assert {
        "sandsig.com",
        "marcusmillichap.com",
        "partnersrealestate.com",
        "email.loopnet.com",
        "ten-x.ccsend.com",
        "c.costarmail.com",
    } <= set(schema["sender_domains"])

    fields = {field["name"] for field in schema["fields"]}
    assert {
        "property_type",
        "price",
        "cap_rate",
        "square_feet",
        "location",
        "sender",
    } <= fields


def test_routing_yaml_sandsig_and_skylineseven_route_to_cre_data():
    routing = load_yaml("scripts/email/email-routing.yaml")

    assert routing["rules"]["sandsig.com"] == "assethold/data/cre-listings"
    assert routing["rules"]["skylineseven.ccsend.com"] == (
        "assethold/data/cre-listings"
    )

