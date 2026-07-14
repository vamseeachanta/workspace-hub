"""Exact normalized readback checks for the owner protection transaction."""

from __future__ import annotations

from .codec import AuthorityError


def _rule(rules, kind):
    matches = [item for item in rules if item.get("type") == kind]
    if len(matches) != 1:
        raise AuthorityError("integrity")
    return matches[0].get("parameters", {})


def verify_readback(preview, environment, ruleset):
    expected_environment = preview["environment"]
    expected_ruleset = preview["ruleset"]
    reviewers = [
        item.get("reviewer", {}).get("login")
        for rule in environment.get("protection_rules", [])
        if rule.get("type") == "required_reviewers"
        for item in rule.get("reviewers", [])
    ]
    deployment = environment.get("deployment_branch_policy", {})
    pull = _rule(ruleset.get("rules", []), "pull_request")
    checks = _rule(ruleset.get("rules", []), "required_status_checks").get(
        "required_status_checks", []
    )
    workflows = _rule(ruleset.get("rules", []), "required_workflows").get(
        "workflows", []
    )
    update = _rule(ruleset.get("rules", []), "update")
    valid = (
        environment.get("name") == expected_environment["name"]
        and reviewers == ["vamseeachanta"]
        and deployment == {"protected_branches": True, "custom_branch_policies": False}
        and ruleset.get("name") == expected_ruleset["name"]
        and ruleset.get("target") == "branch"
        and ruleset.get("enforcement") == "active"
        and ruleset.get("bypass_actors") == []
        and ruleset.get("conditions")
        == {"ref_name": {"include": [expected_ruleset["target"]], "exclude": []}}
        and pull.get("required_approving_review_count")
        == expected_ruleset["required_approving_review_count"]
        and pull.get("require_code_owner_review")
        is expected_ruleset["require_code_owner_review"]
        and checks
        == [
            {
                "context": expected_ruleset["required_check"],
                "integration_id": expected_ruleset["required_integration"],
            }
        ]
        and workflows == [expected_ruleset["required_workflow"]]
        and update.get("allows_direct_updates") is False
    )
    if not valid:
        raise AuthorityError("integrity")
    return True
