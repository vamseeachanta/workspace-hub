"""Tests for synthesize-archive.py — TDD first."""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add parent dir so we can import the module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from synthesize_archive import (
    backfill_knowledge,
    generate_synthesis_report,
    load_existing_ids,
    parse_frontmatter,
    parse_wrk_body,
    scan_archived_wrks,
)


# ── Helpers ──────────────────────────────────────────────────────────


def _make_wrk_file(d, wrk_id, title="Test WRK", category="harness",
                   subcategory="testing", body="## Mission\nDo something."):
    """Create a minimal WRK .md with YAML frontmatter."""
    fm = (
        f"---\n"
        f"id: {wrk_id}\n"
        f"title: \"{title}\"\n"
        f"status: archived\n"
        f"category: {category}\n"
        f"subcategory: {subcategory}\n"
        f"complexity: medium\n"
        f"target_repos:\n"
        f"  - workspace-hub\n"
        f"---\n"
        f"{body}\n"
    )
    month_dir = d / "2026-03"
    month_dir.mkdir(parents=True, exist_ok=True)
    p = month_dir / f"{wrk_id}.md"
    p.write_text(fm)
    return p


def _make_future_work(assets_dir, wrk_id, recommendations):
    """Create a future-work.yaml with given recommendations."""
    evi = assets_dir / wrk_id / "evidence"
    evi.mkdir(parents=True, exist_ok=True)
    import yaml
    data = {"wrk_id": wrk_id, "recommendations": recommendations}
    (evi / "future-work.yaml").write_text(yaml.dump(data))


def _make_resource_intelligence(assets_dir, wrk_id, gaps):
    """Create a resource-intelligence.yaml with given gaps."""
    evi = assets_dir / wrk_id / "evidence"
    evi.mkdir(parents=True, exist_ok=True)
    import yaml
    data = {"wrk_id": wrk_id, "top_p2_gaps": gaps}
    (evi / "resource-intelligence.yaml").write_text(yaml.dump(data))


def _make_cost_summary(assets_dir, wrk_id, input_tokens=1000,
                       output_tokens=500):
    """Create a cost-summary.yaml."""
    evi = assets_dir / wrk_id / "evidence"
    evi.mkdir(parents=True, exist_ok=True)
    import yaml
    data = {
        "wrk_id": wrk_id,
        "total_input_tokens": input_tokens,
        "total_output_tokens": output_tokens,
    }
    (evi / "cost-summary.yaml").write_text(yaml.dump(data))


def _setup_workspace(tmp_path, wrks, futures=None, costs=None,
                     resource_gaps=None):
    """Build a temp workspace with archive, assets, knowledge-base dirs."""
    archive = tmp_path / ".claude" / "work-queue" / "archive"
    assets = tmp_path / ".claude" / "work-queue" / "assets"
    kb = tmp_path / "knowledge-base"
    kb.mkdir(parents=True, exist_ok=True)

    for w in wrks:
        _make_wrk_file(archive, **w)

    if futures:
        for wrk_id, recs in futures.items():
            _make_future_work(assets, wrk_id, recs)

    if costs:
        for wrk_id, tokens in costs.items():
            _make_cost_summary(assets, wrk_id, **tokens)

    if resource_gaps:
        for wrk_id, gaps in resource_gaps.items():
            _make_resource_intelligence(assets, wrk_id, gaps)

    return archive, assets, kb


# ── Test: Frontmatter parsing ────────────────────────────────────────


