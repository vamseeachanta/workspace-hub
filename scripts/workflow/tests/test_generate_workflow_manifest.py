"""TDD suite for the #3284 ecosystem discovery-manifest generator.

Pure aggregation over per-repo ``docs/registry/workflows.yaml`` files. Tests use
fixture registries + an injected resolver so they never touch real sibling repos.
"""
import json
import sys
from pathlib import Path

import pytest

# scripts/workflow is not a package; import the module by path.
SCRIPTS_WORKFLOW = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_WORKFLOW))

import generate_workflow_manifest as gm  # noqa: E402


# ---- fixtures ------------------------------------------------------------

def _make_repo(base: Path, slug: str, registry_text: str | None = None) -> Path:
    repo = base / slug
    repo.mkdir(parents=True, exist_ok=True)
    (repo / "pyproject.toml").write_text("", encoding="utf-8")  # repo marker
    if registry_text is not None:
        regdir = repo / "docs" / "registry"
        regdir.mkdir(parents=True, exist_ok=True)
        (regdir / "workflows.yaml").write_text(registry_text, encoding="utf-8")
    return repo


def _resolver_for(base: Path):
    def _resolve(slug: str) -> Path:
        return base / slug
    return _resolve


REG_V2 = """\
schema_version: 2
invocation: "uv run python -m repoB {input}"
workflows:
  - id: alpha
    version: 1
    status: stable
    latest: true
    basename: alpha
    input: examples/alpha/input.yml
    outputs: [out.json]
    runtime: offline
  - id: alpha
    version: 2
    status: experimental
    basename: alpha
    input: examples/alpha/input2.yml
    runtime: offline
"""

REG_V1 = """\
schema_version: 1
workflows:
  - id: gamma
    basename: gamma
    input: examples/gamma/input.yml
    runtime: fast
    test: tests/test_gamma.py::test_it
"""


# ---- aggregation ---------------------------------------------------------

def test_aggregates_two_repos(tmp_path):
    base = tmp_path
    _make_repo(base, "repoA", REG_V1)
    _make_repo(base, "repoB", REG_V2)
    m = gm.build_manifest(slugs=["repoA", "repoB"], resolve=_resolver_for(base))
    assert m["workflow_count"] == 3  # 1 from repoA + 2 from repoB
    repos = {r["repo"] for r in m["repos"]}
    assert repos == {"repoA", "repoB"}


def test_workflow_id_is_repo_id_version():
    reg = {"invocation": "x {input}"}
    row = {"id": "foo", "version": 3, "input": "i.yml"}
    e = gm.normalize_row("repoA", reg, row)
    assert e["workflow_id"] == "repoA:foo@3"
    assert e["routing_id"] == "repoA:foo"


def test_unversioned_row_is_v1():
    e = gm.normalize_row("repoA", {}, {"id": "foo", "input": "i.yml"})
    assert e["version"] == 1
    assert e["workflow_id"].endswith("@1")


def test_duplicate_id_versions_both_kept(tmp_path):
    base = tmp_path
    _make_repo(base, "repoB", REG_V2)
    m = gm.build_manifest(slugs=["repoB"], resolve=_resolver_for(base))
    ids = sorted(w["workflow_id"] for w in m["workflows"])
    assert ids == ["repoB:alpha@1", "repoB:alpha@2"]
    assert m["latest_by_routing_id"]["repoB:alpha"] == "repoB:alpha@1"  # v1 stable+latest


def test_latest_resolver_highest_stable_when_no_flag():
    workflows = [
        gm.normalize_row("r", {}, {"id": "x", "version": 1, "status": "stable", "input": "a"}),
        gm.normalize_row("r", {}, {"id": "x", "version": 2, "status": "stable", "input": "b"}),
    ]
    latest = gm.latest_by_routing_id(workflows)
    assert latest["r:x"] == "r:x@2"


def test_input_is_preserved():
    e = gm.normalize_row("r", {}, {"id": "x", "input": "examples/x/input.yml"})
    assert e["input"] == "examples/x/input.yml"


def test_license_gated_from_runtime():
    gated = gm.normalize_row("r", {}, {"id": "x", "input": "i", "runtime": "requires-license"})
    off = gm.normalize_row("r", {}, {"id": "y", "input": "i", "runtime": "offline"})
    assert gated["license_gated"] is True
    assert off["license_gated"] is False


