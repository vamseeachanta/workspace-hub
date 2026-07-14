"""Exact normalized readback checks for the owner protection transaction."""

from __future__ import annotations

from .codec import AuthorityError


def _mapping(value):
    if not isinstance(value, dict):
        raise AuthorityError("integrity")
    return value


def _sequence(value):
    if not isinstance(value, list):
        raise AuthorityError("integrity")
    return value


def _rule(rules, kind):
    matches = [
        item
        for item in _sequence(rules)
        if isinstance(item, dict) and item.get("type") == kind
    ]
    if len(matches) != 1:
        raise AuthorityError("integrity")
    return matches[0]


def _parameters(rules, kind):
    return _mapping(_rule(rules, kind).get("parameters"))


def _integer(value):
    if not isinstance(value, int) or isinstance(value, bool):
        raise AuthorityError("integrity")
    return value


def _normalize_environment(value):
    environment = _mapping(value)
    reviewers_rule = _rule(environment.get("protection_rules"), "required_reviewers")
    reviewers = []
    for item in _sequence(reviewers_rule.get("reviewers")):
        reviewer = _mapping(_mapping(item).get("reviewer"))
        login = reviewer.get("login")
        if not isinstance(login, str):
            raise AuthorityError("integrity")
        reviewers.append(login)
    deployment = _mapping(environment.get("deployment_branch_policy"))
    return {
        "deployment_branch_policy": {
            "custom_branch_policies": deployment.get("custom_branch_policies"),
            "protected_branches": deployment.get("protected_branches"),
        },
        "name": environment.get("name"),
        "protection_rules": [
            {
                "reviewers": [{"reviewer": {"login": login}} for login in reviewers],
                "type": "required_reviewers",
            }
        ],
    }


def _normalize_ruleset(value):
    ruleset = _mapping(value)
    rules = ruleset.get("rules")
    pull = _parameters(rules, "pull_request")
    checks = _sequence(
        _parameters(rules, "required_status_checks").get("required_status_checks")
    )
    normalized_checks = []
    for check in checks:
        check = _mapping(check)
        context = check.get("context")
        if not isinstance(context, str):
            raise AuthorityError("integrity")
        normalized_checks.append(
            {
                "context": context,
                "integration_id": _integer(check.get("integration_id")),
            }
        )
    workflow_rule = _rule(rules, "required_workflows")
    if "parameters" in workflow_rule:
        raise AuthorityError("integrity")
    normalized_workflows = []
    for workflow in _sequence(workflow_rule.get("workflows")):
        workflow = _mapping(workflow)
        path = workflow.get("path")
        ref = workflow.get("ref")
        if not isinstance(path, str) or not isinstance(ref, str):
            raise AuthorityError("integrity")
        normalized_workflows.append(
            {
                "path": path,
                "ref": ref,
                "repository_id": _integer(workflow.get("repository_id")),
            }
        )
    update = _parameters(rules, "update")
    return {
        "bypass_actors": ruleset.get("bypass_actors"),
        "conditions": ruleset.get("conditions"),
        "enforcement": ruleset.get("enforcement"),
        "name": ruleset.get("name"),
        "rules": [
            {
                "parameters": {
                    "require_code_owner_review": pull.get("require_code_owner_review"),
                    "required_approving_review_count": pull.get(
                        "required_approving_review_count"
                    ),
                },
                "type": "pull_request",
            },
            {
                "parameters": {"required_status_checks": normalized_checks},
                "type": "required_status_checks",
            },
            {"type": "required_workflows", "workflows": normalized_workflows},
            {
                "parameters": {
                    "allows_direct_updates": update.get("allows_direct_updates")
                },
                "type": "update",
            },
        ],
        "target": ruleset.get("target"),
    }


def verify_readback(preview, environment, ruleset):
    """Verify normalized API readback against the canonical protection preview."""
    preview = _mapping(preview)
    expected_environment = _normalize_environment(preview.get("environment"))
    expected_ruleset = _normalize_ruleset(preview.get("ruleset"))
    if (
        _normalize_environment(environment) != expected_environment
        or _normalize_ruleset(ruleset) != expected_ruleset
    ):
        raise AuthorityError("integrity")
    return True
