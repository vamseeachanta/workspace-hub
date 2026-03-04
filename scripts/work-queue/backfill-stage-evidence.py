#!/usr/bin/env python3
"""Backfill stage evidence ledger for all WRK items."""

from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path


def parse_frontmatter(text: str) -> tuple[str, str] | None:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    if not match:
        return None
    return match.group(1), match.group(2)


def get_scalar(frontmatter: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}:[ \t]*(.+)$", frontmatter, re.MULTILINE)
    return m.group(1).strip() if m else None


def upsert_scalar(frontmatter: str, key: str, value: str) -> str:
    line = f"{key}: {value}"
    if re.search(rf"^{re.escape(key)}:", frontmatter, re.MULTILINE):
        return re.sub(rf"^{re.escape(key)}:.*$", line, frontmatter, flags=re.MULTILINE)
    return frontmatter.rstrip() + "\n" + line + "\n"


def iter_wrk_files(queue_root: Path) -> list[Path]:
    files: list[Path] = []
    for section in ("pending", "working", "done", "blocked"):
        files.extend(sorted((queue_root / section).glob("WRK-*.md")))
    archive_root = queue_root / "archive"
    if archive_root.exists():
        files.extend(sorted(archive_root.glob("*/WRK-*.md")))
    return files


def render_stage_evidence(template_text: str, wrk_id: str, now_utc: str) -> str:
    rendered = template_text.replace("WRK-000", wrk_id)
    rendered = rendered.replace("2026-03-03T00:00:00Z", now_utc)
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill stage evidence for WRK files.")
    parser.add_argument("--write", action="store_true", help="Apply changes (default is dry-run).")
    args = parser.parse_args()

    workspace_root = Path(__file__).resolve().parents[2]
    queue_root = workspace_root / ".claude" / "work-queue"
    template_path = workspace_root / "specs" / "templates" / "stage-evidence-template.yaml"
    if not template_path.exists():
        raise FileNotFoundError(f"Missing template: {template_path}")

    template_text = template_path.read_text(encoding="utf-8")
    now_utc = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    wrk_files = iter_wrk_files(queue_root)
    created_stage_files = 0
    updated_frontmatter = 0
    skipped = 0

    for wrk_file in wrk_files:
        parsed = parse_frontmatter(wrk_file.read_text(encoding="utf-8"))
        if not parsed:
            skipped += 1
            continue
        front, body = parsed
        wrk_id = (get_scalar(front, "id") or wrk_file.stem).strip()

        stage_ref = f".claude/work-queue/assets/{wrk_id}/evidence/stage-evidence.yaml"
        stage_file = queue_root / "assets" / wrk_id / "evidence" / "stage-evidence.yaml"

        if not stage_file.exists():
            created_stage_files += 1
            if args.write:
                stage_file.parent.mkdir(parents=True, exist_ok=True)
                stage_file.write_text(render_stage_evidence(template_text, wrk_id, now_utc), encoding="utf-8")

        existing_ref = get_scalar(front, "stage_evidence_ref")
        if not existing_ref:
            updated_frontmatter += 1
            if args.write:
                new_front = upsert_scalar(front, "stage_evidence_ref", stage_ref)
                wrk_file.write_text(f"---\n{new_front.rstrip()}\n---\n{body}", encoding="utf-8")

    mode = "APPLY" if args.write else "DRY-RUN"
    print(f"[{mode}] WRK files scanned: {len(wrk_files)}")
    print(f"[{mode}] stage-evidence files to create: {created_stage_files}")
    print(f"[{mode}] WRKs to add stage_evidence_ref: {updated_frontmatter}")
    print(f"[{mode}] skipped (invalid frontmatter): {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