def test_network_required_does_not_set_license_gated():
    e = gm.normalize_row("r", {}, {
        "id": "x", "input": "i", "runtime": "offline",
        "data_source": {"network_required": True, "type": "bundled-fixture"},
    })
    assert e["license_gated"] is False
    assert e["data_source"] == {"network_required": True, "type": "bundled-fixture"}


def test_invocation_is_top_level_only():
    reg = {"invocation": "uv run python -m wed {input}"}
    row = {"id": "x", "input": "i", "test": "tests/test_x.py::test_it"}
    e = gm.normalize_row("wed", reg, row)
    assert e["invocation"] == "uv run python -m wed {input}"


def test_invocation_null_and_warning_when_absent(tmp_path):
    base = tmp_path
    _make_repo(base, "repoA", REG_V1)
    m = gm.build_manifest(slugs=["repoA"], resolve=_resolver_for(base))
    e = m["workflows"][0]
    assert e["invocation"] is None
    assert any("repoA" in w and "invocation" in w for w in m["warnings"])


def test_request_response_schema_structured_passthrough():
    absent = gm.normalize_row("r", {}, {"id": "x", "input": "i"})
    assert absent["request_schema"] is None
    assert absent["response_schema"] is None
    present = gm.normalize_row("r", {}, {
        "id": "y", "input": "i",
        "request_schema": {"type": "object", "properties": {"a": {"type": "number"}}},
    })
    assert present["request_schema"] == {"type": "object", "properties": {"a": {"type": "number"}}}


def test_result_descriptor_passthrough():
    with_result = gm.normalize_row("r", {}, {
        "id": "x", "input": "i", "result": {"kind": "files", "outputs": ["a.json"]},
    })
    assert with_result["result"] == {"kind": "files", "outputs": ["a.json"]}
    without = gm.normalize_row("r", {}, {"id": "y", "input": "i"})
    assert without["result"] is None


def test_determinism_field_is_reserved_null():
    a = gm.normalize_row("r", {}, {"id": "x", "input": "i", "assertions": {"k": 1}})
    b = gm.normalize_row("r", {}, {"id": "y", "input": "i"})
    assert a["determinism"] is None
    assert b["determinism"] is None


def test_provenance_registry_hash_and_timestamp(tmp_path):
    import hashlib
    base = tmp_path
    _make_repo(base, "repoB", REG_V2)
    m = gm.build_manifest(slugs=["repoB"], resolve=_resolver_for(base))
    repo_entry = next(r for r in m["repos"] if r["repo"] == "repoB")
    expected = hashlib.sha256(REG_V2.encode("utf-8")).hexdigest()
    assert repo_entry["registry_sha256"] == expected
    assert "T" in m["generated_at"]  # ISO-8601
    assert m["resolver"] == "deckhand/src/deckhand/capability_smoke.py"


def test_missing_registry_is_warning_not_crash(tmp_path):
    base = tmp_path
    _make_repo(base, "repoA", registry_text=None)  # no registry file
    m = gm.build_manifest(slugs=["repoA"], resolve=_resolver_for(base))
    repo_entry = next(r for r in m["repos"] if r["repo"] == "repoA")
    assert repo_entry["status"] == "missing-registry"
    assert any("repoA" in w for w in m["warnings"])
    assert m["workflow_count"] == 0


def test_unparseable_registry_is_warning(tmp_path):
    base = tmp_path
    _make_repo(base, "repoA", "::: not valid yaml :::\n  - [unbalanced")
    _make_repo(base, "repoB", "just a bare scalar string")
    m = gm.build_manifest(slugs=["repoA", "repoB"], resolve=_resolver_for(base))
    statuses = {r["repo"]: r["status"] for r in m["repos"]}
    assert statuses["repoA"] == "unparseable-registry"
    assert statuses["repoB"] == "unparseable-registry"


def test_check_detects_stale_registry(tmp_path):
    base = tmp_path
    _make_repo(base, "repoB", REG_V2)
    manifest_path = tmp_path / "manifest.json"
    gm.write_manifest(manifest_path, slugs=["repoB"], resolve=_resolver_for(base))
    # mutate the registry
    (base / "repoB" / "docs" / "registry" / "workflows.yaml").write_text(
        REG_V2 + "\n  - id: delta\n    input: i\n    runtime: offline\n", encoding="utf-8"
    )
    rc = gm.check_stale(manifest_path, slugs=["repoB"], resolve=_resolver_for(base))
    assert rc == 1


