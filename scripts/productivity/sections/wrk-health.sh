#!/usr/bin/env bash
# ABOUTME: Daily log section — work item health (pipeline, machine load, priority, complexity)
# Usage: bash wrk-health.sh <WORKSPACE_ROOT>

set -euo pipefail
WORKSPACE_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
WRK_DIR="$WORKSPACE_ROOT/.claude/work-queue"

echo "## Work Item Health"
echo ""

python3 - "$WRK_DIR" <<'PYEOF'
import glob, os, sys

wrk_dir = sys.argv[1]
status_counts, priority_counts, complexity_counts, machine_counts = {}, {}, {}, {}
in_progress_items, blocked_items, ready_items = [], [], []

for f in glob.glob(f'{wrk_dir}/pending/*.md') + glob.glob(f'{wrk_dir}/working/*.md'):
    try:
        lines, in_fm = {}, False
        for line in open(f).read().splitlines():
            if line == '---': in_fm = not in_fm; continue
            if in_fm and ':' in line:
                k, _, v = line.partition(':')
                lines[k.strip()] = v.strip().strip("'\"")

        status     = lines.get('status', 'unknown')
        priority   = lines.get('priority', '')
        complexity = lines.get('complexity', '')
        blocked_by = lines.get('blocked_by', '[]').strip('[]')
        computer   = lines.get('computer', '').strip('[]')
        wrk_id     = lines.get('id', os.path.basename(f).replace('.md',''))
        title      = lines.get('title', '').strip("'\"")[:55]

        status_counts[status]       = status_counts.get(status, 0) + 1
        if priority:   priority_counts[priority]     = priority_counts.get(priority, 0) + 1
        if complexity: complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1
        for m in computer.split(','):
            m = m.strip()
            if m: machine_counts[m] = machine_counts.get(m, 0) + 1

        if status in ('in_progress', 'in-progress', 'working'):
            in_progress_items.append(f'{wrk_id}: {title}')
        elif blocked_by and blocked_by not in ('', 'null'):
            blocked_items.append(wrk_id)
        elif status == 'pending':
            ready_items.append(wrk_id)
    except Exception:
        pass

done_count = len(glob.glob(f'{wrk_dir}/done/*.md'))
in_prog    = sum(status_counts.get(s,0) for s in ('in_progress','in-progress','working'))
pending    = status_counts.get('pending', 0)
blocked_n  = len(blocked_items)
ready_n    = max(0, len(ready_items) - blocked_n)
parked     = status_counts.get('parked', 0)
total      = sum(status_counts.values()) + done_count

# ── Pipeline ─────────────────────────────────────────────────────────────────
print("### Pipeline")
print("")
print("| Stage | Count | % of Total |")
print("|-------|-------|-----------|")
pct = lambda n: f"{n*100//total}%" if total else "—"
print(f"| Done              | {done_count:>5} | {pct(done_count):>10} |")
print(f"| In Progress       | {in_prog:>5} | {pct(in_prog):>10} |")
print(f"| Ready for Dev     | {ready_n:>5} | {pct(ready_n):>10} |")
print(f"| Blocked           | {blocked_n:>5} | —          |")
print(f"| Parked            | {parked:>5} | —          |")
print(f"| **Total**         | **{total}** |            |")
print("")

# ── Machine Load ──────────────────────────────────────────────────────────────
# Normalise aliases: orcaflex-license-machine = acma-ansys05
aliases = {'orcaflex-license-machine': 'acma-ansys05'}
merged = {}
for m, c in machine_counts.items():
    canonical = aliases.get(m, m)
    merged[canonical] = merged.get(canonical, 0) + c

print("### Machine Load")
print("")
print("| Machine | Assigned Items |")
print("|---------|---------------|")
for m, c in sorted(merged.items(), key=lambda x: -x[1]):
    print(f"| {m} | {c} |")
print("")

# ── In Progress ───────────────────────────────────────────────────────────────
print("### In Progress")
print("")
if in_progress_items:
    for item in in_progress_items[:10]:
        print(f"- {item}")
else:
    print("_None active_")
print("")

# ── Priority & Complexity ─────────────────────────────────────────────────────
high = priority_counts.get('high',0) + priority_counts.get('P1',0)
med  = priority_counts.get('medium',0)
low  = priority_counts.get('low',0)
print(f"**Priority (pending):** high={high}  medium={med}  low={low}")
print("")

simp = sum(complexity_counts.get(k,0) for k in ('simple','low','small'))
comp = sum(complexity_counts.get(k,0) for k in ('complex','high','large'))
medi = sum(complexity_counts.get(k,0) for k in ('medium','moderate'))
print(f"**Complexity (pending):** simple={simp}  medium={medi}  complex={comp}")
print("")
PYEOF
