# Issue link and verification guardrails

Session-derived guardrails for GitHub issue planning artifacts.

## Problem class

Plan drafts and issue comments often include many cross-references (`#NNNN`) while sequencing parent/child issue trees. It is easy to fix the obvious chat/comment text but leave bare issue references inside plan prose, tables, pseudo-code blocks, and dependency notes. This violates the workspace convention that issue references in durable reports/plans are Markdown links.

## Durable pattern

Before claiming a plan/index/comment update is complete:

1. Verify the artifact exists and the plan index has exactly one row for the plan path.
2. Verify plan frontmatter/status lines (`Status`, `Complexity`) if the template uses them.
3. Run a targeted unlinked-reference sweep over the changed plan and index.
4. If posting/updating GitHub comments, re-read the comment and check sentinel strings: plan path plus at least one linked child issue URL.
5. Treat unlinked issue refs in code fences/pseudocode as still worth fixing when the block is human-facing plan logic, not executable code.

## Example unlinked-reference check

```bash
python3 - <<'PY'
from pathlib import Path
import re
paths = [
    Path('docs/plans/2026-05-31-issue-2900-deckhand-board-level-plan.md'),
    Path('docs/plans/README.md'),
]
for path in paths:
    text = path.read_text()
    bad = []
    for i, line in enumerate(text.splitlines(), 1):
        for m in re.finditer(r'#29[0-9]{2}', line):
            if not (m.start() > 0 and line[m.start() - 1] == '['):
                bad.append((i, line))
    print(f'{path}: unlinked refs={len(bad)}')
    for row in bad[:20]:
        print(' ', row[0], row[1])
PY
```

Adapt the regex to the issue range under review. The key check is semantic: durable planning prose should use `[#{issue}](https://github.com/OWNER/REPO/issues/{issue})`, not bare `#NNNN`.

## Closeout wording

If the verification finds remaining unlinked refs or unresolved formatting debt, report the exact remaining gate instead of saying the planning update is complete. This is especially important near tool-call or context limits.
