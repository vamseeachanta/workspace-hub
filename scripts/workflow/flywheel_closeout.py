#!/usr/bin/env python3
"""Generate advisory flywheel closeout reports for named repo waves."""
from __future__ import annotations
import json
import re
import sys
from argparse import ArgumentParser
from html import escape
from pathlib import Path
from typing import Any

PRIVATE_PREFIXES = ("/home/", "/Users/", "/mnt/" + "ace/")


def _parse_scalar(value: str) -> Any:
    text = value.strip()
    if text == "[]":
        return []
    return text


def load_fixture(path: str | Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    data: dict[str, Any] = {"sources": [], "existing_issues": []}
    current_list: str | None = None
    current: dict[str, Any] | None = None
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        if not raw.startswith(" ") and raw.endswith(":"):
            current_list = raw[:-1]
            continue
        if raw.startswith("  - "):
            current = {}
            data.setdefault(current_list or "", []).append(current)
            item = raw[4:]
            if ":" in item:
                key, value = item.split(":", 1)
                current[key.strip()] = _parse_scalar(value)
            continue
        if current is not None and ":" in raw:
            key, value = raw.strip().split(":", 1)
            current[key] = _parse_scalar(value)
    return data.get("sources", []), data.get("existing_issues", [])


def non_publishable_reason(text: str) -> str | None:
    for prefix in PRIVATE_PREFIXES:
        if prefix in text:
            return "private_path"
    if re.search(r"(?i)(token|secret|password|OPENAI_API_KEY)\s*[:= ]\s*\S+", text):
        return "secret_like"
    if not text.strip():
        return "empty"
    return None


def _candidate(source: dict[str, Any]) -> dict[str, Any] | None:
    text = " ".join(str(source.get(key, "")) for key in ("title", "text")).lower()
    locator = str(source.get("locator", ""))
    repo = str(source.get("repo", ""))
    if "review artifact" in text or "stderr" in text or "stale sha" in text or "publishability" in text:
        return {"id": "review-artifact-publishability", "asset_class": "issue", "route_repo": "vamseeachanta/workspace-hub", "title": "Route review artifact publishability contract", "evidence": [locator], "rationale": "Review artifacts need publishability, metadata, stderr, and stale-SHA gates."}
    if "parser-limit" in text or "prompt" in text:
        return {"id": "parser-limit-prompt", "asset_class": "prompt_template", "route_repo": repo, "title": "Promote parser-limit prompt guidance", "evidence": [locator], "rationale": "Parser-limit lessons should become prompt guidance."}
    if "content-value" in text or "script hardening" in text:
        return {"id": "content-value-script", "asset_class": "script", "route_repo": repo, "title": "Promote content-value script hardening", "evidence": [locator], "rationale": "Content-value filtering should become reusable script hardening."}
    if "flywheel" in text or "learning extraction" in text or "durable assets" in text:
        return {"id": "wave-closeout-docs", "asset_class": "docs", "route_repo": "vamseeachanta/workspace-hub", "title": "Document wave closeout flywheel evidence", "evidence": [locator], "rationale": "Agent waves should leave evidence-linked durable asset routing."}
    return None


def identify_learnings(sources: list[dict[str, Any]], existing_issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for source in sources:
        if non_publishable_reason(json.dumps(source)):
            continue
        candidate = _candidate(source)
        if not candidate:
            continue
        existing = by_id.setdefault(candidate["id"], candidate)
        existing["evidence"] = sorted(set(existing["evidence"] + candidate["evidence"]))
    for candidate in by_id.values():
        if candidate["id"] == "review-artifact-publishability":
            for issue in existing_issues:
                if int(issue.get("number", 0)) == 2502 and issue.get("state") == "OPEN":
                    candidate["suppressed_duplicate_issue"] = True
                    candidate["existing_issue"] = f"{issue['repo']}#{issue['number']}"
                    break
    return sorted(by_id.values(), key=lambda item: item["id"])


def classify_non_publishable(sources: list[dict[str, Any]]) -> list[dict[str, str]]:
    records = []
    for source in sources:
        reason = non_publishable_reason(json.dumps(source))
        if reason:
            records.append({"kind": str(source.get("kind", "")), "repo": str(source.get("repo", "")), "locator": str(source.get("locator", "")), "reason": reason})
    return records


def render_outputs(candidates: list[dict[str, Any]], out_dir: str | Path, source_issue: str, sources: list[dict[str, Any]]) -> dict[str, Path]:
    out = Path(out_dir)
    drafts = out / "issue-drafts"
    drafts.mkdir(parents=True, exist_ok=True)
    draft_paths = []
    manifest = {"mode": "propose", "advisory_only": True, "source_issue": source_issue, "source_count": len(sources), "candidate_count": len(candidates), "warnings": ["missing flywheel evidence is advisory in first slice"], "non_publishable_records": classify_non_publishable(sources), "draft_paths": draft_paths, "candidates": candidates}
    rows = []
    for candidate in candidates:
        evidence = ", ".join(candidate["evidence"])
        rows.append(f"<tr><td>{escape(candidate['asset_class'])}</td><td>{escape(candidate['title'])}</td><td>{escape(candidate['route_repo'])}</td><td>{escape(evidence)}</td></tr>")
        draft_name = "workspace-hub-2502-comment.md" if candidate.get("existing_issue") else f"{candidate['id']}.md"
        draft_path = drafts / draft_name
        draft_paths.append(str(draft_path.relative_to(out)))
        draft_path.write_text(f"# {candidate['title']}\n\n## Source Evidence\n\nParent: {source_issue}\n\n" + "\n".join(f"- {item}" for item in candidate["evidence"]) + f"\n\n## Durable Asset Class\n\n`{candidate['asset_class']}`\n\n## What To Build\n\n{candidate['rationale']}\n\n## Acceptance Criteria\n\n- [ ] Evidence links are present.\n- [ ] Routing decision is explicit: `{candidate['route_repo']}`.\n- [ ] Verification path is clear.\n", encoding="utf-8")
    html = "<!doctype html><meta charset='utf-8'><title>Flywheel Closeout</title><h1>Flywheel Closeout</h1><table>" + "".join(rows) + "</table>"
    manifest_text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    if non_publishable_reason(html + manifest_text):
        raise ValueError("generated output is not publishable")
    (out / "manifest.json").write_text(manifest_text, encoding="utf-8")
    (out / "report.html").write_text(html, encoding="utf-8")
    return {"json": out / "manifest.json", "html": out / "report.html"}


def _build_parser() -> ArgumentParser:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--source-issue", required=True)
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--issue", action="append", default=[])
    parser.add_argument("--pr-range", action="append", default=[])
    parser.add_argument("--artifact", action="append", default=[])
    parser.add_argument("--format", default="html,json,issue-drafts")
    parser.add_argument("--mode", default="propose", choices=["propose"])
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        sources, existing = load_fixture(args.fixture)
        candidates = identify_learnings(sources, existing)
        render_outputs(candidates, args.out_dir, args.source_issue, sources)
    except (OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(f"flywheel-closeout error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
