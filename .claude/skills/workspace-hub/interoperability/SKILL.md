---
name: interoperability
description: "Cross-OS standards and health checks for workspace-hub — encoding, line endings, uv as Python resolver, hook installation, and regular verification items"
version: 1.0.0
category: workspace-hub
author: workspace-hub
type: skill
last_updated: 2026-02-19
wrk_ref: WRK-210
related_skills:
  - repo-sync
  - improve
  - ecosystem-health
  - skill-creator
tags:
  - cross-platform
  - encoding
  - uv
  - hooks
  - windows
  - linux
  - health-checks
platforms: [all]
---

# Interoperability — Cross-OS Standards

Workspace-hub is used daily across Windows and Linux machines. Files authored
on Windows and executed on Linux routinely cause silent failures. This skill
documents the enforced standards and what to verify regularly.

## The Core Problem

Windows editors (Notepad, VSCode with wrong settings) save files as:
- UTF-16 LE (Notepad default) — crashes any parser that assumes UTF-8
- CRLF line endings — breaks bash heredocs, YAML parsers, and diffs
- UTF-8 with BOM (`\xef\xbb\xbf`) — breaks strict UTF-8 parsers

These failures are **silent** — a file arrives via `git pull`, looks fine in
a text editor, and then crashes a script hours later. Catch before the fact,
not after.

## Enforced Standards

### Encoding: UTF-8, no BOM

All workspace text files must be UTF-8 without BOM. Never UTF-16.

**BOM signatures to reject:**

| Encoding | BOM bytes | Source |
|----------|-----------|--------|
| UTF-16 LE | `\xff\xfe` | Windows Notepad default |
| UTF-16 BE | `\xfe\xff` | Some legacy editors |
| UTF-8 BOM | `\xef\xbb\xbf` | Windows "UTF-8 with BOM" |

### Line endings: LF only

`\n` only. No `\r\n`. Enforced by `.gitattributes`.

### Python resolver: uv

All Python invocations in workspace-hub scripts must use:

```bash
uv run --no-project python script.py
# or inline:
uv run --no-project --quiet python - "$arg" <<'PYEOF'
import sys
...
PYEOF
```

**Never** use `python3`/`python` detection chains. uv is a hard dependency —
if it is not installed, fail clearly:

```bash
command -v uv >/dev/null 2>&1 || {
    echo "uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
}
```

`--no-project` is required when invoking from arbitrary working directories
(e.g., git hooks) to avoid uv searching for a `pyproject.toml` upward.

### Hook installation: core.hooksPath

Install git hooks via `git config core.hooksPath`, not symlinks.
Symlinks require Developer Mode on Windows — `core.hooksPath` works everywhere:

```bash
git config core.hooksPath .claude/hooks
```

All hook scripts live in `.claude/hooks/`. Named entry-points (`pre-commit`,
`post-merge`, `post-checkout`) are thin wrappers delegating to the real script.

## Three-Layer Defence (encoding)

```
Layer 1: .gitattributes  — git normalises encoding on checkout (strongest)
Layer 2: pre-commit hook — blocks commits with bad-encoding files
Layer 3: post-merge hook — warns after pull if bad files arrived
```

`.gitattributes` rules (already in repo):
```
*.md   text eol=lf working-tree-encoding=UTF-8
*.yaml text eol=lf working-tree-encoding=UTF-8
*.yml  text eol=lf working-tree-encoding=UTF-8
*.json text eol=lf working-tree-encoding=UTF-8
```

`working-tree-encoding=UTF-8` tells git to re-encode to UTF-8 on checkout
even if the file was committed as UTF-16. This is the strongest layer.

## Fix Command

When the encoding hook flags a file:

```bash
# Detect encoding
file <bad-file>

# Convert UTF-16 to UTF-8
iconv -f UTF-16 -t UTF-8 <bad-file> | sed 's/\r//' > /tmp/fixed.md
mv /tmp/fixed.md <bad-file>

# Or via uv Python (no iconv required — works on Windows Git Bash):
uv run --no-project python - <<'PYEOF'
import pathlib, sys
f = pathlib.Path(sys.argv[1])
f.write_text(f.read_bytes().decode('utf-16').replace('\r', ''), encoding='utf-8')
PYEOF
<bad-file>

git add <bad-file>
git commit -m "fix(encoding): convert <bad-file> to UTF-8"
```

## Setup (new machine or after fresh clone)

```bash
# 1. Install uv (once per machine)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install hooks (once per clone)
bash scripts/operations/setup-hooks.sh

# 3. Verify
git config core.hooksPath          # → .claude/hooks
ls -la .claude/hooks/pre-commit    # → executable
command -v uv                      # → found
```

## Health Check Items

Run these checks after every `git pull` or when diagnosing unexpected failures:

| # | Check | Command | Expected |
|---|-------|---------|----------|
| 1 | Hook wired | `git config core.hooksPath` | `.claude/hooks` |
| 2 | pre-commit executable | `test -x .claude/hooks/pre-commit && echo OK` | `OK` |
| 3 | uv available | `command -v uv && uv --version` | version string |
| 4 | .gitattributes rules | `grep working-tree-encoding .gitattributes` | 4 lines |
| 5 | Encoding clean | `.claude/hooks/check-encoding.sh` | exit 0, no output |
| 6 | Work queue index | `uv run --no-project python scripts/work-queue/generate-index.py` | exit 0 |

These six checks are the minimum to confirm the cross-platform guard is active.
The `/ecosystem-health` skill runs all of these automatically.

## Editor Settings (recommended)

| Editor | Setting | Value |
|--------|---------|-------|
| VSCode | `files.encoding` | `utf8` |
| VSCode | `files.eol` | `\n` |
| VSCode | `files.autoGuessEncoding` | `false` |
| Notepad++ | Encoding menu | UTF-8 (not UTF-8 BOM) |
| Windows Notepad | — | Avoid for repo files |

VSCode `.vscode/settings.json` (already recommended in workspace):
```json
{
  "files.encoding": "utf8",
  "files.eol": "\n"
}
```

## Related

- `WRK-208` — root cause analysis + encoding fix implementation
- `WRK-209` — uv enforcement across all workspace scripts
- `/repo-sync` — Phase 4 runs encoding check after every pull
- `/ecosystem-health` — automated health check suite (WRK-211)
- `.claude/hooks/check-encoding.sh` — the pre-commit/post-merge hook
- `scripts/operations/setup-hooks.sh` — one-command setup on any machine