class TestFrontmatterParsing:
    def test_basic_frontmatter(self, tmp_path):
        p = _make_wrk_file(tmp_path, "WRK-100", title="My Title",
                           category="engineering", subcategory="pipeline")
        fm = parse_frontmatter(p)
        assert fm["id"] == "WRK-100"
        assert fm["title"] == "My Title"
        assert fm["category"] == "engineering"
        assert fm["subcategory"] == "pipeline"

    def test_missing_category(self, tmp_path):
        """WRKs without category field get 'uncategorized'."""
        month = tmp_path / "2026-03"
        month.mkdir(parents=True)
        p = month / "WRK-200.md"
        p.write_text("---\nid: WRK-200\ntitle: \"No cat\"\n---\nBody\n")
        fm = parse_frontmatter(p)
        assert fm["category"] == "uncategorized"

    def test_quoted_and_unquoted_values(self, tmp_path):
        month = tmp_path / "2026-03"
        month.mkdir(parents=True)
        p = month / "WRK-300.md"
        p.write_text(
            '---\nid: WRK-300\ntitle: "Quoted title"\n'
            'category: harness\nsubcategory: testing\n---\nBody\n'
        )
        fm = parse_frontmatter(p)
        assert fm["title"] == "Quoted title"
        assert fm["category"] == "harness"

    def test_body_extraction(self, tmp_path):
        body = "## Mission\nThis is the mission text for testing."
        p = _make_wrk_file(tmp_path, "WRK-400", body=body)
        mission = parse_wrk_body(p, max_chars=500)
        assert "mission text for testing" in mission


# ── Test: Backfill ───────────────────────────────────────────────────


class TestBackfill:
    def test_backfill_new_entries(self, tmp_path):
        """Creates entries for WRKs not in JSONL."""
        archive, assets, kb = _setup_workspace(tmp_path, wrks=[
            {"wrk_id": "WRK-101", "category": "harness"},
            {"wrk_id": "WRK-102", "category": "engineering"},
        ])
        jsonl = kb / "wrk-completions.jsonl"

        stats = backfill_knowledge(
            archive_dir=archive, assets_dir=assets,
            jsonl_path=jsonl, dry_run=False,
        )
        assert stats["backfilled"] == 2
        assert stats["already_existed"] == 0

        lines = jsonl.read_text().strip().split("\n")
        assert len(lines) == 2
        ids = {json.loads(l)["id"] for l in lines}
        assert ids == {"WRK-101", "WRK-102"}

    def test_backfill_skips_existing(self, tmp_path):
        """Doesn't duplicate existing entries."""
        archive, assets, kb = _setup_workspace(tmp_path, wrks=[
            {"wrk_id": "WRK-101", "category": "harness"},
            {"wrk_id": "WRK-102", "category": "engineering"},
        ])
        jsonl = kb / "wrk-completions.jsonl"
        # Pre-populate one entry
        jsonl.write_text(
            json.dumps({"id": "WRK-101", "type": "wrk"}) + "\n"
        )

        stats = backfill_knowledge(
            archive_dir=archive, assets_dir=assets,
            jsonl_path=jsonl, dry_run=False,
        )
        assert stats["backfilled"] == 1
        assert stats["already_existed"] == 1

        lines = jsonl.read_text().strip().split("\n")
        assert len(lines) == 2

    def test_backfill_handles_missing_evidence(self, tmp_path):
        """Works when future-work.yaml / resource-intelligence.yaml missing."""
        archive, assets, kb = _setup_workspace(tmp_path, wrks=[
            {"wrk_id": "WRK-101", "category": "harness"},
        ])
        jsonl = kb / "wrk-completions.jsonl"

        stats = backfill_knowledge(
            archive_dir=archive, assets_dir=assets,
            jsonl_path=jsonl, dry_run=False,
        )
        assert stats["backfilled"] == 1
        rec = json.loads(jsonl.read_text().strip())
        assert rec["follow_ons"] == []
        assert rec["patterns"] == []

    def test_backfill_with_evidence(self, tmp_path):
        """Parses future-work and resource-intelligence when present."""
        futures = {
            "WRK-101": [
                {"id": "FW-1", "title": "Follow-on A", "status": "pending"},
                {"id": "FW-2", "title": "Follow-on B", "status": "pending"},
            ]
        }
        gaps = {"WRK-101": ["Gap 1", "Gap 2"]}
        archive, assets, kb = _setup_workspace(
            tmp_path,
            wrks=[{"wrk_id": "WRK-101", "category": "harness"}],
            futures=futures, resource_gaps=gaps,
        )
        jsonl = kb / "wrk-completions.jsonl"

        backfill_knowledge(
            archive_dir=archive, assets_dir=assets,
            jsonl_path=jsonl, dry_run=False,
        )
        rec = json.loads(jsonl.read_text().strip())
        assert len(rec["follow_ons"]) == 2
        assert len(rec["patterns"]) == 2


# ── Test: Synthesis report ───────────────────────────────────────────


