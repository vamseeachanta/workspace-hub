"""
Marginal-quota validator, floor-occupancy checker, and artifact writers
for the conversion-QA oracle sample.

Imported by conftest.py and test_conversion_quality.py via bare sibling import
(works because markdown_qa/ has NO __init__.py — pytest rootdir-walk adds the
directory to sys.path during conftest loading).
"""

import json
import os
from pathlib import Path
from typing import Iterable, Mapping

# ── Stratification quotas ─────────────────────────────────────────────────────

PRODUCT_QUOTAS = {"OrcaFlex": 12, "OrcaWave": 5, "OrcFxAPI": 3}
CATEGORY_QUOTAS = {"introduction": 4, "data": 5, "theory": 4, "results": 3, "API": 4}
COMPLEXITY_QUOTAS = {"Simple": 6, "Medium": 8, "Hard": 6}
TOTAL_ENTRIES = 20
HARD_ENCODING_STRESS_MIN = 2

# ── Floor-occupancy thresholds ────────────────────────────────────────────────

PER_TOPIC_FLOOR = {
    "heading": 0.90,
    "link": 0.90,
    "table": 0.85,
    "code": 0.90,
    "image": 0.80,
    "list": 0.85,
}
HARD_MIN = 0.70
MAX_BELOW_FLOOR = 2  # per dim, count of topics permitted below the per-topic floor


# ── Manifest validation ───────────────────────────────────────────────────────

def validate_manifest(entries: list[dict]) -> list[str]:
    """Return a list of violation strings; empty = valid.

    Checks:
      1. total entry count == TOTAL_ENTRIES
      2. three axis marginal counts match quotas
      3. Hard-tier encoding_stress count >= HARD_ENCODING_STRESS_MIN
      4. all provenance fields populated
      5. all oracle_review_method == 'from-source'

    Does NOT check joint-cell occupancy (marginal-only by design).
    """
    errors: list[str] = []

    if len(entries) != TOTAL_ENTRIES:
        errors.append(f"entry count {len(entries)} != {TOTAL_ENTRIES}")

    for axis, quotas in [
        ("product", PRODUCT_QUOTAS),
        ("category", CATEGORY_QUOTAS),
        ("complexity", COMPLEXITY_QUOTAS),
    ]:
        actual: dict[str, int] = {}
        for e in entries:
            actual[e.get(axis, "MISSING")] = actual.get(e.get(axis, "MISSING"), 0) + 1
        for key, expected in quotas.items():
            if actual.get(key, 0) != expected:
                errors.append(
                    f"{axis}[{key}] count {actual.get(key, 0)} != {expected}"
                )

    hard_stress = sum(
        1 for e in entries
        if e.get("complexity") == "Hard" and e.get("encoding_stress") is True
    )
    if hard_stress < HARD_ENCODING_STRESS_MIN:
        errors.append(
            f"Hard-tier encoding_stress count {hard_stress} < {HARD_ENCODING_STRESS_MIN}"
        )

    required_fields = [
        "slug", "product", "category", "complexity", "encoding_stress",
        "source_url", "fetched_at", "html_sha256", "html_path", "oracle_md_path",
        "oracle_authored_by", "oracle_authored_at", "oracle_second_reviewer",
        "single_reviewer_timelag", "oracle_review_method",
    ]
    for e in entries:
        slug = e.get("slug", "UNKNOWN")
        for f in required_fields:
            if f not in e or e[f] is None or e[f] == "":
                errors.append(f"slug={slug}: missing field '{f}'")
        if e.get("oracle_review_method") != "from-source":
            errors.append(
                f"slug={slug}: oracle_review_method={e.get('oracle_review_method')!r} != 'from-source'"
            )

    return errors


# ── Floor-occupancy gate ──────────────────────────────────────────────────────

def check_floor_occupancy(per_topic: Iterable[Mapping]) -> list[dict]:
    """Return list of violation records; empty list = pass.

    per_topic: iterable of dicts with keys {slug, dim, score}.
    """
    by_dim: dict[str, list[float]] = {}
    for entry in per_topic:
        by_dim.setdefault(entry["dim"], []).append(entry["score"])

    violations: list[dict] = []
    for dim, scores in by_dim.items():
        floor = PER_TOPIC_FLOOR.get(dim, 1.0)
        below = [s for s in scores if s < floor]
        hard_breaches = [s for s in scores if s < HARD_MIN]
        if len(below) > MAX_BELOW_FLOOR:
            violations.append({
                "dim": dim,
                "rule": "below_floor",
                "count": len(below),
                "max": MAX_BELOW_FLOOR,
                "floor": floor,
            })
        if hard_breaches:
            violations.append({
                "dim": dim,
                "rule": "hard_min",
                "count": len(hard_breaches),
                "scores": hard_breaches,
                "hard_min": HARD_MIN,
            })
    return violations


# ── Artifact writers ──────────────────────────────────────────────────────────

def _artifacts_base(artifacts_dir: Path | None = None) -> Path:
    return artifacts_dir or Path(os.environ.get(
        "MARKDOWN_QA_ARTIFACTS_DIR",
        str(Path(__file__).parent / ".artifacts" / "per-topic"),
    ))


def write_per_topic_artifact(
    slug: str,
    dim: str,
    score: float,
    artifacts_dir: Path | None = None,
) -> Path:
    """Atomically write {slug}-{dim}.json under the artifacts dir. Returns the path."""
    base = _artifacts_base(artifacts_dir)
    base.mkdir(parents=True, exist_ok=True)
    out = base / f"{slug}-{dim}.json"
    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.write_text(json.dumps({"slug": slug, "dim": dim, "score": score}))
    tmp.replace(out)
    return out


def write_report(
    filename: str,
    per_topic: list[dict],
    violations: list[dict],
    artifacts_dir: Path | None = None,
) -> Path:
    """Write the aggregate report next to per-topic artifacts."""
    base = _artifacts_base(artifacts_dir)
    out = base.parent / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "per_topic": per_topic,
        "violations": violations,
        "floor_occupancy_summary": {
            "total_dims": len({e["dim"] for e in per_topic}),
            "violation_count": len(violations),
            "passed": len(violations) == 0,
        },
    }
    out.write_text(json.dumps(payload, indent=2))
    return out
