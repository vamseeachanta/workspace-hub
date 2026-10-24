"""Audit a local field results bundle against an external digest and source bytes.

This consumer implements the existing projection, not a field registry or publisher.
Contract basis: upstream build_explorer_results_bundle.py, build_bundle(), schema
1.0.0; source locators and revision are recorded in the accompanying guide.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path, PurePosixPath


class AuditError(ValueError):
    """A rule identifier only; diagnostics never echo input data or local paths."""


def _require(condition: bool, rule: str) -> None:
    if not condition:
        raise AuditError(rule)


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value == value.strip()


def _digest(value: object) -> bool:
    # Digest width comes from the standard-library SHA-256 implementation.
    width = len(hashlib.sha256().hexdigest())
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]+", value) is not None and len(value) == width


def _read(path: Path) -> bytes:
    try:
        _require(path.is_file(), "input_read")
        return path.read_bytes()
    except OSError:
        raise AuditError("input_read") from None


def _json(raw: bytes) -> dict:
    def pairs(items):
        result = {}
        for key, value in items:
            _require(key not in result, "strict_json")
            result[key] = value
        return result

    def finite(value):
        number = float(value)
        _require(math.isfinite(number), "strict_json")
        return number

    def constant(_value):
        raise AuditError("strict_json")

    try:
        value = json.loads(raw, object_pairs_hook=pairs, parse_float=finite, parse_constant=constant)
    except (ValueError, UnicodeError, RecursionError):
        raise AuditError("strict_json") from None
    _require(isinstance(value, dict), "strict_json")
    return value


def _same_json(left: object, right: object) -> bool:
    """Compare JSON values without treating booleans as numeric ones."""
    def canonical(value):
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)

    return canonical(left) == canonical(right)


def _source_path(root: Path, value: object) -> Path:
    _require(_text(value), "source_path")
    relative = PurePosixPath(value)
    _require(not relative.is_absolute() and relative.as_posix() == value, "source_path")
    _require(bool(relative.parts), "source_path")
    _require(all(part not in (".", "..") and re.fullmatch(r"[A-Za-z0-9_.-]+", part)
                 for part in relative.parts), "source_path")
    candidate = root
    for part in relative.parts:
        candidate = candidate / part
        _require(not candidate.is_symlink(), "source_path")
    _require(candidate.resolve().is_relative_to(root), "source_path")
    return candidate


def _sources(bundle: dict, root: Path) -> dict:
    sources = bundle.get("sources")
    _require(isinstance(sources, list), "source_roles")
    loaded = {}
    paths = set()
    for source in sources:
        _require(isinstance(source, dict), "source_roles")
        role = source.get("role")
        _require(isinstance(role, str) and role in {"field_detail", "global_funnel"}
                 and role not in loaded, "source_roles")
        path = _source_path(root, source.get("path"))
        _require(path not in paths, "source_roles")
        paths.add(path)
        raw = _read(path)
        size = source.get("bytes")
        _require(type(size) is int and size == len(raw)
                 and _digest(source.get("sha256"))
                 and source["sha256"] == hashlib.sha256(raw).hexdigest(), "source_integrity")
        loaded[role] = _json(raw)
    _require(set(loaded) == {"field_detail", "global_funnel"}, "source_roles")
    return loaded


def _projection(bundle: dict, sources: dict) -> tuple[dict, dict, dict]:
    fields, wells, atlas = (bundle.get(key) for key in ("fields", "wells", "atlas"))
    _require(isinstance(fields, dict) and isinstance(wells, dict)
             and isinstance(wells.get("wells"), list) and isinstance(wells.get("fields"), dict)
             and isinstance(atlas, dict) and isinstance(atlas.get("countries"), list)
             and isinstance(atlas.get("fields"), list), "bundle_shape")
    detail, funnel = sources["field_detail"], sources["global_funnel"]
    _require(_same_json(fields, detail.get("fields")) and _same_json(wells, detail.get("wells"))
             and _same_json(atlas["countries"], funnel.get("countries"))
             and _same_json(atlas["fields"], funnel.get("fields")), "source_projection")
    return fields, wells, atlas


def _field_relations(fields: dict, wells: dict) -> dict:
    counts = dict.fromkeys(fields, 0)
    provenance = {}
    for field_id, field in fields.items():
        _require(_text(field_id) and isinstance(field, dict)
                 and field.get("id") == field_id, "field_identity")
        provenance[field_id] = field.get("provenance")
    seen = set()
    for well in wells["wells"]:
        _require(isinstance(well, dict), "well_identity")
        identity = well.get("api")
        _require(_text(identity) and identity not in seen, "well_identity")
        seen.add(identity)
        parent = well.get("field_id")
        _require(_text(parent) and parent in fields, "well_parent")
        counts[parent] += 1
    for key, value in wells["fields"].items():
        _require(key in fields and isinstance(value, dict), "well_rollup")
    for key, field in fields.items():
        # wellsCount is optional in the exporter. When present, it is an exact
        # count, not a tolerance or a claim about absent, unexported wells.
        if "wellsCount" in field:
            count = field["wellsCount"]
            _require(type(count) is int and count == counts[key], "well_count")
    return {"wells_per_field": dict(sorted(counts.items())),
            "zero_well_fields": sorted(key for key, count in counts.items() if count == 0),
            "provenance": provenance}


def _atlas_relations(atlas: dict) -> dict:
    countries = set()
    for row in atlas["countries"]:
        _require(isinstance(row, dict), "country_identity")
        country = row.get("country")
        _require(_text(country) and country not in countries, "country_identity")
        countries.add(country)
    seen = set()
    density = Counter()
    for row in atlas["fields"]:
        _require(isinstance(row, dict), "atlas_identity")
        identity = row.get("catalog_id")
        _require(_text(identity) and identity not in seen, "atlas_identity")
        seen.add(identity)
        country = row.get("country")
        _require(_text(country) and country in countries, "atlas_country")
        tier = row.get("density_tier")
        # Existing atlas honesty tiers, upstream program issue 939 (2026).
        _require(isinstance(tier, str) and tier in {"rich", "sample", "roadmap"}, "atlas_density")
        density[tier] += 1
    return dict(sorted(density.items()))


def audit_bundle(bundle_path: Path, source_root: Path, expected_sha256: str) -> dict:
    """Return deterministic local-integrity evidence or raise a rule-only error.

    The caller supplies a digest obtained independently of this directory. Matching
    caller-supplied bytes does not authenticate publication rights or remote origin.
    Sources must be regular local files below the chosen root, without symlinks.
    """
    _require(_digest(expected_sha256), "bundle_digest")
    raw = _read(Path(bundle_path))
    _require(hashlib.sha256(raw).hexdigest() == expected_sha256, "bundle_digest")
    bundle = _json(raw)
    # Exact existing exporter version, not an invented engineering acceptance limit.
    _require(bundle.get("schema_version") == "1.0.0"
             and bundle.get("projection") == "field_explorer_results"
             and bundle.get("hf_dataset") == "worldenergydata", "bundle_contract")
    sources = _sources(bundle, Path(source_root).resolve())
    fields, wells, atlas = _projection(bundle, sources)
    counts = {"fields": len(fields), "wells": len(wells["wells"]),
              "countries": len(atlas["countries"]), "atlas_fields": len(atlas["fields"])}
    declared = bundle.get("record_counts")
    _require(isinstance(declared, dict) and set(declared) == set(counts)
             and all(type(declared[key]) is int and declared[key] == count
                     for key, count in counts.items()), "record_counts")
    relations = _field_relations(fields, wells)
    _require(_same_json(bundle.get("field_provenance"), relations.pop("provenance")), "field_provenance")
    density = _atlas_relations(atlas)
    return {
        "integrity_status": "PASS", "eligibility_status": "NOT_EVALUATED",
        "bundle_sha256": expected_sha256, "counts": counts, **relations,
        "atlas_density": density,
        "not_evaluated": {
            "canonical_registry_membership": "The authoritative field registry is not an input.",
            "source_freshness": "No source-vintage or intended-use freshness criterion is provided.",
            "redistribution_rights": "Source hashes do not establish redistribution rights.",
            "engineering_readiness": "No qualified engineering evidence or criteria are provided.",
            "economics_basis": "Economic values are preserved, without assessment of their basis.",
            "global_completeness": "Exported rows do not establish complete worldwide coverage.",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--expected-sha256", required=True)
    args = parser.parse_args(argv)
    try:
        report = audit_bundle(args.bundle, args.source_root, args.expected_sha256)
    except AuditError as exc:
        print(json.dumps({"integrity_status": "FAIL", "rule": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
