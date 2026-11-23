# Top-level venvs and open-issue workspaces in `/mnt/local-analysis`

Session learning from a cleanup review of `/mnt/local-analysis` used as the main repo ecosystem root.

## Pattern

Top-level Python virtual environments may accumulate beside canonical repos:

- `*-env/` directories with `pyvenv.cfg`
- large `lib/python*/site-packages` payloads
- package-specific CLI shims in `bin/`

These are normally reconstructible and good cleanup candidates, but they should be handled separately from evidence-bearing agent workspaces.

## Survey commands

Use timeout-capped size probes so one huge repo does not stall the whole inventory:

```bash
python3 - <<'PY'
import pathlib, subprocess, time
base = pathlib.Path('/mnt/local-analysis')
for p in sorted(base.iterdir(), key=lambda x: x.name.lower()):
    try:
        st = p.lstat()
    except FileNotFoundError:
        continue
    try:
        du = subprocess.check_output(
            ['timeout', '15', 'du', '-sh', '--', str(p)],
            text=True,
            stderr=subprocess.DEVNULL,
        ).split()[0]
    except Exception:
        du = 'timeout/err'
    marker = p / '.git'
    if marker.exists():
        typ = 'git-repo' if marker.is_dir() else 'git-worktree'
    elif (p / 'pyvenv.cfg').exists():
        typ = 'venv'
    elif p.is_dir():
        typ = 'dir'
    elif p.is_symlink():
        typ = 'symlink'
    else:
        typ = 'file'
    print(f'{du:>11} {time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime))} {typ:12} {p.name}')
PY
```

For venvs, identify package intent without dumping package lists:

```bash
for d in /mnt/local-analysis/*-env; do
  [ -e "$d/pyvenv.cfg" ] || continue
  printf '%s: ' "$d"
  "$d/bin/python" - <<'PY' 2>/dev/null || true
import sys
mods=[]
for m in ['capytaine','marker','fluids','sectionproperties','raft','cli_anything']:
    try:
        __import__(m); mods.append(m)
    except Exception:
        pass
print('python='+sys.version.split()[0]+' modules='+','.join(mods))
PY
done
```

## Classification rule

Add these cleanup classes:

| Class | Signal | Default action |
|---|---|---|
| top-level reconstructible Python dependency dir | directory contains `pyvenv.cfg`, no `.git`, mostly `lib/` and `bin/` | Tier 2/Tier 3: delete only after confirming it is not the active environment for current work; no archive normally required |
| nested open-issue Python dependency dir | dependency dir under a workspace tied to an OPEN GitHub issue | Tier 2 reduce in place: delete only dependency payloads, preserve scripts/reports/outputs/cache unless separately classified |
| open-issue evidence workspace | agent/GIS/report workspace tied to an OPEN GitHub issue | Tier 3 defer or reduce in place; do not delete evidence-bearing outputs/reports |

## Open GitHub issue guard

When a workspace name or logs mention an issue number, check issue state before deleting the workspace. If the issue is OPEN, preserve evidence-bearing subdirectories (`outputs/`, `reports/`, `scripts/`, logs) and only remove reconstructible dependencies like `.venv`.

If the issue is CLOSED, the workspace may move to archive-then-delete after the standard git/evidence checks.

## Shell pitfall

In bash, avoid `printf '--- %s ---\n' "$name"` because some shells/builtins can treat a leading `--`-like format as an option. Use one of:

```bash
printf '%s\n' "--- $name ---"
printf -- '--- %s ---\n' "$name"
```
