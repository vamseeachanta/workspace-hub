---
name: interoperability-fix-command
description: 'Sub-skill of interoperability: Fix Command.'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Fix Command

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
