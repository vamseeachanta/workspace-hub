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
    assert statuses["repoA"] == "invalid-registry"
    assert statuses["repoB"] == "invalid-registry"


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


# Issue #3450 states are logical expectations over controlled filesystem inputs.
# No numerical engineering criteria apply; row counts are hand-counted fixtures.
def test_missing_repository_is_distinct(tmp_path):
    manifest = gm.build_manifest(slugs=["absent"], resolve=_resolver_for(tmp_path))
    assert manifest["repos"][0]["status"] == "missing-repository"
    assert manifest["repos"][0]["registry_sha256"] is None


@pytest.mark.parametrize("text", [
    "workflows: wrong-shape\n", "workflows: [null]\n",
    "workflows: [{title: missing-id}]\n", "workflows: [{id: [bad]}]\n",
])
def test_invalid_registry_shape_is_not_aggregated(tmp_path, text):
    _make_repo(tmp_path, "fixture", text)
    manifest = gm.build_manifest(slugs=["fixture"], resolve=_resolver_for(tmp_path))
    assert manifest["repos"][0]["status"] == "invalid-registry"
    assert manifest["repos"][0]["registry_sha256"] is None
    assert manifest["workflows"] == []


@pytest.mark.parametrize("error", [PermissionError, UnicodeDecodeError])
def test_unreadable_registry_is_invalid(tmp_path, monkeypatch, error):
    repo = _make_repo(tmp_path, "fixture", REG_V1)
    registry = repo / "docs/registry/workflows.yaml"
    original = Path.read_text

    def read(path, *args, **kwargs):
        if path == registry:
            if error is UnicodeDecodeError:
                raise error("utf-8", b"x", 0, 1, "fixture")
            raise error("fixture")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read)
    manifest = gm.build_manifest(slugs=["fixture"], resolve=_resolver_for(tmp_path))
    assert manifest["repos"][0]["status"] == "invalid-registry"


def test_worked_example_partitions_observations(tmp_path, capsys):
    """Independent truth table from issue #3450, derived without the generator.

    Five synthetic repositories initially have identical REG_V1 bytes. Keep
    one; append a YAML comment to another; remove the third repository via the
    resolver; remove the fourth registry via the reader; invalidate the fifth
    with a YAML scalar. Thus one unchanged + one drifted + three failures = five
    observations. Null cannot establish digest equality or content difference.
    No engineering coefficients or acceptance thresholds are used.
    """
    slugs = ["unchanged", "drifted", "absent", "no-registry", "invalid"]
    for slug in slugs:
        _make_repo(tmp_path, slug, REG_V1)
    saved = tmp_path / "manifest.json"
    gm.write_manifest(saved, slugs=slugs, resolve=_resolver_for(tmp_path))
    (tmp_path / "drifted/docs/registry/workflows.yaml").write_text(REG_V1 + "# changed\n")
    (tmp_path / "invalid/docs/registry/workflows.yaml").write_text("scalar\n")

    def resolve(slug):
        if slug == "absent":
            raise FileNotFoundError("fixture")
        if slug == "no-registry":
            return _make_repo(tmp_path / "empty", slug)
        return tmp_path / slug

    report = gm.stale_report(saved, slugs=slugs, resolve=resolve)
    states = {row["repo"]: row["status"] for row in report["repos"]}
    assert states == {
        "unchanged": "unchanged", "drifted": "drifted",
        "absent": "missing-repository", "no-registry": "missing-registry",
        "invalid": "invalid-registry",
    }
    assert gm.check_stale(saved, slugs=slugs, resolve=resolve) == 1
    human = capsys.readouterr().err
    assert "registries changed since manifest: ['drifted']" in human
    for status in ("missing-repository", "missing-registry", "invalid-registry"):
        assert status in human
    assert "None" not in human


@pytest.mark.parametrize("saved_hash", [None, "", "not-a-hash"])
def test_invalid_saved_digest_never_becomes_drift(tmp_path, saved_hash):
    _make_repo(tmp_path, "fixture", REG_V1)
    saved = tmp_path / "manifest.json"
    gm.write_manifest(saved, slugs=["fixture"], resolve=_resolver_for(tmp_path))
    payload = json.loads(saved.read_text())
    payload["repos"][0]["registry_sha256"] = saved_hash
    saved.write_text(json.dumps(payload))
    report = gm.stale_report(saved, slugs=["fixture"], resolve=_resolver_for(tmp_path))
    assert report["repos"][0]["status"] == "invalid-registry"
    assert report["repos"][0]["reason"] == "invalid-saved-observation"
    assert gm.check_stale(saved, slugs=["fixture"], resolve=_resolver_for(tmp_path)) == 1


def test_equal_null_hashes_do_not_pass(tmp_path):
    slugs = ["absent"]
    saved = tmp_path / "manifest.json"
    gm.write_manifest(saved, slugs=slugs, resolve=_resolver_for(tmp_path))
    assert gm.check_stale(saved, slugs=slugs, resolve=_resolver_for(tmp_path)) == 1


