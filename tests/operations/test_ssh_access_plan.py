"""Offline decision tests; expected outcomes follow hand-applied Boolean rules.

Basis: docs/ops/compute-ssh-access.md, Evidence method. All required true means
PASS; any false means FAIL; otherwise NOT_EVALUATED. Preference is an ordered
policy, not a numeric score. Synthetic evidence never establishes live access.
"""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "ssh_access_plan", ROOT / "scripts/operations/connection/ssh_access_plan.py"
)
plan = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(plan)

# Independent list from the runbook's evidence table, deliberately not imported.
COMMON = (
    "private_only", "key_only", "password_disabled", "interactive_disabled",
    "root_disabled", "host_key_verified", "least_privilege", "recovery_verified",
    "headless_provisioning", "job_survives_disconnect", "ssh_data_transfer",
    "post_reboot",
)
EXTRA = {
    "tailscale_openssh": ("device_controls", "manual_profile_independent"),
    "tailscale_subnet_openssh": (
        "device_controls", "subnet_route_verified", "manual_profile_independent",
    ),
    "lan_openssh": ("routed_private_path", "manual_profile_independent"),
    "cloudflare_openssh": ("unattended_policy", "manual_profile_independent"),
    "managed_wireguard": ("reconnect_verified",),
}


def proven(candidate):
    return dict.fromkeys((*COMMON, *EXTRA[candidate]), True)


def test_empty_evidence_does_not_select_a_path():
    """Hand: no true proofs -> unknown for each option -> no selection."""
    result = plan.assess({})
    assert result["status"] == "NOT_EVALUATED"
    assert result["selected"] is None
    assert all(r["status"] == "NOT_EVALUATED" for r in result["options"].values())
    assert result["manual_profile_independent"] is None


@pytest.mark.parametrize("candidate", EXTRA)
def test_complete_evidence_selects_only_proven_candidate(candidate):
    """Hand: each required proposition true -> the sole eligible option wins."""
    result = plan.assess({candidate: proven(candidate)})
    assert result["selected"] == candidate
    assert result["status"] == "PASS"
    assert result["manual_profile_independent"] is (candidate != "managed_wireguard")


@pytest.mark.parametrize("candidate", tuple(EXTRA)[:-1])
def test_alternative_must_prove_independence_from_old_profile(candidate):
    """Hand: an alternative still using the old profile cannot solve dependence."""
    evidence = proven(candidate)
    evidence["manual_profile_independent"] = False
    result = plan.assess({candidate: evidence})
    assert result["selected"] is None
    assert result["options"][candidate]["failed"] == ["manual_profile_independent"]


@pytest.mark.parametrize("field", COMMON)
@pytest.mark.parametrize("value,status", [(False, "FAIL"), (None, "NOT_EVALUATED")])
def test_each_common_requirement_gates_selection(field, value, status):
    """Hand: a false or unknown conjunct prevents all-true qualification."""
    evidence = proven("tailscale_openssh")
    evidence[field] = value
    result = plan.assess({"tailscale_openssh": evidence})
    option = result["options"]["tailscale_openssh"]
    assert option["status"] == status
    assert field in option["failed" if value is False else "missing"]
    assert result["selected"] is None


@pytest.mark.parametrize("candidate,fields", EXTRA.items())
def test_transport_specific_requirements_are_not_optional(candidate, fields):
    """Hand: removing the transport proof leaves one unknown conjunct."""
    evidence = proven(candidate)
    for field in fields:
        del evidence[field]
    result = plan.assess({candidate: evidence})
    assert result["selected"] is None
    assert result["options"][candidate]["missing"] == list(fields)


def test_failure_takes_precedence_over_unknown_and_other_options_remain_eligible():
    evidence = {"key_only": False}
    result = plan.assess({"tailscale_openssh": evidence, "lan_openssh": proven("lan_openssh")})
    assert result["options"]["tailscale_openssh"]["status"] == "FAIL"
    assert result["selected"] == "lan_openssh"


def test_policy_preference_and_interim_fallback():
    """Hand: first all-true private alternative wins over the interim option."""
    all_proven = {candidate: proven(candidate) for candidate in EXTRA}
    assert plan.assess(all_proven)["selected"] == "tailscale_openssh"
    del all_proven["tailscale_openssh"]
    assert plan.assess(all_proven)["selected"] == "tailscale_subnet_openssh"
    del all_proven["tailscale_subnet_openssh"]
    assert plan.assess(all_proven)["selected"] == "lan_openssh"
    del all_proven["lan_openssh"]
    assert plan.assess(all_proven)["selected"] == "cloudflare_openssh"
    del all_proven["cloudflare_openssh"]
    assert plan.assess(all_proven)["selected"] == "managed_wireguard"


@pytest.mark.parametrize("evidence", [
    [], None, {"public_ssh": {}}, {"tailscale_ssh": {}},
    {"tailscale_openssh": []}, {"tailscale_openssh": {"unknown": True}},
    {"tailscale_openssh": {"key_only": 1}},
    {"tailscale_openssh": {"key_only": "true"}},
    {"tailscale_openssh": {"key_only": {}}},
])
def test_invalid_evidence_is_rejected(evidence):
    with pytest.raises(ValueError):
        plan.assess(evidence)


@pytest.mark.parametrize("raw", [
    '{"tailscale_openssh": {}, "tailscale_openssh": {}}',
    '{"tailscale_openssh": {"key_only": true, "key_only": false}}',
    '{"tailscale_openssh": {"key_only": NaN}}',
    '{"tailscale_openssh": {"key_only": Infinity}}',
    '{"tailscale_openssh": {"key_only": 1.0}}',
    'invalid',
])
def test_cli_invalid_input_is_redacted(tmp_path, capsys, raw):
    source = tmp_path / "private-evidence.json"
    source.write_text(raw)
    assert plan.main([str(source)]) != 0
    output = capsys.readouterr()
    assert output.out == ""
    assert output.err == "Invalid evidence; expected the documented Boolean schema.\n"
    assert str(source) not in output.err


def test_cli_missing_file_is_redacted(tmp_path, capsys):
    assert plan.main([str(tmp_path / "absent")]) != 0
    assert capsys.readouterr().err == "Evidence could not be read.\n"


def test_cli_unknown_is_valid_assessment_not_successful_connectivity(tmp_path, capsys):
    source = tmp_path / "evidence.json"
    source.write_text("{}")
    assert plan.main([str(source)]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "NOT_EVALUATED"


def test_worked_example_matches_hand_calculation():
    """Hand: true key_only, false post_reboot, all other fields unknown -> FAIL.

    Other options have no proofs -> NOT_EVALUATED. Therefore none is selected.
    """
    text = (ROOT / "docs/ops/compute-ssh-access.md").read_text()
    raw = text.split("```json\n", 1)[1].split("```", 1)[0]
    result = plan.assess(json.loads(raw))
    assert result["selected"] is None
    assert result["status"] == "NOT_EVALUATED"
    assert result["options"]["tailscale_openssh"]["failed"] == ["post_reboot"]
    assert result["options"]["tailscale_openssh"]["status"] == "FAIL"
