"""Exact normalized readback checks for the owner protection transaction."""

from __future__ import annotations

from .codec import AuthorityError


def _rule(rules, kind):
    matches = [item for item in rules if item.get("type") == kind]
    if len(matches) != 1:
        raise AuthorityError("integrity")
    return matches[0]


def _parameters(rules, kind):
    rule = _rule(rules, kind)
    parameters = rule.get("parameters")
    if not isinstance(parameters, dict):
        raise AuthorityError("integrity")
    return parameters


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
    rules = ruleset.get("rules", [])
    pull = _parameters(rules, "pull_request")
    checks = _parameters(rules, "required_status_checks").get(
        "required_status_checks", []
    )
    workflow_rule = _rule(rules, "required_workflows")
    if "parameters" in workflow_rule:
        raise AuthorityError("integrity")
    workflows = workflow_rule.get("workflows", [])
    update = _parameters(rules, "update")
    integration_id = expected_ruleset["required_integration_id"]
    workflow = expected_ruleset["required_workflow"]
    if (
        not isinstance(integration_id, int)
        or isinstance(integration_id, bool)
        or not isinstance(workflow.get("repository_id"), int)
        or isinstance(workflow.get("repository_id"), bool)
    ):
        raise AuthorityError("integrity")
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
                "integration_id": integration_id,
            }
        ]
        and workflows == [workflow]
        and update.get("allows_direct_updates") is False
    )
    if not valid:
        raise AuthorityError("integrity")
    return True