def test_json_check_preserves_states(tmp_path, monkeypatch, capsys):
    _make_repo(tmp_path, "fixture", REG_V1)
    saved = tmp_path / "manifest.json"
    gm.write_manifest(saved, slugs=["fixture"], resolve=_resolver_for(tmp_path))
    report = gm.stale_report(saved, slugs=["fixture"], resolve=_resolver_for(tmp_path))
    monkeypatch.setattr(gm, "stale_report", lambda *args, **kwargs: report)
    assert gm.main(["--check", "--json", "--output", str(saved)]) == 0
    output = capsys.readouterr()
    assert json.loads(output.out)["repos"][0]["status"] == "unchanged"
    assert output.err == ""


def test_failure_entries_match_manifest_schema(tmp_path):
    import jsonschema

    schema = json.loads((SCRIPTS_WORKFLOW.parents[1] / "docs/registry/workflow-manifest.schema.json").read_text())
    _make_repo(tmp_path, "empty")
    _make_repo(tmp_path, "invalid", "scalar\n")
    manifest = gm.build_manifest(slugs=["absent", "empty", "invalid"], resolve=_resolver_for(tmp_path))
    jsonschema.validate(manifest, schema)


@pytest.mark.parametrize("saved_text", ["null", "[]", "{bad", '{"repos": null}'])
def test_invalid_saved_manifest_cannot_establish_freshness(tmp_path, saved_text):
    _make_repo(tmp_path, "fixture", REG_V1)
    saved = tmp_path / "manifest.json"
    saved.write_text(saved_text)
    report = gm.stale_report(saved, slugs=["fixture"], resolve=_resolver_for(tmp_path))
    assert report["ok"] is False
    assert report["repos"][0]["status"] == "invalid-registry"
    assert report["repos"][0]["reason"] == "invalid-saved-observation"


def test_membership_changes_are_unavailable_comparisons(tmp_path):
    for slug in ("previous", "new"):
        _make_repo(tmp_path, slug, REG_V1)
    saved = tmp_path / "manifest.json"
    gm.write_manifest(saved, slugs=["previous"], resolve=_resolver_for(tmp_path))
    report = gm.stale_report(saved, slugs=["new"], resolve=_resolver_for(tmp_path))
    assert {row["repo"]: (row["status"], row["reason"]) for row in report["repos"]} == {
        "previous": ("missing-repository", "not-visited"),
        "new": ("invalid-registry", "invalid-saved-observation"),
    }


def test_json_failure_reports_missing_repository(tmp_path, capsys):
    saved = tmp_path / "manifest.json"
    gm.write_manifest(saved, slugs=["absent"], resolve=_resolver_for(tmp_path))
    assert gm.check_stale(saved, slugs=["absent"], resolve=_resolver_for(tmp_path), json_output=True) == 1
    output = capsys.readouterr()
    assert json.loads(output.out)["repos"][0]["status"] == "missing-repository"
    assert output.err == ""


def test_canonical_and_linked_manifest_classifications_agree(tmp_path, monkeypatch):
    """Same sibling bytes imply equal observations, independent of tree depth."""
    import os
    import subprocess
    from functools import partial

    from lib.tier1_repos import resolve_tier1_repo_path

    for name in ("REPO_ROOT", "TIER1_REPOS_BASE"):
        monkeypatch.delenv(name, raising=False)
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    canonical = tmp_path / "workspace/hub"
    canonical.mkdir(parents=True)
    subprocess.run(["git", "init", str(canonical)], env=env, check=True, capture_output=True)
    linked = tmp_path / "worktrees/arbitrary/depth/hub"
    subprocess.run(
        ["git", "-C", str(canonical), "worktree", "add", "--orphan", "-b", "fixture-branch", str(linked)],
        env=env, check=True, capture_output=True,
    )
    _make_repo(canonical.parent, "valid", REG_V1)
    _make_repo(canonical.parent, "empty")
    _make_repo(canonical.parent, "invalid", "scalar\n")
    slugs = ["valid", "empty", "invalid", "absent"]
    canonical_resolve = partial(resolve_tier1_repo_path, repo_root=canonical)
    linked_resolve = partial(resolve_tier1_repo_path, repo_root=linked)
    saved = tmp_path / "manifest.json"
    gm.write_manifest(saved, slugs=slugs, resolve=canonical_resolve)
    main_report = gm.stale_report(saved, slugs=slugs, resolve=canonical_resolve)
    linked_report = gm.stale_report(saved, slugs=slugs, resolve=linked_resolve)
    assert main_report == linked_report
    assert {row["repo"]: row["status"] for row in linked_report["repos"]} == {
        "valid": "unchanged", "empty": "missing-registry",
        "invalid": "invalid-registry", "absent": "missing-repository",
    }


def test_repository_is_resolved_once_per_observation(tmp_path):
    repo = _make_repo(tmp_path, "fixture", REG_V1)
    calls = []

    def resolve(slug):
        calls.append(slug)
        return repo

    gm.build_manifest(slugs=["fixture"], resolve=resolve)
    assert calls == ["fixture"]
