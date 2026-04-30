"""Tests for the #2555 GTM brochure chart renderer."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "gtm" / "render_brochure_charts.py"


def load_renderer():
    spec = importlib.util.spec_from_file_location("render_brochure_charts", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_minimal_digitalmodel_root(tmp_path: Path) -> Path:
    root = tmp_path / "digitalmodel"
    gtm = root / "examples" / "demos" / "gtm"
    write_json(
        gtm / "results" / "vessel_comparison_matrix.json",
        {
            "vessels": [
                {
                    "name": "Large CSV",
                    "type": "CSV",
                    "capabilities": {
                        "mudmat_installation": {
                            "cases_pass": 18,
                            "cases_total": 18,
                            "pass_rate_pct": 100.0,
                            "limiting_factor": "Landing bearing pressure",
                        }
                    },
                },
                {
                    "name": "Medium CSV",
                    "type": "CSV",
                    "capabilities": {
                        "mudmat_installation": {
                            "cases_pass": 18,
                            "cases_total": 18,
                            "pass_rate_pct": 100.0,
                            "limiting_factor": "Splash zone hydrodynamic loads",
                        }
                    },
                },
                {
                    "name": "Large PLV",
                    "type": "PLV",
                    "capabilities": {
                        "shallow_water_pipelay": {
                            "cases_pass": 25,
                            "cases_total": 30,
                            "pass_rate_pct": 83.3,
                            "limiting_factor": "Vessel draft",
                            "go_nogo_matrix": {
                                "8in": {"7m": "NO_GO", "10m": "GO"},
                                "12in": {"7m": "NO_GO", "10m": "GO"},
                            },
                        }
                    },
                },
                {
                    "name": "Shallow Water Barge",
                    "type": "BARGE",
                    "capabilities": {
                        "shallow_water_pipelay": {
                            "cases_pass": 30,
                            "cases_total": 30,
                            "pass_rate_pct": 100.0,
                            "limiting_factor": "Tensioner capacity",
                            "go_nogo_matrix": {
                                "8in": {"7m": "GO", "10m": "GO"},
                                "12in": {"7m": "GO", "10m": "GO"},
                            },
                        }
                    },
                },
            ]
        },
    )
    write_json(
        gtm / "results" / "structure_comparison_matrix.json",
        {
            "comparisons": [
                {
                    "category": "mudmats",
                    "by_vessel": {
                        "Large CSV": {"crane_util_at_1500m": {"Mudmat-L-200te": 20.6}},
                        "Medium CSV": {"crane_util_at_1500m": {"Mudmat-L-200te": 71.5}},
                    },
                }
            ]
        },
    )
    write_json(
        gtm / "data" / "pipelay_vessels.json",
        {
            "_description": "Pipelay vessel database. Vessel parameters are representative of real vessel classes.",
            "_references": ["DNV-ST-F101", "DNV-OS-F101", "API RP 1111"],
            "vessels": [
                {"name": "Large PLV", "representative_class": "S-lay", "pipelay_system": {"water_depth_range": {"min_m": 10}}},
                {"name": "Shallow Water Barge", "representative_class": "DLB", "pipelay_system": {"water_depth_range": {"min_m": 5}}},
            ],
        },
    )
    write_json(
        gtm / "data" / "csv_hlv_vessels.json",
        {
            "_description": "CSV database. Vessel parameters are representative of real vessel classes but are not exact specifications of any named vessel.",
            "_references": ["DNV-RP-H103", "DNV-ST-N001", "DNV-OS-H101"],
            "vessels": [
                {"name": "Large CSV", "representative_class": "Aegir class"},
                {"name": "Medium CSV", "representative_class": "Normand class"},
            ],
        },
    )
    return root


def test_build_chart_pack_derives_required_headlines_and_disclosures(tmp_path: Path) -> None:
    renderer = load_renderer()
    root = build_minimal_digitalmodel_root(tmp_path)

    pack = renderer.build_chart_pack(root)

    assert [chart.chart_id for chart in pack.charts] == ["C1", "C2", "C3"]
    assert pack.total_cases == 96
    c1, c2, c3 = pack.charts
    assert "Shallow Water Barge" in c1.headline
    assert "100.0% pass rate across 30 cases" in c1.headline
    assert "representative classes" in c1.disclosure
    assert "DNV-ST-F101" in c1.caption
    assert "API RP 1111" in c1.caption
    assert "7m" in c2.headline
    assert "Large PLV" in c2.headline
    assert "20.6%" in c3.headline and "71.5%" in c3.headline


def test_render_chart_pack_writes_manifest_sidecars_and_three_formats(tmp_path: Path) -> None:
    renderer = load_renderer()
    root = build_minimal_digitalmodel_root(tmp_path)
    output_dir = tmp_path / "assets"
    legal_dir = tmp_path / "legal-scans"
    output_dir.mkdir(parents=True)
    legal_dir.mkdir(parents=True)

    manifest_path = renderer.render_chart_pack(root, output_dir, legal_dir)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["issue"] == 2555
    assert manifest["chart_count"] == 3
    assert manifest["legal_scan_status"] == "passed"
    assert all(chart["caption_sidecar"] for chart in manifest["charts"])
    assert not Path(manifest["legal_scan"]).is_absolute()
    for chart in manifest["charts"]:
        for key in ["png", "svg", "pdf", "caption_sidecar", "metadata_sidecar"]:
            assert not Path(chart[key]).is_absolute()
            path = output_dir / Path(chart[key]).name
            assert path.exists(), f"missing {key}: {path}"
            assert path.stat().st_size > 0
        caption = (output_dir / Path(chart["caption_sidecar"]).name).read_text(encoding="utf-8")
        assert "representative" in caption.lower()
        assert "client_projects" not in caption


def test_renderer_refuses_missing_asset_directory_gate(tmp_path: Path) -> None:
    renderer = load_renderer()
    root = build_minimal_digitalmodel_root(tmp_path)
    missing_output = tmp_path / "missing" / "assets"

    try:
        renderer.render_chart_pack(root, missing_output, tmp_path / "legal")
    except FileNotFoundError as exc:
        assert "asset-directory gate" in str(exc)
    else:
        raise AssertionError("renderer should require pre-existing asset directory")
