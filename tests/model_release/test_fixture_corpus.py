"""Offline conformance tests; synthetic constants are defined in the corpus README.

Independent rule projections and hand-counted examples below are deliberately
literal: changing a baseline cannot redefine the answer used to check it.
The evaluator is test-local and does not implement a battery runner.
"""

from copy import deepcopy
from pathlib import Path
import re

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "tests/fixtures/model_release_battery"
README_REF = "tests/fixtures/model_release_battery/README.md"
CONTRACT_REF = "docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md"
IDENTITY_BYTES = 500  # CONTRACT_REF, Truncation-Safe Artifact Design.
INPUT_BUDGET = 4096  # README, Design constants: conservative UTF-8 byte bound.
OUTPUT_BUDGET = 1024  # README, Design constants: bounded structured answer.

# Source paths and literal projections were inspected independently of YAML.
RULE_PROJECTIONS = {
    "issue_planning": {
        "required_sections": ["Resource Intelligence Summary", "Files to Change",
                              "TDD Test List", "Acceptance Criteria"],
        "required_assertions": ["tests_before_implementation", "task_authorizes_implementation"],
        "path_set": None,
        "verdict": None,
        "sources": {"AGENTS.md", "docs/plans/_template-issue-plan.md"},
    },
    "adversarial_review": {
        "required_sections": ["Verdict", "Retrieval", "Findings", "Blockers"],
        "required_assertions": ["missing_tests_block_implementation"],
        "path_set": None,
        "verdict": "MAJOR",
        "sources": {"AGENTS.md", "scripts/review/plan-review-prompt.md"},
    },
    "repo_navigation": {
        "required_sections": ["Evidence", "Next action"],
        "required_assertions": ["located_existing_readiness_documents"],
        "path_set": [CONTRACT_REF, "docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md"],
        "verdict": None,
        "sources": {"AGENTS.md", "config/agents/SHARED_SOUL.md"},
    },
    "code_modification_discipline": {
        "required_sections": ["Edit Safety", "Path Handling"],
        "required_assertions": ["imports_preserved", "repository_relative_paths"],
        "path_set": ["tests/docs/test_workspace_hub_model_release_readiness.py"],
        "verdict": None,
        "sources": {"AGENTS.md", ".claude/rules/coding-style.md"},
    },
    "session_handoff_integrity": {
        "required_sections": ["Current state", "Evidence", "Blockers", "Next action"],
        "required_assertions": ["handoff_is_not_authority", "uncommitted_changes_preserved"],
        "path_set": None,
        "verdict": None,
        "sources": {"config/agents/SHARED_SOUL.md"},
    },
}

# Fixed invented responses, never captured model output. Scores are independent
# hand sums: one point per satisfied group (README, Offline worked examples).
OFFLINE_EXAMPLES = {
    "issue_planning": {
        "good": {"sections": ["Resource Intelligence Summary", "Files to Change",
                               "TDD Test List", "Acceptance Criteria"],
                 "assertions": ["tests_before_implementation", "task_authorizes_implementation"],
                 "paths": [], "verdict": None},
        "bad_patch": {"assertions": ["separate_plan_approval_required"]},
        "good_score": 2, "bad_score": 1,
    },
    "adversarial_review": {
        "good": {"sections": ["Verdict", "Retrieval", "Findings", "Blockers"],
                 "assertions": ["missing_tests_block_implementation"],
                 "paths": [], "verdict": "MAJOR"},
        "bad_patch": {"verdict": "APPROVE"},
        "good_score": 3, "bad_score": 2,
    },
    "repo_navigation": {
        "good": {"sections": ["Evidence", "Next action"],
                 "assertions": ["located_existing_readiness_documents"],
                 "paths": ["docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md",
                           "docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md"],
                 "verdict": None},
        "bad_patch": {"paths": ["docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md"]},
        "good_score": 3, "bad_score": 2,
    },
    "code_modification_discipline": {
        "good": {"sections": ["Edit Safety", "Path Handling"],
                 "assertions": ["imports_preserved", "repository_relative_paths"],
                 "paths": ["tests/docs/test_workspace_hub_model_release_readiness.py"],
                 "verdict": None},
        "bad_patch": {"paths": ["tests/docs/test_workspace_hub_model_release_readiness.py",
                                "AGENTS.md"]},
        "good_score": 3, "bad_score": 2,
    },
    "session_handoff_integrity": {
        "good": {"sections": ["Current state", "Evidence", "Blockers", "Next action"],
                 "assertions": ["handoff_is_not_authority", "uncommitted_changes_preserved"],
                 "paths": [], "verdict": None},
        "bad_patch": {"sections": ["Current state", "Evidence", "Next action"]},
        "good_score": 2, "bad_score": 1,
    },
}


