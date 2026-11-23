import importlib.util
import json
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "flywheel_closeout.py"


def load_module():
    spec = importlib.util.spec_from_file_location("flywheel_closeout", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_fixture(tmp_path: Path) -> Path:
    fixture = tmp_path / "wave.yaml"
    fixture.write_text(
        """
sources:
  - kind: issue
    repo: vamseeachanta/llm-wiki
    locator: https://github.com/vamseeachanta/llm-wiki/issues/227
    title: flagged bucket strategy
    text: parser-limit lesson should become prompt guidance
  - kind: review_artifact
    repo: vamseeachanta/llm-wiki
    locator: scripts/review/results/2026-06-02-plan-259-disagreement.md
    title: review artifact privacy
    text: review artifact stale SHA and stderr publishability risk should route to workspace-hub
  - kind: pr
    repo: vamseeachanta/llm-wiki
    locator: https://github.com/vamseeachanta/llm-wiki/pull/248
    title: content-value filter
    text: content-value filter should be script hardening
existing_issues:
  - repo: vamseeachanta/workspace-hub
    number: 2502
    title: Review artifact metadata and privacy
    state: OPEN
""",
        encoding="utf-8",
    )
    return fixture


def test_fixture_closeout_routes_candidates_and_suppresses_2502_duplicate(tmp_path: Path) -> None:
    module = load_module()
    fixture = write_fixture(tmp_path)
    sources, existing = module.load_fixture(fixture)
    candidates = module.identify_learnings(sources, existing)
    by_id = {candidate["id"]: candidate for candidate in candidates}
    assert by_id["parser-limit-prompt"]["route_repo"] == "vamseeachanta/llm-wiki"
    assert by_id["content-value-script"]["asset_class"] == "script"
    assert by_id["review-artifact-publishability"]["route_repo"] == "vamseeachanta/workspace-hub"
    assert by_id["review-artifact-publishability"]["suppressed_duplicate_issue"] is True
    assert by_id["review-artifact-publishability"]["existing_issue"] == "vamseeachanta/workspace-hub#2502"


def test_render_outputs_are_advisory_and_evidence_linked(tmp_path: Path) -> None:
    module = load_module()
    fixture = write_fixture(tmp_path)
    rc = module.main(["--repo", "vamseeachanta/llm-wiki", "--source-issue", "vamseeachanta/workspace-hub#2945", "--fixture", str(fixture), "--out-dir", str(tmp_path / "out")])
    assert rc == 0
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["mode"] == "propose"
    assert manifest["advisory_only"] is True
    assert manifest["warnings"]
    assert manifest["candidate_count"] >= 3
    assert (tmp_path / "out" / "report.html").exists()
    assert (tmp_path / "out" / "issue-drafts" / "workspace-hub-2502-comment.md").exists()
    assert manifest["source_count"] >= 3
    assert manifest["draft_paths"]
    draft = (tmp_path / "out" / "issue-drafts" / "content-value-script.md").read_text(encoding="utf-8")
    assert "## What To Build" in draft
    assert "## Acceptance Criteria" in draft


def test_private_sources_are_advisory_nonpublishable_records(tmp_path: Path) -> None:
    module = load_module()
    bad = tmp_path / "bad.yaml"
    bad.write_text("sources:\n  - kind: issue\n    repo: x/y\n    locator: bad\n    title: leak\n    text: /home/vamsee/private\n", encoding="utf-8")
    rc = module.main(["--repo", "x/y", "--source-issue", "x/y#1", "--fixture", str(bad), "--out-dir", str(tmp_path / "bad-out")])
    assert rc == 0
    manifest = json.loads((tmp_path / "bad-out" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["non_publishable_records"][0]["reason"] == "private_path"


def test_approved_cli_surface_accepts_source_selectors(tmp_path: Path) -> None:
    module = load_module()
    fixture = write_fixture(tmp_path)
    rc = module.main([
        "--repo", "vamseeachanta/llm-wiki",
        "--source-issue", "vamseeachanta/workspace-hub#2945",
        "--issue", "135", "--issue", "226", "--issue", "227", "--issue", "259", "--issue", "260",
        "--pr-range", "176-258",
        "--artifact", "scripts/review/results/2026-06-02-plan-259-disagreement.md",
        "--fixture", str(fixture),
        "--out-dir", str(tmp_path / "out"),
        "--format", "html,json,issue-drafts",
        "--mode", "propose",
    ])
    assert rc == 0