def test_check_clean_returns_zero(tmp_path):
    base = tmp_path
    _make_repo(base, "repoB", REG_V2)
    manifest_path = tmp_path / "manifest.json"
    gm.write_manifest(manifest_path, slugs=["repoB"], resolve=_resolver_for(base))
    rc = gm.check_stale(manifest_path, slugs=["repoB"], resolve=_resolver_for(base))
    assert rc == 0


def test_output_is_deterministic_sorted(tmp_path):
    base = tmp_path
    _make_repo(base, "repoA", REG_V1)
    _make_repo(base, "repoB", REG_V2)
    m1 = gm.build_manifest(slugs=["repoA", "repoB"], resolve=_resolver_for(base))
    m2 = gm.build_manifest(slugs=["repoB", "repoA"], resolve=_resolver_for(base))
    ids = [w["workflow_id"] for w in m1["workflows"]]
    assert ids == sorted(ids)
    assert json.dumps(m1["workflows"]) == json.dumps(m2["workflows"])  # order-independent of slug order


@pytest.fixture
def saved_manifest(tmp_path):
    """Synthetic registry: one stable row plus one experimental row (REG_V2)."""
    _make_repo(tmp_path, "repoB", REG_V2)
    path = tmp_path / "manifest.json"
    resolve = _resolver_for(tmp_path)
    gm.write_manifest(path, slugs=["repoB"], resolve=resolve)
    return path, resolve


def _rewrite_manifest(path, edit):
    saved = json.loads(path.read_text(encoding="utf-8"))
    edit(saved)
    path.write_text(json.dumps(saved), encoding="utf-8")


@pytest.mark.parametrize("field,value", [
    ("input", "examples/replaced.yml"),
    ("invocation", "unexpected {input}"),
    ("request_schema", {"type": "string"}),
    ("response_schema", {"type": "number"}),
    ("license_gated", True),
    ("version", True),
    ("determinism", {"reproducible": True}),
])
def test_check_rejects_changed_payload_with_unchanged_hash(saved_manifest, field, value):
    """Independent oracle: altered discovery data cannot equal its registry row."""
    path, resolve = saved_manifest
    _rewrite_manifest(path, lambda saved: saved["workflows"][0].update({field: value}))
    assert gm.check_stale(path, slugs=["repoB"], resolve=resolve) == 1


@pytest.mark.parametrize("field,value", [
    ("latest_by_routing_id", {"repoB:alpha": "repoB:alpha@2"}),
    ("workflow_count", 99),
    ("manifest_version", True),
    ("generator", "other.py"),
    ("resolver", "other.py"),
    ("warnings", []),
])
def test_check_rejects_changed_metadata(saved_manifest, field, value):
    """Routing must select stable alpha@1, and count must be 1 + 1 = 2.

    Other expected metadata is fixed by the manifest schema. The warnings case
    is made different explicitly because REG_V2 normally has no warnings.
    """
    path, resolve = saved_manifest
    if field == "warnings":
        value = ["unexpected warning"]
    _rewrite_manifest(path, lambda saved: saved.update({field: value}))
    assert gm.check_stale(path, slugs=["repoB"], resolve=resolve) == 1


def test_check_ignores_observation_time_and_unrelated_commit(saved_manifest):
    """Registry bytes and workflow meaning stay fixed when observation changes."""
    path, resolve = saved_manifest

    def edit(saved):
        saved["generated_at"] = "2000-01-01T00:00:00+00:00"
        saved["repos"][0]["git_sha"] = "unrelated-commit"

    _rewrite_manifest(path, edit)
    assert gm.check_stale(path, slugs=["repoB"], resolve=resolve) == 0


@pytest.mark.parametrize("content", [
    "{", "null", "[]", "{}", '{"repos": null}',
    '{"repos": [], "repos": []}', '{"workflow_count": NaN}',
    '{"workflow_count": Infinity}',
])
def test_check_invalid_saved_json_fails_without_traceback(saved_manifest, content, capsys):
    """Invalid or incomplete evidence has no valid discovery comparison."""
    path, resolve = saved_manifest
    path.write_text(content, encoding="utf-8")
    assert gm.check_stale(path, slugs=["repoB"], resolve=resolve) == 1
    assert "STALE:" in capsys.readouterr().err


def test_check_missing_manifest_fails_without_traceback(tmp_path, capsys):
    assert gm.check_stale(tmp_path / "absent.json", slugs=[], resolve=_resolver_for(tmp_path)) == 1
    assert "STALE:" in capsys.readouterr().err


