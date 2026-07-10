"""Build deterministic, public-safe Landman pilot decision artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.research import landman_pilot_decision as decision_logic  # noqa: E402
from scripts.research.landman_pilot_render import render_outputs  # noqa: E402


DEFAULT_EVIDENCE = ROOT / "docs/reports/landman/2026-07-09-pilot-evidence.yaml"
DEFAULT_DECISION = ROOT / "docs/reports/landman/2026-07-09-pilot-decision.yaml"
DEFAULT_HTML = ROOT / "docs/reports/landman/2026-07-09-pilot-decision.html"
sensitivity = decision_logic.sensitivity


def build_decision(evidence: dict) -> dict:
    """Expose decision generation while retaining a patchable sensitivity seam."""
    return decision_logic.build_decision(evidence, sensitivity)


def write_outputs(
    evidence_path: Path, decision_path: Path, html_path: Path, check: bool
) -> bool:
    evidence = yaml.safe_load(evidence_path.read_text(encoding="utf-8"))
    decision, report = render_outputs(evidence)
    if check:
        return decision_path.read_bytes() == decision.encode(
            "utf-8"
        ) and html_path.read_bytes() == report.encode("utf-8")
    decision_path.parent.mkdir(parents=True, exist_ok=True)
    decision_path.write_text(decision, encoding="utf-8", newline="\n")
    html_path.write_text(report, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--decision", type=Path, default=DEFAULT_DECISION)
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return (
        0 if write_outputs(args.evidence, args.decision, args.html, args.check) else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
