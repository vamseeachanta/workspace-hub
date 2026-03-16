---
name: interoperability-encoding-utf-8-no-bom
description: 'Sub-skill of interoperability: Encoding: UTF-8, no BOM (+3).'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Encoding: UTF-8, no BOM (+3)

## Encoding: UTF-8, no BOM


All workspace text files must be UTF-8 without BOM. Never UTF-16.

**BOM signatures to reject:**

| Encoding | BOM bytes | Source |
|----------|-----------|--------|
| UTF-16 LE | `\xff\xfe` | Windows Notepad default |
| UTF-16 BE | `\xfe\xff` | Some legacy editors |
| UTF-8 BOM | `\xef\xbb\xbf` | Windows "UTF-8 with BOM" |


## Line endings: LF only


`\n` only. No `\r\n`. Enforced by `.gitattributes`.


## Python resolver: uv


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


## Hook installation: core.hooksPath


Install git hooks via `git config core.hooksPath`, not symlinks.
Symlinks require Developer Mode on Windows — `core.hooksPath` works everywhere:

```bash
git config core.hooksPath .claude/hooks
```

All hook scripts live in `.claude/hooks/`. Named entry-points (`pre-commit`,
`post-merge`, `post-checkout`) are thin wrappers delegating to the real script.