@pytest.mark.parametrize("registry", [None, "[unclosed", "workflows: false\n"])
def test_check_cannot_accept_matching_unavailable_evidence(tmp_path, registry):
    """Two absent or invalid observations are not evidence of readiness."""
    _make_repo(tmp_path, "repoA", registry)
    path = tmp_path / "manifest.json"
    resolve = _resolver_for(tmp_path)
    gm.write_manifest(path, slugs=["repoA"], resolve=resolve)
    assert gm.check_stale(path, slugs=["repoA"], resolve=resolve) == 1


@pytest.mark.parametrize("field", ["repos", "workflows"])
def test_check_rejects_duplicate_identities(saved_manifest, field):
    """A duplicated identity is ambiguous even when every registry hash matches."""
    path, resolve = saved_manifest
    _rewrite_manifest(path, lambda saved: saved[field].append(saved[field][0]))
    assert gm.check_stale(path, slugs=["repoB"], resolve=resolve) == 1


def test_check_compares_collections_independent_of_order(tmp_path):
    """Two repos contribute 1 + 2 = 3 rows; order does not change the set."""
    _make_repo(tmp_path, "repoA", REG_V1)
    _make_repo(tmp_path, "repoB", REG_V2)
    path = tmp_path / "manifest.json"
    resolve = _resolver_for(tmp_path)
    gm.write_manifest(path, slugs=["repoA", "repoB"], resolve=resolve)

    def edit(saved):
        saved["repos"].reverse()
        saved["workflows"].reverse()
        saved["warnings"].reverse()

    _rewrite_manifest(path, edit)
    assert gm.check_stale(path, slugs=["repoB", "repoA"], resolve=resolve) == 0


def test_generated_collections_are_order_independent(tmp_path):
    """Equivalent repo sets must emit the same payload apart from observation time."""
    _make_repo(tmp_path, "repoA", REG_V1)
    _make_repo(tmp_path, "repoB", REG_V1)
    resolve = _resolver_for(tmp_path)
    left = gm.build_manifest(slugs=["repoA", "repoB", "repoA"], resolve=resolve)
    right = gm.build_manifest(slugs=["repoB", "repoA"], resolve=resolve)
    left.pop("generated_at")
    right.pop("generated_at")
    assert left == right


@pytest.mark.parametrize("fragment", [
    '"workflow_count": 2, "workflow_count": 2',
    '"git_sha": NaN',
    '"git_sha": Infinity',
])
def test_check_rejects_invalid_json_inside_otherwise_valid_manifest(saved_manifest, fragment):
    """Duplicate keys and non-finite scalars are invalid even in ignored metadata."""
    path, resolve = saved_manifest
    saved = path.read_text(encoding="utf-8")
    original = '"git_sha": null' if fragment.startswith('"git_sha"') else '"workflow_count": 2'
    assert original in saved
    path.write_text(saved.replace(original, fragment), encoding="utf-8")
    assert gm.check_stale(path, slugs=["repoB"], resolve=resolve) == 1


@pytest.mark.parametrize("content", [b"\xff", b'{"repos": []}'])
def test_check_rejects_unreadable_or_incomplete_manifest(saved_manifest, content, capsys):
    path, resolve = saved_manifest
    path.write_bytes(content)
    assert gm.check_stale(path, slugs=["repoB"], resolve=resolve) == 1
    assert capsys.readouterr().err == (
        "STALE: manifest or registry evidence is invalid or unavailable\n"
    )


@pytest.mark.parametrize("rows", ["[null]", "[{id: null}]", "[{id: 7}]", "[{}]"])
def test_invalid_registry_rows_do_not_become_successful_empty_evidence(tmp_path, rows):
    """A missing row identity prevents enumeration; it cannot prove an empty set."""
    _make_repo(tmp_path, "repoA", f"workflows: {rows}\n")
    path = tmp_path / "manifest.json"
    resolve = _resolver_for(tmp_path)
    gm.write_manifest(path, slugs=["repoA"], resolve=resolve)
    assert gm.check_stale(path, slugs=["repoA"], resolve=resolve) == 1


