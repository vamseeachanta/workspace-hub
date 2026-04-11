#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from workspace_hub.workstations.resolver import WorkstationPathResolver


PROMPT_RE = re.compile(r"prompt", re.IGNORECASE)
STAGE_PROMPT_RE = re.compile(r"stage-(\d+)-prompt\.md", re.IGNORECASE)
WORK_ITEM_RE = re.compile(r"(WRK-\d+|workspace-hub-\d+)", re.IGNORECASE)
REPO_ROOT = Path(__file__).resolve().parents[2]
WORKSTATION_RESOLVER = WorkstationPathResolver.for_repo(REPO_ROOT)


def normalize_path(raw_path: str | None, repo_root: Path) -> tuple[str, bool, str]:
    if not raw_path:
        return "", False, "unknown"
    raw = WORKSTATION_RESOLVER.rewrite_workspace_path(str(raw_path), current_repo_root=repo_root)
    path = Path(raw)
    if path.is_absolute():
        try:
            rel = path.relative_to(repo_root)
            return rel.as_posix(), path.exists(), "repo"
        except ValueError:
            return raw, path.exists(), "external"
    candidate = repo_root / raw
    return raw, candidate.exists(), "repo"


def iter_post_records(logs_dir: Path) -> Iterable[dict]:
    for log_path in sorted(logs_dir.glob("session_*.jsonl")):
        for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("hook") == "post":
                record["_session_file"] = log_path.name
                yield record


def top_items(counter: Counter, limit: int) -> list[dict]:
    return [{"path": key, "count": value} for key, value in counter.most_common(limit)]


def top_pairs(counter: Counter, limit: int, key_name: str = "value") -> list[dict]:
    return [{key_name: key, "count": value} for key, value in counter.most_common(limit)]


def work_item_from_path(path: str) -> str | None:
    match = WORK_ITEM_RE.search(path)
    return match.group(1) if match else None


def collect_stage_prompt_packages(repo_root: Path, prompt_reads: Counter[str]) -> list[dict]:
    assets_root = repo_root / ".claude" / "work-queue" / "assets"
    package_map: dict[str, dict] = {}

    def ensure_package(work_item: str) -> dict:
        return package_map.setdefault(
            work_item,
            {"work_item": work_item, "stages": set(), "prompt_files": {}, "evidence_files": set()},
        )

    for path, reads in prompt_reads.items():
        work_item = work_item_from_path(path)
        stage_match = STAGE_PROMPT_RE.search(path)
        if not work_item or not stage_match:
            continue
        package = ensure_package(work_item)
        stage = int(stage_match.group(1))
        package["stages"].add(stage)
        package["prompt_files"][path] = {
            "path": path,
            "exists": (repo_root / path).exists(),
            "reads": reads,
        }

    if assets_root.exists():
        for work_dir in sorted(p for p in assets_root.iterdir() if p.is_dir()):
            work_item = work_dir.name
            package = ensure_package(work_item)
            for prompt_path in sorted(work_dir.glob("stage-*-prompt.md")):
                rel = prompt_path.relative_to(repo_root).as_posix()
                stage_match = STAGE_PROMPT_RE.search(rel)
                if stage_match:
                    package["stages"].add(int(stage_match.group(1)))
                existing = package["prompt_files"].get(rel, {"path": rel, "exists": True, "reads": 0})
                existing["exists"] = True
                package["prompt_files"][rel] = existing
            evidence_dir = work_dir / "evidence"
            if evidence_dir.exists():
                for evidence_path in sorted(p for p in evidence_dir.rglob("*") if p.is_file()):
                    package["evidence_files"].add(evidence_path.relative_to(repo_root).as_posix())

    rendered = []
    for work_item in sorted(package_map):
        package = package_map[work_item]
        rendered.append(
            {
                "work_item": work_item,
                "stages": sorted(package["stages"]),
                "prompt_files": [package["prompt_files"][p] for p in sorted(package["prompt_files"])],
                "evidence_files": sorted(package["evidence_files"]),
            }
        )
    return rendered