class TestSynthesisReport:
    def _build_jsonl(self, tmp_path, records):
        """Write records to a temporary JSONL."""
        jsonl = tmp_path / "wrk-completions.jsonl"
        with open(jsonl, "w") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")
        return jsonl

    def test_synthesis_groups_by_category(self, tmp_path):
        """Correct category grouping."""
        recs = [
            {"id": "WRK-1", "category": "engineering",
             "subcategory": "pipeline", "title": "A",
             "follow_ons": [], "patterns": []},
            {"id": "WRK-2", "category": "engineering",
             "subcategory": "marine", "title": "B",
             "follow_ons": [], "patterns": []},
            {"id": "WRK-3", "category": "harness",
             "subcategory": "testing", "title": "C",
             "follow_ons": [], "patterns": []},
        ]
        archive, assets, kb = _setup_workspace(tmp_path, wrks=[
            {"wrk_id": "WRK-1", "category": "engineering",
             "subcategory": "pipeline"},
            {"wrk_id": "WRK-2", "category": "engineering",
             "subcategory": "marine"},
            {"wrk_id": "WRK-3", "category": "harness",
             "subcategory": "testing"},
        ])
        jsonl = self._build_jsonl(kb, recs)
        out = tmp_path / "report.yaml"

        report = generate_synthesis_report(
            jsonl_path=jsonl, archive_dir=archive,
            assets_dir=assets, output_path=out, dry_run=False,
        )
        assert report["categories"]["engineering"]["count"] == 2
        assert report["categories"]["harness"]["count"] == 1
        subs = report["categories"]["engineering"]["subcategories"]
        assert "pipeline" in subs
        assert "marine" in subs

    def test_synthesis_counts_follow_ons(self, tmp_path):
        """Unaddressed follow-on counting."""
        futures = {
            "WRK-1": [
                {"id": "FW-1", "title": "Unaddressed A",
                 "status": "pending"},
                {"id": "FW-2", "title": "Addressed B",
                 "status": "captured", "captured": True},
            ]
        }
        recs = [
            {"id": "WRK-1", "category": "engineering",
             "subcategory": "pipeline", "title": "A",
             "follow_ons": ["FW-1", "FW-2"], "patterns": []},
        ]
        archive, assets, kb = _setup_workspace(
            tmp_path,
            wrks=[{"wrk_id": "WRK-1", "category": "engineering",
                   "subcategory": "pipeline"}],
            futures=futures,
        )
        jsonl = self._build_jsonl(kb, recs)
        out = tmp_path / "report.yaml"

        report = generate_synthesis_report(
            jsonl_path=jsonl, archive_dir=archive,
            assets_dir=assets, output_path=out, dry_run=False,
        )
        cat = report["categories"]["engineering"]
        assert len(cat["unaddressed_follow_ons"]) == 1
        assert cat["unaddressed_follow_ons"][0]["wrk"] == "WRK-1"

    def test_synthesis_repeat_spawners(self, tmp_path):
        """Identifies WRKs with 3+ follow-ons."""
        futures = {
            "WRK-1": [
                {"id": f"FW-{i}", "title": f"Item {i}",
                 "status": "pending"}
                for i in range(4)
            ]
        }
        recs = [
            {"id": "WRK-1", "category": "harness",
             "subcategory": "testing", "title": "Spawner",
             "follow_ons": [f"FW-{i}" for i in range(4)],
             "patterns": []},
        ]
        archive, assets, kb = _setup_workspace(
            tmp_path,
            wrks=[{"wrk_id": "WRK-1", "category": "harness",
                   "subcategory": "testing"}],
            futures=futures,
        )
        jsonl = self._build_jsonl(kb, recs)
        out = tmp_path / "report.yaml"

        report = generate_synthesis_report(
            jsonl_path=jsonl, archive_dir=archive,
            assets_dir=assets, output_path=out, dry_run=False,
        )
        spawners = report["categories"]["harness"]["repeat_spawners"]
        assert len(spawners) == 1
        assert spawners[0]["follow_on_count"] == 4

    def test_synthesis_heat_map(self, tmp_path):
        """Correct density calculation in heat_map."""
        futures = {
            "WRK-1": [
                {"id": "FW-1", "title": "A", "status": "pending"},
            ],
        }
        recs = [
            {"id": "WRK-1", "category": "engineering",
             "subcategory": "pipeline", "title": "A",
             "follow_ons": ["FW-1"], "patterns": []},
            {"id": "WRK-2", "category": "engineering",
             "subcategory": "pipeline", "title": "B",
             "follow_ons": [], "patterns": []},
        ]
        archive, assets, kb = _setup_workspace(
            tmp_path,
            wrks=[
                {"wrk_id": "WRK-1", "category": "engineering",
                 "subcategory": "pipeline"},
                {"wrk_id": "WRK-2", "category": "engineering",
                 "subcategory": "pipeline"},
            ],
            futures=futures,
        )
        jsonl = self._build_jsonl(kb, recs)
        out = tmp_path / "report.yaml"

        report = generate_synthesis_report(
            jsonl_path=jsonl, archive_dir=archive,
            assets_dir=assets, output_path=out, dry_run=False,
        )
        hm = report["heat_map"]
        assert len(hm) >= 1
        assert hm[0]["category"] == "engineering"
        # 1 unaddressed out of 2 = 0.5
        assert hm[0]["density"] == 0.5

    def test_synthesis_cost_aggregation(self, tmp_path):
        """Aggregates cost data across WRKs."""
        costs = {
            "WRK-1": {"input_tokens": 1000, "output_tokens": 500},
            "WRK-2": {"input_tokens": 2000, "output_tokens": 800},
        }
        recs = [
            {"id": "WRK-1", "category": "engineering",
             "subcategory": "pipeline", "title": "A",
             "follow_ons": [], "patterns": []},
            {"id": "WRK-2", "category": "harness",
             "subcategory": "testing", "title": "B",
             "follow_ons": [], "patterns": []},
        ]
        archive, assets, kb = _setup_workspace(
            tmp_path,
            wrks=[
                {"wrk_id": "WRK-1", "category": "engineering",
                 "subcategory": "pipeline"},
                {"wrk_id": "WRK-2", "category": "harness",
                 "subcategory": "testing"},
            ],
            costs=costs,
        )
        jsonl = self._build_jsonl(kb, recs)
        out = tmp_path / "report.yaml"

        report = generate_synthesis_report(
            jsonl_path=jsonl, archive_dir=archive,
            assets_dir=assets, output_path=out, dry_run=False,
        )
        cs = report["cost_summary"]
        assert cs["total_tokens"] == 4300
        assert cs["by_category"]["engineering"] == 1500
        assert cs["by_category"]["harness"] == 2800


