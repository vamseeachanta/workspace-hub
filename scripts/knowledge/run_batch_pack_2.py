"""Batch Pack 2 conference-summary promotion runner.

This module intentionally reads only indexed JSONL/YAML artifacts. It never
opens source PDFs under /mnt/ace/docs/conferences.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import logging
import math
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


STOPWORDS_SHA = "b412e096c4e7485ae8b4838e3309cf55613b951cb18b3b0b4d3fe25bd62ff19d"
SCHEMA_VERSION = "1.2"
GENERATOR_VERSION = "1.0"
SOURCE_ISSUE = 2369
CANONICAL_COLLECTIONS = ["DOT", "OMAE", "OTC"]
ALLOWED_COLLECTIONS = set(CANONICAL_COLLECTIONS)
ALLOWED_DOMAINS = {
    "pipeline",
    "subsea",
    "VIV",
    "hydrodynamics",
    "marine",
    "structural",
    "misc",
}
SECONDARY_DOMAINS = ALLOWED_DOMAINS - {"misc"}
ALLOWED_WIKIS = {"engineering", "marine-engineering", "naval-architecture"}
DOMAIN_TARGET_WIKI = {
    "pipeline": "engineering",
    "subsea": "marine-engineering",
    "VIV": "marine-engineering",
    "hydrodynamics": "naval-architecture",
    "marine": "marine-engineering",
    "structural": "engineering",
    "misc": "engineering",
}

_DENY_PREFIXES = (os.path.realpath("/mnt/ace/docs/conferences/"),)
_ALLOWED_READ_MODES = {"r", "rb", "rt"}
_TOKEN_RE = re.compile(r"[a-z0-9_]+")
_LOG = logging.getLogger(__name__)


class PathGuardError(RuntimeError):
    pass


class SchemaValidationError(ValueError):
    pass


@dataclass(frozen=True)
class Paper:
    paper_id: str
    conference: str
    title: str
    path: str | None
    year: int | None


@dataclass(frozen=True)
class RunResult:
    processed_collections: list[str]
    deferred_collections: dict[str, str]
    paper_count: int
    skipped_count: int
    stub_count: int


DOMAIN_KEYWORDS: dict[str, dict[str, int]] = {
    "VIV": {
        "viv": 5,
        "vortex_induced": 5,
        "vibration": 5,
    },
    "pipeline": {
        "pipeline": 4,
        "pipelines": 4,
        "flowline": 4,
        "flowlines": 4,
        "riser": 4,
        "risers": 4,
        "jumper": 4,
        "jumpers": 4,
        "integrity": 2,
        "corrosion": 2,
    },
    "subsea": {
        "subsea": 4,
        "christmas_tree": 4,
        "manifold": 4,
        "wellhead": 4,
        "deepwater": 1,
    },
    "hydrodynamics": {
        "hydrodynamic": 3,
        "hydrodynamics": 3,
        "seakeeping": 3,
        "wave": 2,
        "waves": 2,
        "current": 2,
    },
    "structural": {
        "structural": 2,
        "fracture": 2,
        "stress": 2,
        "stress_concentration": 2,
        "buckling": 2,
    },
    "marine": {
        "marine": 1,
        "offshore": 1,
        "mooring": 1,
        "floater": 1,
        "floating": 1,
        "semi_submersible": 1,
        "offshore_wind": 1,
    },
}


def safe_open(path: str | os.PathLike[str], mode: str = "r", *args: Any, **kwargs: Any):
    if mode not in _ALLOWED_READ_MODES:
        raise ValueError(
            f"safe_open: write modes not allowed; got mode={mode!r}; "
            f"allowed={sorted(_ALLOWED_READ_MODES)}"
        )
    real_path = os.path.realpath(path)
    if any(real_path.startswith(prefix) for prefix in _DENY_PREFIXES):
        raise PathGuardError(f"Refused open under deny-prefix: {real_path}")
    return open(path, mode, *args, **kwargs)


def tokenize_v1(text: str) -> list[str]:
    return _TOKEN_RE.findall((text or "").lower())


def classify_paper_domain_ranked(title: str) -> tuple[str, list[str]]:
    tokens = tokenize_v1(title)
    scores: dict[str, int] = {domain: 0 for domain in DOMAIN_KEYWORDS}
    for token in tokens:
        for domain, keywords in DOMAIN_KEYWORDS.items():
            scores[domain] += keywords.get(token, 0)

    if all(score == 0 for score in scores.values()):
        if {"pipe", "line"}.issubset(tokens):
            scores["pipeline"] += 1
        elif {"marine", "system"}.issubset(tokens):
            scores["marine"] += 1
        else:
            return "misc", []
        _LOG.debug(
            "classifier fallback fired; tied scores will resolve alphabetically "
            "(marine < pipeline)"
        )

    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    primary, primary_score = ranked[0]
    secondary = [
        domain
        for domain, score in ranked[1:]
        if domain != "misc" and score > 0 and score >= max(1, primary_score - 2)
    ]
    return primary, secondary


def validate_cross_link_candidate(candidate: dict[str, Any]) -> None:
    required = {
        "stub_id": str,
        "schema_version": str,
        "source_issue": int,
        "title": str,
        "engineering_domain": str,
        "secondary_domains": list,
        "target_wiki": str,
        "target_wiki_path_hint": str,
        "paper_count": int,
        "top_paper_ids": list,
        "topic_label": str,
        "cluster_quality_caveat": str,
        "cross_link_candidates": list,
        "generated_at": str,
        "generator": str,
        "generator_version": str,
    }
    for key, expected_type in required.items():
        if key not in candidate:
            raise SchemaValidationError(f"missing required field: {key}")
        if not isinstance(candidate[key], expected_type):
            raise SchemaValidationError(f"{key} must be {expected_type.__name__}")
    if candidate["schema_version"] != SCHEMA_VERSION:
        raise SchemaValidationError("schema_version must be 1.2")
    if candidate["source_issue"] != SOURCE_ISSUE:
        raise SchemaValidationError("source_issue must be 2369")
    if candidate["engineering_domain"] not in ALLOWED_DOMAINS:
        raise SchemaValidationError("engineering_domain is not allowed")
    bad_secondaries = [
        item for item in candidate["secondary_domains"] if item not in SECONDARY_DOMAINS
    ]
    if bad_secondaries:
        raise SchemaValidationError(
            f"secondary_domains contains disallowed values: {bad_secondaries}"
        )
    if candidate["target_wiki"] not in ALLOWED_WIKIS:
        raise SchemaValidationError("target_wiki is not allowed")


def _load_catalog(catalog_path: Path) -> tuple[set[str], dict[str, str]]:
    with safe_open(catalog_path, "r", encoding="utf-8") as handle:
        catalog = yaml.safe_load(handle)
    complete: set[str] = set()
    deferred: dict[str, str] = {}
    for entry in catalog.get("conferences", []):
        name = entry.get("name")
        status = entry.get("indexing_status")
        if status == "phase_a_complete":
            complete.add(name)
        else:
            deferred[name] = str(status or "unknown")
    return complete, deferred


def _load_phase_a_records(
    phase_a_jsonl: Path, selected_collections: set[str]
) -> tuple[list[Paper], list[dict[str, Any]]]:
    papers: list[Paper] = []
    skipped: list[dict[str, Any]] = []
    with safe_open(phase_a_jsonl, "r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                skipped.append({"line": line_number, "error": str(exc), "raw": line.rstrip()})
                continue
            conference = record.get("conference")
            if conference not in selected_collections:
                continue
            title = (record.get("title") or "").strip()
            if not title:
                skipped.append(
                    {
                        "line": line_number,
                        "conference": conference,
                        "error": "missing title",
                    }
                )
                continue
            paper_id = f"{conference}-{line_number:06d}"
            papers.append(
                Paper(
                    paper_id=paper_id,
                    conference=conference,
                    title=" ".join(title.split()),
                    path=record.get("path"),
                    year=record.get("year"),
                )
            )
    return papers, skipped


def _stopwords() -> set[str]:
    stopwords_path = Path(__file__).with_name("data") / "stopwords_en_v1.txt"
    digest = hashlib.sha256(stopwords_path.read_bytes()).hexdigest()
    if STOPWORDS_SHA == "<unpinned>":
        raise RuntimeError("STOPWORDS_SHA is unpinned; run pin-stopwords-sha first")
    if digest != STOPWORDS_SHA:
        raise RuntimeError(
            f"stopwords SHA drift: expected {STOPWORDS_SHA}, found {digest}"
        )
    return {
        line.strip()
        for line in stopwords_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def _topic_label(papers: list[Paper], stopwords: set[str]) -> str:
    counts: Counter[str] = Counter()
    for paper in papers:
        counts.update(token for token in tokenize_v1(paper.title) if token not in stopwords)
    if not counts:
        return "misc"
    terms = [term for term, _count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:3]]
    return " | ".join(terms)


def _slug(text: str) -> str:
    tokens = tokenize_v1(text.replace("|", " "))
    return "-".join(tokens[:8]) or "conference-topic"


def _build_stub_candidates(
    papers: list[Paper], generated_at: str, stopwords: set[str]
) -> list[dict[str, Any]]:
    by_domain: dict[str, list[tuple[Paper, list[str]]]] = defaultdict(list)
    for paper in papers:
        primary, secondary = classify_paper_domain_ranked(paper.title)
        by_domain[primary].append((paper, secondary))

    candidates: list[dict[str, Any]] = []
    for domain in sorted(by_domain):
        domain_rows = sorted(by_domain[domain], key=lambda item: item[0].paper_id)
        domain_papers = [paper for paper, _secondary in domain_rows]
        secondaries = sorted(
            {
                secondary
                for _paper, secondary_domains in domain_rows
                for secondary in secondary_domains
                if secondary != domain
            }
        )
        label = _topic_label(domain_papers, stopwords)
        wiki = DOMAIN_TARGET_WIKI[domain]
        candidate = {
            "stub_id": f"bp2-{domain.lower()}-001",
            "schema_version": SCHEMA_VERSION,
            "source_issue": SOURCE_ISSUE,
            "title": f"{domain} conference paper topic cluster",
            "engineering_domain": domain,
            "secondary_domains": secondaries,
            "target_wiki": wiki,
            "target_wiki_path_hint": f"concepts/{_slug(label)}.md",
            "paper_count": len(domain_papers),
            "top_paper_ids": [paper.paper_id for paper in domain_papers[:10]],
            "topic_label": label,
            "duplicate_candidate_path": None,
            "cluster_quality_caveat": "single-pass-deterministic",
            "cross_link_candidates": [
                {
                    "target_wiki": DOMAIN_TARGET_WIKI[secondary],
                    "target_path": f"concepts/{secondary.lower()}.md",
                    "confidence": 0.5,
                }
                for secondary in secondaries[:5]
            ],
            "generated_at": generated_at,
            "generator": "scripts/knowledge/run_batch_pack_2.py",
            "generator_version": GENERATOR_VERSION,
        }
        validate_cross_link_candidate(candidate)
        candidates.append(candidate)
    return candidates


def _write_report(
    report_path: Path,
    processed_collections: list[str],
    deferred_collections: dict[str, str],
    candidates: list[dict[str, Any]],
    paper_count: int,
    skipped_count: int,
    generated_at: str,
) -> None:
    lines = [
        "# Batch Pack 2 Conference Summary Stubs",
        "",
        f"Generated: {generated_at}",
        f"Processed collections: {', '.join(processed_collections)}",
        f"Paper records processed: {paper_count}",
        f"Skipped records: {skipped_count}",
        "",
        "## Deferred Collections",
        "",
    ]
    for name in sorted(deferred_collections):
        if name == "ISOPE" or name in CANONICAL_COLLECTIONS:
            lines.append(f"- {name}: {deferred_collections[name]}")
    lines.extend(["", "## Topic Stubs", ""])
    for candidate in candidates:
        lines.extend(
            [
                f"### {candidate['title']}",
                "",
                f"- Stub ID: {candidate['stub_id']}",
                f"- Engineering domain: {candidate['engineering_domain']}",
                f"- Secondary domains: {', '.join(candidate['secondary_domains']) or 'none'}",
                f"- Target wiki: {candidate['target_wiki']}",
                f"- Paper count: {candidate['paper_count']}",
                f"- Topic label: {candidate['topic_label']}",
                f"- Top paper IDs: {', '.join(candidate['top_paper_ids'])}",
                "- Cluster quality caveat: single-pass-deterministic",
                "",
            ]
        )
    lines.extend(
        [
            "## ISOPE re-index follow-on (proposed body)",
            "",
            "ISOPE remains deferred for Batch Pack 2 because the authoritative "
            "`conference-paper-catalog.yaml` entry is `not_indexed` and phase-A "
            "summary records are not present in `conference-phase-a-results.jsonl`. "
            "Run a readiness/reconciliation slice before including ISOPE in a "
            "summary-backed promotion.",
            "",
        ]
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")


def run_batch_pack_2(
    catalog_path: str | os.PathLike[str],
    phase_a_jsonl: str | os.PathLike[str],
    output_report_path: str | os.PathLike[str],
    *,
    cross_link_path: str | os.PathLike[str] = "data/document-index/batch-pack-2-cross-link-candidates.jsonl",
    skipped_path: str | os.PathLike[str] = "data/document-index/batch-pack-2-skipped.jsonl",
    collections: list[str] | None = None,
    now: str | None = None,
) -> RunResult:
    selected = collections or list(CANONICAL_COLLECTIONS)
    invalid = sorted(set(selected) - ALLOWED_COLLECTIONS)
    if invalid:
        raise ValueError(f"invalid collections: {invalid}; allowed={sorted(ALLOWED_COLLECTIONS)}")

    generated_at = now or os.environ.get("BP2_NOW") or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    complete, deferred = _load_catalog(Path(catalog_path))
    selected_set = set(selected)
    not_complete = sorted(selected_set - complete)
    for name in not_complete:
        _LOG.warning("collection %s selected but not phase_a_complete; skipping", name)
        selected_set.remove(name)
    processed_collections = [name for name in CANONICAL_COLLECTIONS if name in selected_set]

    papers, skipped = _load_phase_a_records(Path(phase_a_jsonl), selected_set)
    stopwords = _stopwords()
    candidates = _build_stub_candidates(papers, generated_at, stopwords)

    cross_path = Path(cross_link_path)
    cross_path.parent.mkdir(parents=True, exist_ok=True)
    cross_path.write_text(
        "".join(json.dumps(candidate, sort_keys=True) + "\n" for candidate in candidates),
        encoding="utf-8",
    )

    skipped_out = Path(skipped_path)
    skipped_out.parent.mkdir(parents=True, exist_ok=True)
    skipped_out.write_text(
        "".join(json.dumps(item, sort_keys=True) + "\n" for item in skipped),
        encoding="utf-8",
    )

    _write_report(
        Path(output_report_path),
        processed_collections,
        deferred,
        candidates,
        len(papers),
        len(skipped),
        generated_at,
    )

    if collections is None and len(papers) + len(skipped) != 14180:
        raise SystemExit(2)

    return RunResult(
        processed_collections=processed_collections,
        deferred_collections=deferred,
        paper_count=len(papers),
        skipped_count=len(skipped),
        stub_count=len(candidates),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", default="data/document-index/conference-paper-catalog.yaml")
    parser.add_argument("--phase-a-jsonl", default="data/document-index/conference-phase-a-results.jsonl")
    parser.add_argument("--output-report", default="docs/reports/batch-pack-2-conference-summary-stubs.md")
    parser.add_argument("--cross-link-path", default="data/document-index/batch-pack-2-cross-link-candidates.jsonl")
    parser.add_argument("--skipped-path", default="data/document-index/batch-pack-2-skipped.jsonl")
    parser.add_argument("--collections", nargs="+", choices=sorted(ALLOWED_COLLECTIONS))
    parser.add_argument("--now")
    args = parser.parse_args(argv)
    run_batch_pack_2(
        args.catalog,
        args.phase_a_jsonl,
        args.output_report,
        cross_link_path=args.cross_link_path,
        skipped_path=args.skipped_path,
        collections=args.collections,
        now=args.now,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