def build_summary(logs_dir: Path, repo_root: Path) -> dict:
    sessions = sorted(logs_dir.glob("session_*.jsonl"))
    tool_counts: Counter[str] = Counter()
    repo_counts: Counter[str] = Counter()
    missing_repo_reads: Counter[str] = Counter()
    missing_external_reads: Counter[str] = Counter()
    prompt_reads: Counter[str] = Counter()
    missing_prompt_reads: Counter[str] = Counter()
    read_counts: Counter[str] = Counter()
    stage_counts: Counter[int] = Counter()
    wrk_counts: Counter[str] = Counter()
    python3_bash_calls = 0
    uv_python_bash_calls = 0
    post_records = 0

    for record in iter_post_records(logs_dir):
        post_records += 1
        tool = str(record.get("tool", "unknown"))
        tool_counts[tool] += 1
        repo = str(record.get("repo", "unknown"))
        repo_counts[repo] += 1

        cmd = str(record.get("cmd", "") or "")
        if tool == "Bash" and "python3" in cmd:
            python3_bash_calls += 1
        if tool == "Bash" and "uv run" in cmd and " python" in cmd:
            uv_python_bash_calls += 1

        if tool != "Read":
            continue

        normalized, exists, scope = normalize_path(record.get("file"), repo_root)
        read_counts[normalized] += 1
        if PROMPT_RE.search(normalized):
            prompt_reads[normalized] += 1
            if not exists:
                missing_prompt_reads[normalized] += 1
                stage_match = STAGE_PROMPT_RE.search(normalized)
                if stage_match:
                    stage_counts[int(stage_match.group(1))] += 1
                    work_item = work_item_from_path(normalized)
                    if work_item:
                        wrk_counts[work_item] += 1

        if exists:
            continue
        if scope == "repo":
            missing_repo_reads[normalized] += 1
        elif scope == "external":
            missing_external_reads[normalized] += 1

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo_root": str(repo_root),
        "logs_dir": str(logs_dir),
        "sessions_analyzed": len(sessions),
        "post_records": post_records,
        "tool_distribution": top_pairs(tool_counts, 10, key_name="tool"),
        "repo_distribution": top_pairs(repo_counts, 10, key_name="repo"),
        "top_reads": top_items(read_counts, 15),
        "top_missing_repo_reads": top_items(missing_repo_reads, 20),
        "top_missing_external_reads": top_items(missing_external_reads, 15),
        "prompt_read_total": sum(prompt_reads.values()),
        "prompt_read_unique": len(prompt_reads),
        "top_prompt_reads": top_items(prompt_reads, 15),
        "top_missing_prompt_reads": top_items(missing_prompt_reads, 20),
        "stage_prompt_distribution": [
            {"stage": stage, "count": count} for stage, count in stage_counts.most_common()
        ],
        "stage_prompt_work_items": [
            {"work_item": wrk, "count": count} for wrk, count in wrk_counts.most_common(15)
        ],
        "stage_prompt_packages": collect_stage_prompt_packages(repo_root, prompt_reads),
        "missing_repo_read_total": sum(missing_repo_reads.values()),
        "missing_external_read_total": sum(missing_external_reads.values()),
        "python3_bash_calls": python3_bash_calls,
        "uv_python_bash_calls": uv_python_bash_calls,
    }


