#!/usr/bin/env python3
"""run_skill_evals.py — Execute skill eval checks defined in specs/skills/evals/*.yaml.

For each eval YAML:
  - Read the target SKILL.md (path from eval's skill_path field)
  - Check required_sections[] and required_commands[] exist in SKILL.md body
  - Emit one JSONL record per check to .claude/state/skill-eval-results/YYYY-MM-DD.jsonl
  - On FAIL, write a proposal to .claude/state/skill-eval-candidates/

Exit 0 if all pass/skip, 1 if any fail.
"""
import argparse
import json
import os
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run skill evals")
    parser.add_argument(
        "--evals-dir",
        default="specs/skills/evals",
        help="Directory containing eval YAML files (default: specs/skills/evals)",
    )
    parser.add_argument(
        "--results-dir",
        default=".claude/state/skill-eval-results",
        help="Directory to write JSONL results (default: .claude/state/skill-eval-results)",
    )
    return parser.parse_args()


def load_yaml_simple(path: Path) -> dict:
    """Minimal YAML loader for eval files — supports only flat/list structures."""
    try:
        import yaml  # type: ignore[import]
        with path.open(encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except ImportError:
        pass
    # Fallback: basic line-by-line parser for our simple schema
    return _parse_yaml_simple(path.read_text(encoding="utf-8"))


def _parse_yaml_simple(text: str) -> dict:
    """Very simple YAML parser that handles our eval schema without PyYAML."""
    result: dict = {}
    lines = text.splitlines()
    i = 0
    current_eval: dict | None = None
    current_checks: dict | None = None
    current_list_key: str | None = None
    in_evals = False
    in_checks = False

    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip()

        # top-level keys
        if not line.startswith(" ") and ":" in stripped:
            key, _, val = stripped.partition(":")
            val = val.strip()
            if key == "evals":
                result["evals"] = []
                in_evals = True
                in_checks = False
                current_eval = None
            elif key in ("version", "wrk_id", "skill_name", "skill_path"):
                result[key] = val.strip("' \"") if val else ""
                in_evals = False
        elif in_evals and stripped.startswith("  - "):
            # new eval entry
            current_eval = {}
            result["evals"].append(current_eval)
            in_checks = False
            current_list_key = None
            # parse first key on same line
            rest = stripped[4:]
            if ":" in rest:
                k, _, v = rest.partition(":")
                current_eval[k.strip()] = v.strip().strip("'\"")
        elif current_eval is not None and stripped.startswith("    ") and not stripped.startswith("      "):
            rest = stripped.strip()
            if rest == "checks:":
                current_eval["checks"] = {}
                current_checks = current_eval["checks"]
                in_checks = True
                current_list_key = None
            elif ":" in rest:
                k, _, v = rest.partition(":")
                current_eval[k.strip()] = v.strip().strip("'\"")
        elif in_checks and current_checks is not None and stripped.startswith("      ") and not stripped.startswith("        "):
            rest = stripped.strip()
            if rest.endswith(":"):
                current_list_key = rest[:-1]
                current_checks[current_list_key] = []
            elif ":" in rest:
                k, _, v = rest.partition(":")
                current_checks[k.strip()] = v.strip().strip("'\"")
        elif current_list_key is not None and stripped.startswith("        - "):
            val_str = stripped.strip()[2:].strip().strip("'\"")
            current_checks[current_list_key].append(val_str)  # type: ignore[index]

        i += 1

    return result


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown. Returns (meta dict, body text)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_text = text[4:end]
    body = text[end + 4:]
    meta: dict = {}
    for line in fm_text.splitlines():
        if ":" in line and not line.strip().startswith("-"):
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip().strip("'\"")
    return meta, body


def run_eval(
    eval_def: dict,
    skill_path_str: str,
    repo_root: Path,
    run_id: str,
    source_eval: str,
    timestamp: str,
) -> list[dict]:
    """Run a single eval definition. Returns list of result records."""
    records: list[dict] = []
    eval_id = eval_def.get("eval_id", "unknown")
    eval_type = eval_def.get("eval_type", "capability")
    skill_name = eval_def.get("skill_name", "")
    checks = eval_def.get("checks", {})

    skill_path = repo_root / skill_path_str
    if not skill_path.exists():
        records.append({
            "run_id": run_id,
            "skill_name": skill_name,
            "skill_path": skill_path_str,
            "eval_id": eval_id,
            "eval_type": eval_type,
            "result": "fail",
            "reason": f"SKILL.md not found at {skill_path_str}",
            "timestamp": timestamp,
            "source_eval": source_eval,
        })
        return records

    text = skill_path.read_text(encoding="utf-8", errors="replace")
    _meta, body = parse_frontmatter(text)

    required_sections = checks.get("required_sections", [])
    required_commands = checks.get("required_commands", [])

    all_checks = (
        [("section", s) for s in required_sections]
        + [("command", c) for c in required_commands]
    )

    if not all_checks:
        records.append({
            "run_id": run_id,
            "skill_name": skill_name,
            "skill_path": skill_path_str,
            "eval_id": eval_id,
            "eval_type": eval_type,
            "result": "skip",
            "reason": "No checks defined",
            "timestamp": timestamp,
            "source_eval": source_eval,
        })
        return records

    failures = []
    for check_type, check_val in all_checks:
        if check_val not in body:
            failures.append(f"{check_type}={check_val!r} not found")

    if failures:
        result = "fail"
        reason = "; ".join(failures)
    else:
        result = "pass"
        reason = f"All {len(all_checks)} checks passed"

    records.append({
        "run_id": run_id,
        "skill_name": skill_name,
        "skill_path": skill_path_str,
        "eval_id": eval_id,
        "eval_type": eval_type,
        "result": result,
        "reason": reason,
        "timestamp": timestamp,
        "source_eval": source_eval,
    })
    return records


def write_candidate_proposal(
    skill_name: str,
    skill_path: str,
    failing_evals: list[str],
    output_dir: Path,
    timestamp: str,
) -> None:
    """Write a fix-proposal YAML for skills with failing evals."""
    output_dir.mkdir(parents=True, exist_ok=True)
    date_str = timestamp[:10]
    safe_name = skill_name.replace("/", "-").replace(" ", "_")
    out_path = output_dir / f"{date_str}-{safe_name}.yaml"
    content = (
        f"skill_name: {skill_name}\n"
        f"skill_path: {skill_path}\n"
        f"wrk_id: WRK-1009\n"
        f"suggested_action: fix\n"
        f"generated_at: {timestamp}\n"
        f"failing_evals:\n"
    )
    for eval_id in failing_evals:
        content += f"  - {eval_id}\n"

    tmp = out_path.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.rename(out_path)


def atomic_append_jsonl(records: list[dict], output_file: Path) -> None:
    """Append records to a JSONL file atomically using a temp file + rename trick.

    Since JSONL is append-only, we read existing content, add new records, write to tmp,
    then rename.
    """
    existing = ""
    if output_file.exists():
        existing = output_file.read_text(encoding="utf-8")

    new_lines = "\n".join(json.dumps(r) for r in records)
    combined = existing.rstrip("\n")
    if combined:
        combined = combined + "\n" + new_lines + "\n"
    else:
        combined = new_lines + "\n"

    tmp = output_file.with_suffix(".tmp")
    tmp.write_text(combined, encoding="utf-8")
    tmp.rename(output_file)


def main() -> int:
    args = parse_args()
    repo_root = Path.cwd()

    evals_dir = repo_root / args.evals_dir
    results_dir = repo_root / args.results_dir
    candidates_dir = repo_root / ".claude" / "state" / "skill-eval-candidates"

    results_dir.mkdir(parents=True, exist_ok=True)
    candidates_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    date_str = timestamp[:10]
    run_id = str(uuid.uuid4())

    eval_files = sorted(evals_dir.glob("*.yaml")) if evals_dir.exists() else []
    if not eval_files:
        print(f"WARNING: no eval files found in {evals_dir}", file=sys.stderr)
        return 0

    all_records: list[dict] = []
    failures_by_skill: dict[str, dict] = {}

    for eval_file in eval_files:
        eval_data = load_yaml_simple(eval_file)
        skill_path_str = eval_data.get("skill_path", "")
        skill_name = eval_data.get("skill_name", eval_file.stem)

        for eval_def in eval_data.get("evals", []):
            eval_def["skill_name"] = skill_name
            records = run_eval(
                eval_def=eval_def,
                skill_path_str=skill_path_str,
                repo_root=repo_root,
                run_id=run_id,
                source_eval=str(eval_file.relative_to(repo_root)),
                timestamp=timestamp,
            )
            all_records.extend(records)
            for r in records:
                if r["result"] == "fail":
                    key = f"{skill_name}::{skill_path_str}"
                    if key not in failures_by_skill:
                        failures_by_skill[key] = {
                            "skill_name": skill_name,
                            "skill_path": skill_path_str,
                            "failing_evals": [],
                        }
                    failures_by_skill[key]["failing_evals"].append(r["eval_id"])

    # Write JSONL results
    output_jsonl = results_dir / f"{date_str}.jsonl"
    if all_records:
        atomic_append_jsonl(all_records, output_jsonl)

    # Summary
    total = len(all_records)
    passes = sum(1 for r in all_records if r["result"] == "pass")
    fails = sum(1 for r in all_records if r["result"] == "fail")
    skips = sum(1 for r in all_records if r["result"] == "skip")
    print(f"Skill evals: {total} checks — PASS={passes} FAIL={fails} SKIP={skips}")
    print(f"Results: {output_jsonl}")

    # Write candidate proposals for failing skills
    for entry in failures_by_skill.values():
        write_candidate_proposal(
            skill_name=entry["skill_name"],
            skill_path=entry["skill_path"],
            failing_evals=entry["failing_evals"],
            output_dir=candidates_dir,
            timestamp=timestamp,
        )
        print(
            f"  CANDIDATE PROPOSAL: {entry['skill_name']} "
            f"({len(entry['failing_evals'])} failing evals)"
        )

    if fails > 0:
        print(f"ERROR: {fails} eval(s) FAILED — see {output_jsonl}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