def test_registry_encoding_error_is_unavailable_evidence(tmp_path):
    repo = _make_repo(tmp_path, "repoA", "workflows: []\n")
    (repo / "docs" / "registry" / "workflows.yaml").write_bytes(b"\xff")
    path = tmp_path / "manifest.json"
    resolve = _resolver_for(tmp_path)
    gm.write_manifest(path, slugs=["repoA"], resolve=resolve)
    assert gm.check_stale(path, slugs=["repoA"], resolve=resolve) == 1


def test_matching_empty_readable_registries_can_pass(tmp_path):
    """An explicit empty list is evidence of zero entries, unlike missing data."""
    _make_repo(tmp_path, "repoA", "workflows: []\n")
    path = tmp_path / "manifest.json"
    resolve = _resolver_for(tmp_path)
    gm.write_manifest(path, slugs=["repoA"], resolve=resolve)
    assert gm.check_stale(path, slugs=["repoA"], resolve=resolve) == 0


def test_documented_freshness_example(tmp_path):
    """Execute the published example; its expected routing is enumerated in prose."""
    import os
    import re
    import subprocess

    root = SCRIPTS_WORKFLOW.parents[1]
    document = (root / "docs" / "guides" / "workflow-manifest-freshness.md").read_text(
        encoding="utf-8"
    )
    blocks = re.findall(r"```python\n(.*?)\n```", document, re.DOTALL)
    assert len(blocks) == 1
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env["TMPDIR"] = str(tmp_path)
    result = subprocess.run(
        [sys.executable, "-c", blocks[0]],
        cwd=root, env=env, capture_output=True, text=True, check=True,
    )
    assert result.stdout.strip() == "selected=repoA:alpha@1; rows=2; clean=0; altered=1"
    assert result.stderr.strip() == "STALE: discovery content differs from current registries"


@pytest.mark.parametrize("value", [[], {}, True, 7])
def test_ignored_commit_observation_still_requires_schema_type(saved_manifest, value):
    """The manifest schema allows a string or null commit, not arbitrary JSON."""
    path, resolve = saved_manifest
    _rewrite_manifest(path, lambda saved: saved["repos"][0].update({"git_sha": value}))
    assert gm.check_stale(path, slugs=["repoB"], resolve=resolve) == 1


@pytest.mark.parametrize("field", ["workflows", "latest_by_routing_id", "workflow_count", "warnings"])
def test_missing_discovery_field_is_not_accepted(saved_manifest, field):
    path, resolve = saved_manifest
    _rewrite_manifest(path, lambda saved: saved.pop(field))
    assert gm.check_stale(path, slugs=["repoB"], resolve=resolve) == 1


def test_changed_repository_selection_is_stale(saved_manifest):
    """Omitting the only selected repository changes the discovery set."""
    path, resolve = saved_manifest
    assert gm.check_stale(path, slugs=[], resolve=resolve) == 1


def test_generated_manifest_conforms_to_documented_schema(tmp_path):
    """Validate both healthy and diagnostic snapshots against the existing contract."""
    import jsonschema

    root = SCRIPTS_WORKFLOW.parents[1]
    schema = json.loads((root / "docs/registry/workflow-manifest.schema.json").read_text())
    jsonschema.Draft7Validator.check_schema(schema)
    _make_repo(tmp_path, "repoA", REG_V2)
    _make_repo(tmp_path, "repoB", "workflows: false\n")
    manifest = gm.build_manifest(slugs=["repoA", "repoB"], resolve=_resolver_for(tmp_path))
    jsonschema.validate(manifest, schema)


def test_cli_freshness_exit_codes(tmp_path):
    """CLI oracle: unchanged inputs return zero; altered routing data returns one."""
    import os
    import subprocess

    _make_repo(tmp_path, "repoA", REG_V2)
    repos_file = tmp_path / "repos.txt"
    repos_file.write_text("repoA\n", encoding="utf-8")
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(TIER1_REPOS_FILE=str(repos_file), TIER1_REPOS_BASE=str(tmp_path))
    path = tmp_path / "manifest.json"
    command = [sys.executable, str(SCRIPTS_WORKFLOW / "generate_workflow_manifest.py")]
    command.extend(["--output", str(path)])
    subprocess.run(command + ["--write"], env=env, capture_output=True, text=True, check=True)
    subprocess.run(command + ["--check"], env=env, capture_output=True, text=True, check=True)
    _rewrite_manifest(path, lambda saved: saved.update({"latest_by_routing_id": {}}))
    result = subprocess.run(
        command + ["--check"], env=env, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 1
    assert result.stderr.strip() == "STALE: discovery content differs from current registries"
