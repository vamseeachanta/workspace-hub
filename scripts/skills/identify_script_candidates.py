#!/usr/bin/env python3
"""identify_script_candidates.py — Phase 0: Classify SKILL.md files as script conversion candidates.

Classifies each SKILL.md into:
  - candidate: body is purely deterministic (bash commands, no LLM reasoning words)
  - needs_human_review: mixed signals
  - not_candidate: clearly requires LLM judgment
"""
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"
OUTPUT_MD = REPO_ROOT / "specs" / "skills" / "script-conversion-candidates.md"
STATE_DIR = REPO_ROOT / ".claude" / "state" / "skill-script-candidates"

# Words that signal LLM reasoning — disqualify from pure-script classification
REASONING_WORDS = [
    r"\bthink\b", r"\bconsider\b", r"\banalyze\b", r"\banalyse\b",
    r"\bevaluate\b", r"\bassess\b", r"\bdecide\b", r"\bjudge\b",
    r"\bif the user\b", r"\bwhen the user\b", r"\bunderstand\b",
    r"\binterpret\b", r"\breason\b", r"\binfer\b", r"\bdiscern\b",
    r"\bcontextual\b",
]

REASONING_RE = re.compile("|".join(REASONING_WORDS), re.IGNORECASE)

# Patterns that signal pure determinism
BASH_COMMAND_RE = re.compile(r"```bash|`[a-z].*`|\$ ", re.IGNORECASE)
CONDITIONAL_GUIDANCE_RE = re.compile(
    r"\bif\s+(it|the|there|you|this)\b|\bwhen\s+(the|there|you)\b",
    re.IGNORECASE,
)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown text. Returns (meta, body)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_text = text[4:end]
    body = text[end + 4:]
    meta: dict = {}
    for line in fm_text.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip()
    return meta, body


def classify(body: str) -> str:
    """Return 'candidate', 'needs_human_review', or 'not_candidate'."""
    reasoning_hits = len(REASONING_RE.findall(body))
    bash_hits = len(BASH_COMMAND_RE.findall(body))
    conditional_hits = len(CONDITIONAL_GUIDANCE_RE.findall(body))

    if reasoning_hits == 0 and conditional_hits == 0 and bash_hits >= 2:
        return "candidate"
    if reasoning_hits == 0 and bash_hits >= 1:
        return "needs_human_review"
    if reasoning_hits >= 3:
        return "not_candidate"
    return "needs_human_review"


def find_skill_files(skills_dir: Path) -> list[Path]:
    """Walk skills dir with os.walk for better performance on slow filesystems."""
    import os
    found = []
    for root, dirs, files in os.walk(str(skills_dir)):
        dirs[:] = [d for d in dirs if d not in ("_archive", "_diverged")]
        if "SKILL.md" in files:
            found.append(Path(root) / "SKILL.md")
    return sorted(found)


def scan_skills(skills_dir: Path) -> list[dict]:
    results = []
    for skill_md in find_skill_files(skills_dir):
        try:
            text = skill_md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        meta, body = parse_frontmatter(text)
        name = meta.get("name", skill_md.parent.name)
        classification = classify(body)
        rel_path = str(skill_md.relative_to(skills_dir.parent.parent))
        results.append({
            "name": name,
            "path": rel_path,
            "classification": classification,
            "reasoning_hits": len(REASONING_RE.findall(body)),
            "bash_hits": len(BASH_COMMAND_RE.findall(body)),
        })
    return results


def write_markdown(results: list[dict], output_path: Path) -> None:
    candidates = [r for r in results if r["classification"] == "candidate"]
    review = [r for r in results if r["classification"] == "needs_human_review"]
    not_cand = [r for r in results if r["classification"] == "not_candidate"]

    lines = [
        "# Skill Script Conversion Candidates",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}  ",
        f"Total skills scanned: {len(results)}",
        "",
        f"## Candidates ({len(candidates)})",
        "",
        "Skills with purely deterministic content (bash commands only, no reasoning).",
        "",
        "| Name | Path |",
        "|------|------|",
    ]
    for r in candidates:
        lines.append(f"| {r['name']} | `{r['path']}` |")

    lines += [
        "",
        f"## Needs Human Review ({len(review)})",
        "",
        "Mixed signals — may be convertible with refactoring.",
        "",
        "| Name | Path | Reasoning Hits | Bash Hits |",
        "|------|------|:-:|:-:|",
    ]
    for r in review:
        lines.append(
            f"| {r['name']} | `{r['path']}` | {r['reasoning_hits']} | {r['bash_hits']} |"
        )

    lines += [
        "",
        f"## Not Candidates ({len(not_cand)})",
        "",
        "Requires LLM judgment — keep as skill.",
        "",
        "| Name | Path |",
        "|------|------|",
    ]
    for r in not_cand:
        lines.append(f"| {r['name']} | `{r['path']}` |")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = output_path.with_suffix(".tmp")
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    tmp.rename(output_path)


def write_json(results: list[dict], state_dir: Path) -> Path:
    state_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_path = state_dir / f"{date_str}.json"
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total": len(results),
        "summary": {
            "candidate": sum(1 for r in results if r["classification"] == "candidate"),
            "needs_human_review": sum(
                1 for r in results if r["classification"] == "needs_human_review"
            ),
            "not_candidate": sum(
                1 for r in results if r["classification"] == "not_candidate"
            ),
        },
        "skills": results,
    }
    tmp = output_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.rename(output_path)
    return output_path


def main() -> int:
    print(f"Scanning skills in {SKILLS_DIR}")
    results = scan_skills(SKILLS_DIR)
    print(f"  Found {len(results)} SKILL.md files")

    write_markdown(results, OUTPUT_MD)
    print(f"  Markdown report: {OUTPUT_MD.relative_to(REPO_ROOT)}")

    json_path = write_json(results, STATE_DIR)
    print(f"  JSON state: {json_path.relative_to(REPO_ROOT)}")

    candidates = sum(1 for r in results if r["classification"] == "candidate")
    review = sum(1 for r in results if r["classification"] == "needs_human_review")
    print(
        f"  Classification: {candidates} candidate, "
        f"{review} needs_human_review, "
        f"{len(results) - candidates - review} not_candidate"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