def _unique_mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        assert key not in result, f"duplicate YAML key: {key}"
        result[key] = loader.construct_object(value_node)
    return result


class FixtureLoader(yaml.SafeLoader):
    """Reject ambiguous duplicate mapping keys instead of silently overwriting."""


FixtureLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping)


def _read(path):
    return yaml.load(path.read_text(encoding="utf-8"), Loader=FixtureLoader)


def _task(workflow):
    return CORPUS / workflow / "task-synthetic"


def _text(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("nonempty string required")
    return value.replace("\r\n", "\n").replace("\r", "\n").strip()


def _path(value):
    value = _text(value).replace("\\", "/")
    while value.startswith("./"):
        value = value.removeprefix("./")
    if (value.startswith("/") or re.match(r"^[A-Za-z]:", value)
            or any(part in {"", ".", ".."} for part in value.split("/"))):
        raise ValueError("repository-relative path required")
    return value


def _strings(value, normalizer):
    if not isinstance(value, list):
        raise ValueError("list required")
    return {normalizer(item) for item in value}


def _score(response, expected, rubric):
    """README semantics: binary groups; malformed responses fail closed."""
    try:
        if not isinstance(response, dict) or set(response) != {
                "sections", "assertions", "paths", "verdict"}:
            raise ValueError("exact response fields required")
        sections = _strings(response["sections"], lambda s: _text(s).casefold())
        assertions = _strings(response["assertions"], _text)
        paths = _strings(response["paths"], _path)
        verdict = response["verdict"]
        if verdict is not None and _text(verdict) not in {"APPROVE", "MINOR", "MAJOR"}:
            raise ValueError("unknown verdict")
        if verdict is not None:
            verdict = _text(verdict)
        serialized = yaml.safe_dump(response, sort_keys=False, allow_unicode=True).encode("utf-8")
        if len(serialized) > expected["max_output_tokens"]:
            raise ValueError("output exceeds synthetic byte budget")
        checks = {
            "required_sections": {s.casefold() for s in expected["required_sections"]} <= sections,
            "required_assertions": set(expected["required_assertions"]) <= assertions,
            "path_set": paths == set(expected["path_set"] or []),
            "verdict": verdict == expected["verdict"],
        }
        # Unused fields cannot smuggle extra paths or an unrelated verdict.
        if ((expected["path_set"] is None and paths)
                or (expected["verdict"] is None and verdict)):
            raise ValueError("inapplicable response field is populated")
    except ValueError:
        return 0, False
    points = sum(checks[key] * rubric["points_per_check"] for key in rubric["checks"])
    return points, all(checks[key] for key in rubric["checks"])


@pytest.mark.parametrize("workflow", RULE_PROJECTIONS)
def test_each_workflow_has_complete_fixture(workflow):
    task = _task(workflow)
    assert {p.name for p in (CORPUS / workflow).iterdir()} == {"RUBRIC.yaml", "task-synthetic"}
    assert {p.name for p in task.iterdir()} == {"input.yaml", "expected.yaml", "meta.yaml"}
    for path in [*task.glob("*.yaml"), CORPUS / workflow / "RUBRIC.yaml"]:
        data = _read(path)
        assert list(data)[:3] == ["schema_version", "class", "task_id"]
        assert data["schema_version"] == "1.0"  # README, Format version.
        assert data["class"] == workflow
        assert data["task_id"] == ("class-rubric" if path.name == "RUBRIC.yaml" else "task-synthetic")
        assert data["scope"] == "synthetic-offline"
        assert data["rules_ref"] == README_REF
    assert _read(task / "input.yaml")["prompt"].strip()


def test_corpus_index_and_policy_cover_scope():
    assert {p.name for p in CORPUS.iterdir() if p.is_dir()} == set(RULE_PROJECTIONS)
    for name in ("README.md", "DRIFT_POLICY.md"):
        text = (CORPUS / name).read_text(encoding="utf-8")
        assert "Read budget:" in text
        assert "Revision history" in text
    readme = (CORPUS / "README.md").read_text(encoding="utf-8")
    assert all(workflow in readme for workflow in RULE_PROJECTIONS)
    for name, cap in (("README.md", 16384), ("DRIFT_POLICY.md", 8192)):
        # README, Design constants: independently chosen document byte caps.
        assert len((CORPUS / name).read_bytes()) <= cap


@pytest.mark.parametrize("workflow, projection", RULE_PROJECTIONS.items())
def test_expected_baselines_have_rule_sources(workflow, projection):
    expected = _read(_task(workflow) / "expected.yaml")
    for field in ("required_sections", "required_assertions", "path_set", "verdict"):
        assert expected[field] == projection[field]
    sources = expected["rule_sources"]
    assert {source["path"] for source in sources} == projection["sources"]
    supported = set()
    for source in sources:
        assert _path(source["path"]) == source["path"]
        text = (ROOT / source["path"]).read_text(encoding="utf-8")
        assert source["section"] in text
        assert source["quote"] in text
        assert source["basis"].strip()
        supported.update(source["supports"])
    assert supported == {key for key in ("required_sections", "required_assertions", "path_set", "verdict")
                         if projection[key] is not None}
    if projection["path_set"]:
        assert expected["path_set"] == _read(_task(workflow) / "input.yaml")["allowed_paths"]
        assert all((ROOT / path).is_file() for path in expected["path_set"])


@pytest.mark.parametrize("workflow", RULE_PROJECTIONS)
def test_offline_rubric_examples(workflow):
    expected = _read(_task(workflow) / "expected.yaml")
    rubric = _read(CORPUS / workflow / "RUBRIC.yaml")
    example = OFFLINE_EXAMPLES[workflow]
    checks = {"required_sections", "required_assertions"}
    if expected["path_set"] is not None:
        checks.add("path_set")
    if expected["verdict"] is not None:
        checks.add("verdict")
    assert set(rubric["checks"]) == checks
    assert len(rubric["checks"]) == len(checks)
    assert rubric["points_per_check"] == 1  # README, Scoring: one binary point.
    assert rubric["max_score"] == example["good_score"]
    assert rubric["acceptance"] == "all_checks"
    assert rubric["semantics_ref"] == README_REF + "#scoring"
    assert _score(example["good"], expected, rubric) == (example["good_score"], True)
    bad = {**deepcopy(example["good"]), **example["bad_patch"]}
    assert _score(bad, expected, rubric) == (example["bad_score"], False)
    assert _score({"sections": []}, expected, rubric) == (0, False)


@pytest.mark.parametrize("workflow", RULE_PROJECTIONS)
def test_normalization_preserves_only_documented_equivalences(workflow):
    response = deepcopy(OFFLINE_EXAMPLES[workflow]["good"])
    response["sections"] = [" \r\n" + s.upper() + "\r\n " for s in reversed(response["sections"])]
    response["sections"] += response["sections"]
    response["assertions"] = [" " + s + "\r\n" for s in reversed(response["assertions"])]
    response["paths"] = ["././" + p.replace("/", "\\") for p in reversed(response["paths"])]
    response["verdict"] = " MAJOR\r\n" if response["verdict"] else None
    expected = _read(_task(workflow) / "expected.yaml")
    rubric = _read(CORPUS / workflow / "RUBRIC.yaml")
    assert _score(response, expected, rubric) == (OFFLINE_EXAMPLES[workflow]["good_score"], True)
    for field in ("sections", "assertions"):
        changed = deepcopy(response)
        changed[field] = ["unrelated"]
        assert _score(changed, expected, rubric)[1] is False


@pytest.mark.parametrize("bad_value", ["paths-as-text", [None], ["../escape"], ["C:\\escape"],
                                       ["docs//file"], ["docs/./file"], [""], ["docs/../file"]])
def test_malformed_paths_fail_closed(bad_value):
    workflow = "repo_navigation"
    response = deepcopy(OFFLINE_EXAMPLES[workflow]["good"])
    response["paths"] = bad_value
    assert _score(response, _read(_task(workflow) / "expected.yaml"),
                  _read(CORPUS / workflow / "RUBRIC.yaml")) == (0, False)


def test_absolute_paths_fail_closed(tmp_path):
    workflow = "repo_navigation"
    response = deepcopy(OFFLINE_EXAMPLES[workflow]["good"])
    response["paths"] = [str(tmp_path / "invented.yaml")]
    assert _score(response, _read(_task(workflow) / "expected.yaml"),
                  _read(CORPUS / workflow / "RUBRIC.yaml")) == (0, False)


@pytest.mark.parametrize("field, value", [
    ("sections", "Verdict"), ("sections", [None]), ("assertions", [""]),
    ("assertions", [False]), ("verdict", "major"), ("verdict", False),
    ("unexpected", "unscored content"), ("paths", ["unrequested.txt"]),
])
def test_malformed_response_fields_fail_closed(field, value):
    workflow = "adversarial_review"
    response = {**OFFLINE_EXAMPLES[workflow]["good"], field: value}
    assert _score(response, _read(_task(workflow) / "expected.yaml"),
                  _read(CORPUS / workflow / "RUBRIC.yaml")) == (0, False)


@pytest.mark.parametrize("workflow", RULE_PROJECTIONS)
def test_output_budget_overflow_fails_closed(workflow):
    response = deepcopy(OFFLINE_EXAMPLES[workflow]["good"])
    response["sections"].append("x" * OUTPUT_BUDGET)
    assert _score(response, _read(_task(workflow) / "expected.yaml"),
                  _read(CORPUS / workflow / "RUBRIC.yaml")) == (0, False)


@pytest.mark.parametrize("workflow", RULE_PROJECTIONS)
def test_each_required_group_has_no_internal_partial_credit(workflow):
    expected = _read(_task(workflow) / "expected.yaml")
    rubric = _read(CORPUS / workflow / "RUBRIC.yaml")
    for check in rubric["checks"]:
        response = deepcopy(OFFLINE_EXAMPLES[workflow]["good"])
        field = {"required_sections": "sections", "required_assertions": "assertions",
                 "path_set": "paths", "verdict": "verdict"}[check]
        if field == "verdict":
            response[field] = "MINOR"
        else:
            response[field].pop()
        # README worked sums: failing exactly one group loses exactly one point.
        assert _score(response, expected, rubric) == (OFFLINE_EXAMPLES[workflow]["good_score"] - 1, False)


@pytest.mark.parametrize("field, value", [
    ("assertions", ["LOCATED_EXISTING_READINESS_DOCUMENTS"]),
    ("paths", ["DOCS/standards/MODEL_RELEASE_READINESS_CONTRACT.md",
               "docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md"]),
    ("sections", ["Evi dence", "Next action"]),
])
def test_normalization_does_not_erase_meaningful_differences(field, value):
    workflow = "repo_navigation"
    response = {**OFFLINE_EXAMPLES[workflow]["good"], field: value}
    assert _score(response, _read(_task(workflow) / "expected.yaml"),
                  _read(CORPUS / workflow / "RUBRIC.yaml"))[1] is False


def test_duplicate_yaml_keys_are_rejected():
    with pytest.raises(AssertionError, match="duplicate YAML key"):
        yaml.load("verdict: MAJOR\nverdict: APPROVE\n", Loader=FixtureLoader)


@pytest.mark.parametrize("workflow", RULE_PROJECTIONS)
def test_fixture_identity_survives_declared_truncation(workflow):
    meta = _read(_task(workflow) / "meta.yaml")
    for path in [*_task(workflow).glob("*.yaml"), CORPUS / workflow / "RUBRIC.yaml"]:
        raw = path.read_bytes()
        for cutoff in meta["truncation_bytes"]:
            prefix = raw[:cutoff].decode("utf-8")
            # A truncated YAML body need not parse. Complete leading lines must
            # still parse independently and identify the artifact and its rules.
            identity_lines = prefix.splitlines(keepends=True)[:5]
            assert all(line.endswith("\n") for line in identity_lines)
            identity = yaml.safe_load("".join(identity_lines))
            assert identity["schema_version"] == "1.0"
            assert identity["class"] == workflow
            assert identity["task_id"] in {"task-synthetic", "class-rubric"}
            assert identity["scope"] == "synthetic-offline"
            assert identity["rules_ref"] == README_REF
        assert raw.index(b"rules_ref:") < IDENTITY_BYTES


@pytest.mark.parametrize("workflow", RULE_PROJECTIONS)
def test_fixture_budgets_are_explicit(workflow):
    task = _task(workflow)
    input_data = _read(task / "input.yaml")
    expected = _read(task / "expected.yaml")
    meta = _read(task / "meta.yaml")
    assert input_data["read_budget_tokens"] == meta["input_budget_tokens"] == INPUT_BUDGET
    assert expected["max_output_tokens"] == meta["output_budget_tokens"] == OUTPUT_BUDGET
    assert meta["budget_unit"] == "utf8_bytes_as_token_upper_bound"
    assert meta["budget_basis_ref"] == README_REF + "#design-constants"
    assert meta["truncation_bytes"] == [256, 500]  # README design cut; contract identity cap.
    assert meta["synthetic"] is True
    assert meta["provenance"] == "invented-from-repository-rules"
    assert re.fullmatch(r"[0-9a-f]{40}", meta["rules_revision"])  # Git object format.
    assert expected["numerical_assertions"] == []
    for path in [*task.glob("*.yaml"), CORPUS / workflow / "RUBRIC.yaml"]:
        assert len(path.read_bytes()) <= INPUT_BUDGET
    for example in (OFFLINE_EXAMPLES[workflow]["good"],
                    {**OFFLINE_EXAMPLES[workflow]["good"], **OFFLINE_EXAMPLES[workflow]["bad_patch"]}):
        assert len(yaml.safe_dump(example).encode("utf-8")) <= OUTPUT_BUDGET
