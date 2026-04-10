#!/usr/bin/env bash
# correction-to-skill-candidates.sh — Identify correction patterns for skill promotion
# Issue: #1426 — Accelerate correction-to-skill promotion pipeline
#
# Analyzes .claude/state/corrections/ data to find:
# 1. Files corrected 10+ times (strong promotion candidates)
# 2. Skill files that are frequently re-edited (skill needs update)
# 3. Correction clusters in the same directory (new skill opportunity)
#
# Usage:
#   bash scripts/enforcement/correction-to-skill-candidates.sh [--json] [--threshold N]
#
# Output: skill promotion candidates ranked by correction frequency.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
CORRECTIONS_DIR="${REPO_ROOT}/.claude/state/corrections"
THRESHOLD="${2:-10}"
JSON_MODE=false

for arg in "$@"; do
  case "$arg" in
    --json) JSON_MODE=true ;;
    --threshold) shift; THRESHOLD="${1:-10}" ;;
  esac
done

if [[ ! -d "$CORRECTIONS_DIR" ]]; then
  echo "[skill-candidates] No corrections directory found."
  exit 0
fi

uv run --no-project python - "$CORRECTIONS_DIR" "$THRESHOLD" "$JSON_MODE" <<'PYTHON'
import sys, json, os, glob
from collections import Counter, defaultdict
from pathlib import Path

corrections_dir = sys.argv[1]
threshold = int(sys.argv[2])
json_mode = sys.argv[3] == "True"

# Parse all correction records
file_corrections = Counter()
dir_corrections = Counter()
skill_corrections = Counter()
correction_dates = defaultdict(set)

for f in sorted(glob.glob(os.path.join(corrections_dir, "session_*.jsonl"))):
    with open(f) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except:
                continue

            filepath = d.get("file", "")
            # Normalize paths
            for prefix in ["/mnt/local-analysis/workspace-hub/", "/mnt/github/workspace-hub/", "/home/vamsee/"]:
                filepath = filepath.replace(prefix, "")

            file_corrections[filepath] += 1
            dir_corrections[str(Path(filepath).parent)] += 1
            correction_dates[filepath].add(d.get("timestamp", "")[:10])

            # Track skill files specifically
            if "skills/" in filepath and filepath.endswith("SKILL.md"):
                skill_corrections[filepath] += 1

# Build candidates
candidates = []

# Category 1: Frequently corrected files → new skill needed
for filepath, count in file_corrections.most_common():
    if count < threshold:
        break
    if "skills/" in filepath:
        continue  # Handle separately
    days = len(correction_dates[filepath])
    candidates.append({
        "type": "new_skill_opportunity",
        "file": filepath,
        "corrections": count,
        "correction_days": days,
        "rationale": f"Corrected {count} times across {days} days — pattern likely worth capturing as a skill"
    })

# Category 2: Frequently corrected skills → skill needs update
skill_candidates = []
for filepath, count in skill_corrections.most_common():
    if count < 5:
        break
    days = len(correction_dates[filepath])
    skill_candidates.append({
        "type": "skill_needs_update",
        "file": filepath,
        "corrections": count,
        "correction_days": days,
        "rationale": f"Skill corrected {count} times across {days} days — skill content likely stale or incomplete"
    })

# Category 3: Hot directories → skill domain gap
dir_candidates = []
for dirpath, count in dir_corrections.most_common(10):
    if count < threshold * 2:
        break
    dir_candidates.append({
        "type": "directory_hotspot",
        "directory": dirpath,
        "total_corrections": count,
        "rationale": f"Directory had {count} corrections — may indicate a missing domain skill"
    })

total_corrections = sum(file_corrections.values())
total_files = len(file_corrections)
files_over_threshold = len([c for c in file_corrections.values() if c >= threshold])

summary = {
    "total_corrections": total_corrections,
    "total_unique_files": total_files,
    "files_over_threshold": files_over_threshold,
    "threshold": threshold,
    "new_skill_candidates": len(candidates),
    "skills_needing_update": len(skill_candidates),
    "directory_hotspots": len(dir_candidates),
}

if json_mode:
    output = {
        "summary": summary,
        "new_skill_candidates": candidates[:20],
        "skills_needing_update": skill_candidates[:10],
        "directory_hotspots": dir_candidates[:10],
    }
    print(json.dumps(output, indent=2))
else:
    print(f"[skill-candidates] Correction Analysis Summary")
    print(f"  Total corrections: {total_corrections}")
    print(f"  Unique files: {total_files}")
    print(f"  Files with {threshold}+ corrections: {files_over_threshold}")
    print()
    print(f"=== NEW SKILL OPPORTUNITIES (top 15) ===")
    for c in candidates[:15]:
        print(f"  {c['corrections']:4d}x ({c['correction_days']}d)  {c['file']}")
    print()
    print(f"=== SKILLS NEEDING UPDATE (top 10) ===")
    for c in skill_candidates[:10]:
        print(f"  {c['corrections']:4d}x ({c['correction_days']}d)  {c['file']}")
    print()
    print(f"=== DIRECTORY HOTSPOTS (top 5) ===")
    for c in dir_candidates[:5]:
        print(f"  {c['total_corrections']:4d}x  {c['directory']}")

PYTHON
