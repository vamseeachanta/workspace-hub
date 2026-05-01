#!/usr/bin/env python3
"""Render #2555 vessel capability brochure chart assets.

This wrapper intentionally lives outside ``digitalmodel/``. It consumes the existing
representative-class GTM demo JSON outputs, writes static brochure assets under
``docs/reports/gtm/assets/``, and archives caption/metadata/legal-scan sidecars so
#2556 can assemble a brochure without re-deriving chart context.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ISSUE_NUMBER = 2555
FORBIDDEN_PATTERNS = (
    "client_projects",
    "acma-projects",
    "seanation",
    "frontierdeepwater",
)
REPRESENTATIVE_DISCLOSURE = (
    "Vessel parameters are representative classes only; not measured telemetry "
    "or exact specifications of any named vessel."
)


@dataclass(frozen=True)
class ChartSpec:
    chart_id: str
    slug: str
    title: str
    headline: str
    caption: str
    disclosure: str
    data_inputs: tuple[str, ...]
    rows: tuple[tuple[str, str, str, str], ...]


@dataclass(frozen=True)
class ChartPack:
    charts: tuple[ChartSpec, ...]
    total_cases: int
    generated_at: str


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Required #2555 chart input is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def gtm_root(digitalmodel_root: Path) -> Path:
    return digitalmodel_root / "examples" / "demos" / "gtm"


def require_representative_source(payload: dict[str, Any], path: str) -> None:
    description = str(payload.get("_description", "")).lower()
    if "representative" not in description:
        raise ValueError(f"{path} must disclose representative-class vessel data")


def normalise_standard(ref: str) -> str:
    return ref.split("(", 1)[0].strip().replace("API-RP", "API RP")


def standards_from(*payloads: dict[str, Any]) -> list[str]:
    seen: list[str] = []
    for payload in payloads:
        for ref in payload.get("_references", []):
            standard = normalise_standard(str(ref))
            if standard and standard not in seen:
                seen.append(standard)
    return seen


def iter_capabilities(vessel_matrix: dict[str, Any]):
    for vessel in vessel_matrix.get("vessels", []):
        for capability_name, capability in vessel.get("capabilities", {}).items():
            yield vessel, capability_name, capability


def build_chart_pack(digitalmodel_root: Path) -> ChartPack:
    root = gtm_root(digitalmodel_root)
    vessel_path = root / "results" / "vessel_comparison_matrix.json"
    structure_path = root / "results" / "structure_comparison_matrix.json"
    pipelay_path = root / "data" / "pipelay_vessels.json"
    csv_path = root / "data" / "csv_hlv_vessels.json"
    vessel_logical_path = "digitalmodel/examples/demos/gtm/results/vessel_comparison_matrix.json"
    structure_logical_path = "digitalmodel/examples/demos/gtm/results/structure_comparison_matrix.json"
    pipelay_logical_path = "digitalmodel/examples/demos/gtm/data/pipelay_vessels.json"
    csv_logical_path = "digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json"

    vessel_matrix = load_json(vessel_path)
    structure_matrix = load_json(structure_path)
    pipelay_vessels = load_json(pipelay_path)
    csv_vessels = load_json(csv_path)
    require_representative_source(pipelay_vessels, "pipelay_vessels.json")
    require_representative_source(csv_vessels, "csv_hlv_vessels.json")

    total_cases = sum(int(cap.get("cases_total", 0)) for _, _, cap in iter_capabilities(vessel_matrix))

    # C1: pick strongest pass-rate pair, tie-broken to Shallow Water Barge shallow pipelay
    capabilities = list(iter_capabilities(vessel_matrix))
    preferred = [
        item
        for item in capabilities
        if item[0].get("name") == "Shallow Water Barge"
        and item[1] in {"shallow_water_pipelay", "shallow_pipelay"}
    ]
    c1_vessel, c1_capability_name, c1_capability = (preferred or sorted(
        capabilities,
        key=lambda item: (float(item[2].get("pass_rate_pct", 0)), int(item[2].get("cases_total", 0))),
        reverse=True,
    ))[0]
    c1_standards = standards_from(pipelay_vessels, csv_vessels)
    c1_rows = tuple(
        (
            str(vessel.get("name", "Unknown vessel")),
            humanize_capability(capability_name),
            f"{float(capability.get('pass_rate_pct', 0)):.1f}%",
            f"{int(capability.get('cases_pass', 0))}/{int(capability.get('cases_total', 0))} pass; limiting: {capability.get('limiting_factor', 'not stated')}",
        )
        for vessel, capability_name, capability in capabilities
    )
    c1 = ChartSpec(
        chart_id="C1",
        slug="c1-vessel-job-capability-heatmap",
        title="Vessel-vs-Job Capability Heatmap",
        headline=(
            f"{c1_vessel['name']} — {humanize_capability(c1_capability_name)}: "
            f"{float(c1_capability['pass_rate_pct']):.1f}% pass rate across "
            f"{int(c1_capability['cases_total'])} cases; current matrix totals {total_cases} cases."
        ),
        caption=(
            "Screening-grade vessel-vs-job capability matrix from ACE Engineer's GTM demo outputs. "
            f"Standards cited/inherited: {', '.join(c1_standards)}. "
            + REPRESENTATIVE_DISCLOSURE
        ),
        disclosure=REPRESENTATIVE_DISCLOSURE,
        data_inputs=(vessel_logical_path, pipelay_logical_path, csv_logical_path),
        rows=c1_rows,
    )

    # C2: pipelay operating envelope, comparing PLV and shallow-water barge.
    pipelay_items = [item for item in capabilities if "pipelay" in item[1]]
    rows: list[tuple[str, str, str, str]] = []
    shallow_barge_headline = "Shallow Water Barge shallow-water capability recomputed from latest matrix."
    for vessel, _, capability in pipelay_items:
        matrix = capability.get("go_nogo_matrix", {})
        go_cells: list[tuple[str, str]] = []
        no_go_cells: list[tuple[str, str]] = []
        for pipe_size, by_depth in matrix.items():
            for depth, status in by_depth.items():
                (go_cells if status == "GO" else no_go_cells).append((str(pipe_size), str(depth)))
        depths = sorted({depth for _, depth in go_cells}, key=depth_sort_key)
        pipe_sizes = sorted({pipe for pipe, _ in go_cells}, key=pipe_sort_key)
        rows.append(
            (
                str(vessel.get("name", "Unknown vessel")),
                f"{len(go_cells)} GO / {len(go_cells) + len(no_go_cells)} cells",
                f"Depths: {span_label(depths)}",
                f"Pipe sizes: {span_label(pipe_sizes)}; limiting: {capability.get('limiting_factor', 'not stated')}",
            )
        )
        if vessel.get("name") == "Shallow Water Barge" and depths and pipe_sizes:
            shallow_barge_headline = (
                f"Shallow Water Barge screens GO across {span_label(pipe_sizes)} at "
                f"{span_label(depths)} while Large PLV is draft-limited at the shallowest row."
            )
    c2 = ChartSpec(
        chart_id="C2",
        slug="c2-pipelay-operating-envelope",
        title="Pipelay Operating Envelope",
        headline=shallow_barge_headline,
        caption=(
            "Shallow-water S-lay envelope by vessel class, pipe size, and water depth. "
            "Citations inherited from pipelay source: "
            f"{', '.join(standards_from(pipelay_vessels))}. "
            + REPRESENTATIVE_DISCLOSURE
        ),
        disclosure=REPRESENTATIVE_DISCLOSURE,
        data_inputs=(vessel_logical_path, pipelay_logical_path),
        rows=tuple(rows),
    )

    # C3: crane-utilisation margin map.
    mudmats = next(
        (comp for comp in structure_matrix.get("comparisons", []) if comp.get("category") == "mudmats"),
        None,
    )
    if not mudmats:
        raise ValueError("structure_comparison_matrix.json has no mudmats comparison")
    util_by_vessel = {
        vessel: data.get("crane_util_at_1500m", {})
        for vessel, data in mudmats.get("by_vessel", {}).items()
    }
    structures = sorted({s for data in util_by_vessel.values() for s in data})
    largest: tuple[float, str, float, float] | None = None
    c3_rows: list[tuple[str, str, str, str]] = []
    for structure in structures:
        vals = {vessel: float(data[structure]) for vessel, data in util_by_vessel.items() if structure in data}
        if len(vals) >= 2:
            low_vessel = min(vals, key=vals.get)
            high_vessel = max(vals, key=vals.get)
            delta = vals[high_vessel] - vals[low_vessel]
            if largest is None or delta > largest[0]:
                largest = (delta, structure, vals[low_vessel], vals[high_vessel])
        c3_rows.append((structure, *(f"{vessel}: {value:.1f}%" for vessel, value in vals.items()), "1500 m"))
    if largest is None:
        raise ValueError("Need at least two vessels with crane utilisation for C3")
    _, structure, low_util, high_util = largest
    c3 = ChartSpec(
        chart_id="C3",
        slug="c3-crane-utilisation-margin-map",
        title="Crane-Utilisation Margin Map",
        headline=(
            f"{structure} at 1500 m: Large CSV at {low_util:.1f}% crane utilisation vs "
            f"Medium CSV at {high_util:.1f}% — same GO decision, different margin."
        ),
        caption=(
            "Crane-utilisation margin for mudmat installation screening at 1500 m water depth. "
            "Citations inherited from CSV/HLV source: "
            f"{', '.join(standards_from(csv_vessels))}. "
            + REPRESENTATIVE_DISCLOSURE
        ),
        disclosure=REPRESENTATIVE_DISCLOSURE,
        data_inputs=(structure_logical_path, csv_logical_path),
        rows=tuple(c3_rows),
    )

    return ChartPack(
        charts=(c1, c2, c3),
        total_cases=total_cases,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )


def humanize_capability(name: str) -> str:
    return name.replace("_", " ").replace("shallow water", "shallow-water").title()


def depth_sort_key(depth: str) -> int:
    return int(re.sub(r"\D", "", depth) or 0)


def pipe_sort_key(pipe: str) -> int:
    return int(re.sub(r"\D", "", pipe) or 0)


def span_label(items: list[str]) -> str:
    if not items:
        return "none"
    if len(items) == 1:
        return items[0]
    return f"{items[0]}–{items[-1]}"


def assert_output_dirs(output_dir: Path, legal_scan_dir: Path) -> None:
    if not output_dir.exists() or not output_dir.is_dir():
        raise FileNotFoundError(
            f"asset-directory gate not met; create via implementation slice before render: {output_dir}"
        )
    if not legal_scan_dir.exists() or not legal_scan_dir.is_dir():
        raise FileNotFoundError(
            f"legal-scan directory gate not met; create before render: {legal_scan_dir}"
        )


def validate_chart_text(chart: ChartSpec) -> None:
    text = "\n".join([chart.title, chart.headline, chart.caption, chart.disclosure, *chart.data_inputs])
    lowered = text.lower()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in lowered:
            raise ValueError(f"Forbidden private/proprietary path or token in chart {chart.chart_id}: {pattern}")
    if "representative" not in lowered:
        raise ValueError(f"Chart {chart.chart_id} is missing representative-class disclosure")


def safe_text(text: str) -> str:
    return text.replace("—", "-").replace("–", "-").replace("×", "x")


def render_png(chart: ChartSpec, path: Path) -> None:
    width, height = 1600, 900
    image = Image.new("RGB", (width, height), "#F7FAFC")
    draw = ImageDraw.Draw(image)
    try:
        title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 54)
        head_font = ImageFont.truetype("DejaVuSans.ttf", 34)
        body_font = ImageFont.truetype("DejaVuSans.ttf", 26)
        small_font = ImageFont.truetype("DejaVuSans.ttf", 20)
    except OSError:
        title_font = head_font = body_font = small_font = ImageFont.load_default()

    draw.rectangle((0, 0, width, 110), fill="#0B2341")
    draw.text((48, 28), f"{chart.chart_id}: {chart.title}", fill="white", font=title_font)
    y = 145
    for line in wrap_text(chart.headline, 76):
        draw.text((48, y), line, fill="#0B2341", font=head_font)
        y += 43
    y += 10
    colors = ["#2EA44F", "#F2C94C", "#EB5757", "#2F80ED", "#6C5CE7", "#00A3A3"]
    for idx, row in enumerate(chart.rows[:7]):
        top = y + idx * 78
        draw.rectangle((48, top, width - 48, top + 58), fill="white", outline="#CBD5E1", width=2)
        draw.rectangle((48, top, 70, top + 58), fill=row_color(row))
        draw.text((90, top + 13), "  |  ".join(str(cell) for cell in row), fill="#1F2937", font=body_font)
    legend_y = min(y + len(chart.rows[:7]) * 78 + 8, height - 165)
    draw.text((48, legend_y), "Colour cue: green >=80% pass/utilisation margin OK, amber 50-79%, red <50% or high utilisation risk", fill="#334155", font=small_font)
    disclosure_y = height - 112
    draw.rectangle((0, disclosure_y - 12, width, height), fill="#EAF2F8")
    for line in wrap_text(chart.disclosure, 118):
        draw.text((48, disclosure_y), line, fill="#334155", font=small_font)
        disclosure_y += 27
    image.save(path)


def wrap_text(text: str, width: int) -> list[str]:
    words = safe_text(text).split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join([*current, word])
        if len(candidate) > width and current:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines


def row_color(row: tuple[str, ...]) -> str:
    text = " ".join(str(cell) for cell in row)
    percentages = [float(match) for match in re.findall(r"(\d+(?:\.\d+)?)%", text)]
    if not percentages:
        return "#2F80ED"
    # Capability rows use pass rate. C3 utilisation rows list utilisation;
    # lower crane utilisation is the safer margin, so mark >70% as amber.
    pct = max(percentages)
    if "util" in text.lower() and pct > 70:
        return "#F2C94C"
    if pct >= 80:
        return "#2EA44F"
    if pct >= 50:
        return "#F2C94C"
    return "#EB5757"


def render_svg(chart: ChartSpec, path: Path) -> None:
    rows = "\n".join(
        f'<rect x="48" y="{232 + idx * 54}" width="20" height="34" fill="{row_color(row)}"/>'
        f'<text x="80" y="{260 + idx * 54}" class="row">{escape_xml(" | ".join(row))}</text>'
        for idx, row in enumerate(chart.rows[:8])
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <style>.title{{font:700 52px DejaVu Sans,Arial;fill:#fff}}.headline{{font:32px DejaVu Sans,Arial;fill:#0B2341}}.row{{font:26px DejaVu Sans,Arial;fill:#1F2937}}.small{{font:20px DejaVu Sans,Arial;fill:#334155}}</style>
  <rect width="1600" height="900" fill="#F7FAFC"/>
  <rect width="1600" height="112" fill="#0B2341"/>
  <text x="48" y="72" class="title">{chart.chart_id}: {escape_xml(chart.title)}</text>
  <text x="48" y="170" class="headline">{escape_xml(safe_text(chart.headline[:128]))}</text>
  <text x="48" y="210" class="small">Colour cue: green &gt;=80% pass/utilisation margin OK; amber 50-79% or high utilisation risk; red &lt;50%.</text>
  {rows}
  <rect y="780" width="1600" height="120" fill="#EAF2F8"/>
  <text x="48" y="824" class="small">{escape_xml(safe_text(chart.disclosure))}</text>
</svg>'''
    path.write_text(svg, encoding="utf-8")


def render_pdf(chart: ChartSpec, png_path: Path, pdf_path: Path) -> None:
    # Pillow writes a single-page PDF from the brochure PNG. Caption text is also
    # archived in the adjacent sidecar and named in the manifest.
    with Image.open(png_path) as image:
        image.convert("RGB").save(pdf_path, "PDF", resolution=150.0)


def escape_xml(text: str) -> str:
    return safe_text(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def display_path(path: Path) -> str:
    """Return a non-leaky path for committed manifests/sidecars."""
    candidate = path
    try:
        if candidate.is_absolute():
            return candidate.resolve().relative_to(Path.cwd().resolve()).as_posix()
        return candidate.as_posix()
    except ValueError:
        # If a caller renders to /tmp or another absolute path, do not serialize
        # workstation-local prefixes into public collateral metadata.
        return candidate.name


def write_sidecars(chart: ChartSpec, output_dir: Path, assets: dict[str, Path]) -> tuple[Path, Path]:
    caption_path = output_dir / f"{chart.slug}.caption.txt"
    metadata_path = output_dir / f"{chart.slug}.metadata.json"
    caption_path.write_text(
        "\n".join(
            [
                f"{chart.chart_id}: {chart.title}",
                f"Headline: {chart.headline}",
                f"Caption: {chart.caption}",
                f"Disclosure: {chart.disclosure}",
                "Data inputs:",
                *(f"- {path}" for path in chart.data_inputs),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    metadata_path.write_text(
        json.dumps(
            {
                "issue": ISSUE_NUMBER,
                "chart_id": chart.chart_id,
                "title": chart.title,
                "headline": chart.headline,
                "data_inputs": chart.data_inputs,
                "disclosure": chart.disclosure,
                "assets": {key: display_path(value) for key, value in assets.items()},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return caption_path, metadata_path


def legal_scan_sidecars(output_dir: Path, legal_scan_dir: Path) -> Path:
    findings: list[dict[str, str]] = []
    scanned: list[str] = []
    for path in sorted(output_dir.glob("*.txt")) + sorted(output_dir.glob("*.json")) + sorted(output_dir.glob("*.svg")):
        text = path.read_text(encoding="utf-8", errors="replace")
        scanned.append(display_path(path))
        lowered = text.lower()
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in lowered:
                findings.append({"path": str(path), "pattern": pattern})
    result = {
        "issue": ISSUE_NUMBER,
        "status": "failed" if findings else "passed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scanner": "render_brochure_charts.py sidecar legal scan",
        "scanned_files": scanned,
        "findings": findings,
        "note": "Binary PNG/PDF files are covered through adjacent caption/metadata/SVG sidecars.",
    }
    path = legal_scan_dir / "2026-04-30-chart-pack-scan.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if findings:
        raise ValueError(f"Legal sidecar scan failed: {findings}")
    return path


def render_chart_pack(digitalmodel_root: Path, output_dir: Path, legal_scan_dir: Path) -> Path:
    assert_output_dirs(output_dir, legal_scan_dir)
    pack = build_chart_pack(digitalmodel_root)
    rendered: list[dict[str, Any]] = []
    for chart in pack.charts:
        validate_chart_text(chart)
        png_path = output_dir / f"{chart.slug}.brochure.png"
        svg_path = output_dir / f"{chart.slug}.print.svg"
        pdf_path = output_dir / f"{chart.slug}.1page.pdf"
        render_png(chart, png_path)
        render_svg(chart, svg_path)
        render_pdf(chart, png_path, pdf_path)
        caption_path, metadata_path = write_sidecars(
            chart,
            output_dir,
            {"png": png_path, "svg": svg_path, "pdf": pdf_path},
        )
        rendered.append(
            {
                "chart_id": chart.chart_id,
                "title": chart.title,
                "headline": chart.headline,
                "png": display_path(png_path),
                "svg": display_path(svg_path),
                "pdf": display_path(pdf_path),
                "caption_sidecar": display_path(caption_path),
                "metadata_sidecar": display_path(metadata_path),
                "data_inputs": chart.data_inputs,
            }
        )
    legal_scan_path = legal_scan_sidecars(output_dir, legal_scan_dir)
    manifest = {
        "issue": ISSUE_NUMBER,
        "chart_count": len(rendered),
        "generated_at": pack.generated_at,
        "total_cases": pack.total_cases,
        "legal_scan_status": "passed",
        "legal_scan": display_path(legal_scan_path),
        "charts": rendered,
    }
    manifest_path = output_dir / "vessel-capability-chart-pack-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--digitalmodel-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("docs/reports/gtm/assets"))
    parser.add_argument("--legal-scan-dir", type=Path, default=Path("docs/reports/gtm/legal-scans"))
    parser.add_argument(
        "--create-output-dirs",
        action="store_true",
        help="Implementation-slice mkdir gate: create output/legal directories before rendering.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.create_output_dirs:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        args.legal_scan_dir.mkdir(parents=True, exist_ok=True)
    manifest = render_chart_pack(args.digitalmodel_root, args.output_dir, args.legal_scan_dir)
    print(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
