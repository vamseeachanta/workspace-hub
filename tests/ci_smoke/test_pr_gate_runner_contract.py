"""Offline routing and security contracts for the two configurable workflows."""

import ast
import json
import re
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = {
    "baseline-check.yml": {
        "test": "Run Tests", "lint": "Code Quality", "governance": "Governance Checks",
    },
    "domain-matrix.yml": {
        "discover": "Discover domains", "test-domain": "Domain ${{ matrix.name }}",
        "aggregate": "Aggregate domain results",
    },
}
LABELS = ["self-hosted", "Linux", "ARM64"]


def evaluate(expression, context):
    """Evaluate only the boolean/comparison/literal JSON routing subset.

    GitHub string equality is case insensitive. Missing context properties are
    empty strings, and boolean operators return the selected operand.
    """
    assert expression.startswith("${{") and expression.endswith("}}")
    source = expression[3:-2].strip().replace("&&", " and ").replace("||", " or ")
    tree = ast.parse(source, mode="eval")

    def visit(node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, (ast.Attribute, ast.Name)):
            return context.get(ast.unparse(node), "")
        if isinstance(node, ast.BoolOp):
            result = visit(node.values[0])
            for value in node.values[1:]:
                if isinstance(node.op, ast.And) and not result:
                    return result
                if isinstance(node.op, ast.Or) and result:
                    return result
                result = visit(value)
            return result
        if isinstance(node, ast.Compare):
            assert len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq)
            return visit(node.left).casefold() == visit(node.comparators[0]).casefold()
        if isinstance(node, ast.Call):
            assert isinstance(node.func, ast.Name) and node.func.id == "fromJSON"
            assert len(node.args) == 1 and not node.keywords
            assert isinstance(node.args[0], ast.Constant), "JSON must be a fixed literal"
            return json.loads(visit(node.args[0]))
        raise AssertionError(f"Unsupported routing syntax: {ast.dump(node)}")

    return visit(tree.body)


@pytest.fixture(params=WORKFLOWS)
def workflow(request):
    path = ROOT / ".github/workflows" / request.param
    return request.param, yaml.safe_load(path.read_text())


@pytest.mark.parametrize("token", [None, "", "unknown", '"other-runner"', '["self-hosted"]', "self-hosted-arm64"])
@pytest.mark.parametrize("event,head,draft,eligible", [
    ("pull_request", "example/repository", False, True),
    ("pull_request", "example/repository", True, True),
    ("pull_request", "example/fork", False, False),
    ("pull_request", "example/fork", True, False),
    ("pull_request", "", False, False),
    ("push", "", False, True),
    ("workflow_dispatch", "", False, True),
    ("pull_request_target", "example/repository", False, False),
    ("schedule", "", False, False),
    ("workflow_call", "", False, False),
])
def test_runner_selection(workflow, token, event, head, draft, eligible):
    _, document = workflow
    context = {
        "github.event_name": event,
        "github.repository": "example/repository",
        "github.event.pull_request.head.repo.full_name": head,
        "github.event.pull_request.draft": draft,
    }
    if token is not None:
        context["vars.PR_GATE_RUNNER"] = token
    expected = LABELS if eligible and token == "self-hosted-arm64" else "ubuntu-latest"
    for job in document["jobs"].values():
        assert evaluate(job["runs-on"], context) == expected


def test_gates_and_checkout_security(workflow):
    filename, document = workflow
    assert document["permissions"] == {"contents": "read"}
    assert {key: job["name"] for key, job in document["jobs"].items()} == WORKFLOWS[filename]
    for key, job in document["jobs"].items():
        assert job.get("if") == ("always()" if key == "aggregate" else None)
        for step in job["steps"]:
            assert "draft" not in str(step.get("if", "")).lower()
            if step.get("uses", "").startswith("actions/checkout@"):
                assert step["with"]["persist-credentials"] is False
    text = (ROOT / ".github/workflows" / filename).read_text()
    assert re.search(r"^#.*PR_GATE_RUNNER.*self-hosted-arm64", text, re.MULTILINE)