# ── Test: Dry run ────────────────────────────────────────────────────


class TestDryRun:
    def test_dry_run_no_writes(self, tmp_path):
        """Dry-run doesn't write files."""
        archive, assets, kb = _setup_workspace(tmp_path, wrks=[
            {"wrk_id": "WRK-101", "category": "harness"},
        ])
        jsonl = kb / "wrk-completions.jsonl"
        report_out = tmp_path / "report.yaml"

        backfill_knowledge(
            archive_dir=archive, assets_dir=assets,
            jsonl_path=jsonl, dry_run=True,
        )
        assert not jsonl.exists()

        # Create an empty JSONL so report can read it
        jsonl.write_text("")
        generate_synthesis_report(
            jsonl_path=jsonl, archive_dir=archive,
            assets_dir=assets, output_path=report_out, dry_run=True,
        )
        assert not report_out.exists()


# ── Test: Scanning ───────────────────────────────────────────────────


class TestScanning:
    def test_scan_finds_sharded_archives(self, tmp_path):
        """Finds WRKs in YYYY-MM subdirectories."""
        archive = tmp_path / "archive"
        m1 = archive / "2026-01"
        m1.mkdir(parents=True)
        (m1 / "WRK-001.md").write_text("---\nid: WRK-001\n---\n")
        m2 = archive / "2026-02"
        m2.mkdir(parents=True)
        (m2 / "WRK-002.md").write_text("---\nid: WRK-002\n---\n")
        # Also flat
        (archive / "WRK-003.md").write_text("---\nid: WRK-003\n---\n")

        files = scan_archived_wrks(archive)
        ids = {f.stem for f in files}
        assert ids == {"WRK-001", "WRK-002", "WRK-003"}