def render_markdown(summary: dict) -> str:
    def lines_for_table(title: str, rows: list[dict], key: str) -> list[str]:
        out = [f"## {title}"]
        if not rows:
            out.append("- none")
            out.append("")
            return out
        for row in rows:
            out.append(f"- `{row[key]}` — {row['count']}")
        out.append("")
        return out

    lines = [
        f"# Claude session ecosystem audit — {summary['generated_at'][:10]}",
        "",
        "Scope: post-hook records from `logs/orchestrator/claude/session_*.jsonl` compared against the current repo checkout.",
        "",
        "## Corpus",
        f"- Sessions analyzed: {summary['sessions_analyzed']}",
        f"- Post-hook records: {summary['post_records']}",
        f"- Prompt-like reads: {summary['prompt_read_total']} total / {summary['prompt_read_unique']} unique",
        f"- Missing repo-local reads: {summary['missing_repo_read_total']}",
        f"- Missing external reads: {summary['missing_external_read_total']}",
        f"- Bash calls using bare `python3`: {summary['python3_bash_calls']}",
        f"- Bash calls using `uv run ... python`: {summary['uv_python_bash_calls']}",
        "",
    ]
    lines += lines_for_table("Top tool distribution", summary["tool_distribution"], "tool")
    lines += lines_for_table("Top repo distribution", summary["repo_distribution"], "repo")
    lines += lines_for_table("Most-read files", summary["top_reads"], "path")
    lines += lines_for_table("Missing repo-local reads", summary["top_missing_repo_reads"], "path")
    lines += lines_for_table("Missing external reads", summary["top_missing_external_reads"], "path")
    lines += lines_for_table("Prompt reads", summary["top_prompt_reads"], "path")
    lines += lines_for_table("Missing prompt reads", summary["top_missing_prompt_reads"], "path")
    lines += lines_for_table("Stage prompt distribution", summary["stage_prompt_distribution"], "stage")
    lines += lines_for_table("Stage prompt work items", summary["stage_prompt_work_items"], "work_item")

    lines.append("## Stage prompt package index")
    stage_packages = summary.get("stage_prompt_packages", [])
    if not stage_packages:
        lines.append("- none")
        lines.append("")
    else:
        for package in stage_packages:
            stages = ", ".join(str(stage) for stage in package.get("stages", [])) or "none"
            prompt_files = package.get("prompt_files", [])
            evidence_files = package.get("evidence_files", [])
            missing_count = sum(1 for item in prompt_files if not item.get("exists"))
            lines.append(
                f"- `{package['work_item']}` — stages: {stages} | prompt files: {len(prompt_files)} | missing prompt artifacts: {missing_count} | evidence files: {len(evidence_files)}"
            )
            for prompt in prompt_files:
                status = "present" if prompt.get("exists") else "missing"
                lines.append(
                    f"  - prompt: `{prompt['path']}` ({status}, reads={prompt.get('reads', 0)})"
                )
            for evidence in evidence_files[:10]:
                lines.append(f"  - evidence: `{evidence}`")
            if len(evidence_files) > 10:
                lines.append(f"  - evidence: ... {len(evidence_files) - 10} more")
        lines.append("")

    lines += [
        "## Ecosystem strengthening recommendations",
        "1. Add a periodic audit for stale work-queue references; the hottest missing reads are legacy `scripts/work-queue/*` paths that are still present in historical Claude workflows.",
        "2. Keep a generated report in-repo so future refactors can measure whether missing-reference drift is shrinking or growing.",
        "3. Reduce bare `python3` usage in automation and prompts; the session corpus still shows direct `python3` bash calls despite the repo-wide `uv run` policy.",
        "4. Treat missing stage prompt assets as first-class evidence gaps. If the asset is intentionally ephemeral, generate an index or summary artifact before cleanup.",
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Audit Claude session logs against the current repo ecosystem.")
    parser.add_argument("--repo-root", default=str(repo_root))
    parser.add_argument("--logs-dir", default=str(repo_root / "logs" / "orchestrator" / "claude"))
    parser.add_argument("--output-json", help="Optional JSON output path")
    parser.add_argument("--output-md", help="Optional markdown output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    logs_dir = Path(args.logs_dir).resolve()
    summary = build_summary(logs_dir, repo_root)
    markdown = render_markdown(summary)

    if args.output_json:
        output_json = Path(args.output_json)
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if args.output_md:
        output_md = Path(args.output_md)
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_md.write_text(markdown + "\n", encoding="utf-8")
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
