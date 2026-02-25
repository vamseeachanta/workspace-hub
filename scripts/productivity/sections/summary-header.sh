#!/usr/bin/env bash
# ABOUTME: Daily log section — top-of-report summary (usage, work queue, data health)
# ABOUTME: Pulls key numbers from quota cache, work queue, and repo state
# Usage: bash summary-header.sh <WORKSPACE_ROOT>

set -euo pipefail
WORKSPACE_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
WRK_DIR="$WORKSPACE_ROOT/.claude/work-queue"
USER_QUOTA_CACHE="$HOME/.cache/agent-quota.json"
WORKSPACE_QUOTA="$WORKSPACE_ROOT/config/ai-tools/agent-quota-latest.json"

echo "## Summary"
echo ""
echo "_$(date '+%A, %B %-d %Y  %-I:%M %p')_"
echo ""

python3 - "$WRK_DIR" "$USER_QUOTA_CACHE" "$WORKSPACE_QUOTA" "$WORKSPACE_ROOT" <<'PYEOF'
import glob, os, sys, json, time

wrk_dir, user_quota, ws_quota, workspace = sys.argv[1:5]

# ── Work queue ────────────────────────────────────────────────────────────────
status_counts, machine_counts = {}, {}
in_progress, blocked_ids, ready_ids = [], [], []

for f in glob.glob(f'{wrk_dir}/pending/*.md') + glob.glob(f'{wrk_dir}/working/*.md'):
    try:
        fm, in_fm = {}, False
        for line in open(f).read().splitlines():
            if line == '---': in_fm = not in_fm; continue
            if in_fm and ':' in line:
                k, _, v = line.partition(':')
                fm[k.strip()] = v.strip().strip("'\"")
        status     = fm.get('status', 'unknown')
        blocked_by = fm.get('blocked_by', '[]').strip('[]')
        computer   = fm.get('computer', '').strip('[]')
        wrk_id     = fm.get('id', os.path.basename(f).replace('.md',''))
        title      = fm.get('title', '').strip("'\"")[:50]
        status_counts[status] = status_counts.get(status, 0) + 1
        for m in computer.split(','):
            m = m.strip()
            if m:
                aliases = {'orcaflex-license-machine': 'acma-ansys05'}
                m = aliases.get(m, m)
                machine_counts[m] = machine_counts.get(m, 0) + 1
        if status in ('in_progress', 'in-progress', 'working'):
            in_progress.append(f'{wrk_id}: {title}')
        elif blocked_by and blocked_by not in ('', 'null'):
            blocked_ids.append(wrk_id)
        elif status == 'pending':
            ready_ids.append(wrk_id)
    except Exception:
        pass

done_n    = len(glob.glob(f'{wrk_dir}/done/*.md'))
in_prog_n = sum(status_counts.get(s,0) for s in ('in_progress','in-progress','working'))
blocked_n = len(blocked_ids)
ready_n   = max(0, len(ready_ids) - blocked_n)
total_n   = sum(status_counts.values()) + done_n

# ── AI quota ──────────────────────────────────────────────────────────────────
quota_data = None
for qf in [user_quota, ws_quota]:
    if os.path.isfile(qf):
        age = time.time() - os.path.getmtime(qf)
        if age < 7200:  # within 2h
            try:
                with open(qf) as f:
                    quota_data = json.load(f)
                break
            except Exception:
                pass

def quota_remaining(data, provider):
    if not data:
        return None
    for a in data.get('agents', []):
        if a.get('provider') == provider:
            if 'week_pct' in a:
                return 100 - float(a['week_pct'] or 0)
            return float(a.get('pct_remaining') or 0)
    return None

c_rem = quota_remaining(quota_data, 'claude')
o_rem = quota_remaining(quota_data, 'codex')
g_rem = quota_remaining(quota_data, 'gemini')

def fmt_pct(v):
    if v is None: return '?%'
    v = int(v)
    icon = '⚠' if v <= 20 else ('⬆' if v <= 50 else '✓')
    return f'{icon} {v}%'

# ── Repo dirty count ──────────────────────────────────────────────────────────
import subprocess
repos = {'workspace-hub': workspace,
         'digitalmodel': os.path.join(workspace, 'digitalmodel'),
         'worldenergydata': os.path.join(workspace, 'worldenergydata')}
dirty_repos = []
for name, path in repos.items():
    if not os.path.isdir(path): continue
    try:
        r = subprocess.run(['git', 'status', '--porcelain'], cwd=path,
                           capture_output=True, text=True, timeout=5)
        if r.stdout.strip():
            dirty_repos.append(name)
    except Exception:
        pass

# ── Print summary ─────────────────────────────────────────────────────────────
print("| | |")
print("|---|---|")
print(f"| **Work Queue** | {done_n} done · {in_prog_n} in progress · {ready_n} ready · {blocked_n} blocked · {total_n} total |")
print(f"| **Machine Load** | " +
      "  ".join(f"{m}: {c}" for m, c in sorted(machine_counts.items(), key=lambda x: -x[1])) + " |")
print(f"| **AI Usage** | claude {fmt_pct(c_rem)} remaining · codex {fmt_pct(o_rem)} · gemini {fmt_pct(g_rem)} |")
if dirty_repos:
    print(f"| **Dirty Repos** | {', '.join(dirty_repos)} — uncommitted changes |")
if in_progress:
    items = '  '.join(f'`{x.split(":")[0]}`' for x in in_progress[:5])
    print(f"| **Active WRK** | {items} |")
PYEOF

echo ""
