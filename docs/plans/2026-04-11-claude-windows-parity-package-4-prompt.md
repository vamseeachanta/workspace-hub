You are working in /mnt/local-analysis/workspace-hub.

Read and follow first:
- AGENTS.md
- CLAUDE.md

Task:
Implement Work Package 4 only for Windows Claude Code parity.

Goal:
Make the Windows readiness proof artifact exist at the path already required by the repo's readiness consumers.

Target files
- scripts/windows/setup-scheduler-tasks.ps1
- scripts/readiness/harness-config.yaml
- scripts/readiness/compare-harness-state.sh
- new file to create only if truly needed for proof generation support:
  - .claude/state/harness-readiness-licensed-win-1.yaml

Intent
- The repo already expects .claude/state/harness-readiness-licensed-win-1.yaml
- The repo already models licensed-win-1 in readiness config
- compare-harness-state.sh already checks for that report
- Your job is to close the proof gap in the minimum safe way

Strict scope
- Only edit the target files above
- Do not edit docs
- Do not edit hooks
- Do not edit memory bridge files
- Do not edit any files from Packages 1–3
- Do not create extra helper files unless absolutely necessary
- Do not commit

Implementation guidance
- Prefer the smallest repo-grounded implementation that makes the Windows readiness artifact path real and consumable.
- Do not invent a broad new architecture.
- Keep this package narrowly focused on proof generation / proof path closure.
- If the scheduler script needs to be updated so Windows can generate or preserve the expected readiness artifact, do so conservatively.
- If compare-harness-state.sh should remain stale-report based for Windows, keep that behavior unless a minimal improvement is clearly necessary.
- If harness-config.yaml should stay as-is, leave it alone.
- Create .claude/state/harness-readiness-licensed-win-1.yaml only if the implementation requires a tracked starter artifact or fixture; otherwise prefer generating it through the intended flow.

Required verification
Run all of these and report results:
- bash -n scripts/readiness/compare-harness-state.sh
- python3 - <<'PY'
from pathlib import Path
p = Path('.claude/state/harness-readiness-licensed-win-1.yaml')
print('exists:', p.exists())
if p.exists():
    print('size:', p.stat().st_size)
    print('head:')
    print('\n'.join(p.read_text().splitlines()[:20]))
PY
- grep -n 'licensed-win-1' scripts/readiness/harness-config.yaml scripts/readiness/compare-harness-state.sh scripts/windows/setup-scheduler-tasks.ps1 || true
- git diff -- scripts/windows/setup-scheduler-tasks.ps1 scripts/readiness/harness-config.yaml scripts/readiness/compare-harness-state.sh .claude/state/harness-readiness-licensed-win-1.yaml
- git status --short -- scripts/windows/setup-scheduler-tasks.ps1 scripts/readiness/harness-config.yaml scripts/readiness/compare-harness-state.sh .claude/state/harness-readiness-licensed-win-1.yaml

Output format
1. What you changed
2. How the Windows readiness proof gap is now closed
3. Verification results
4. Explicit confirmation that no files outside the allowed scope were modified
5. Stop without committing
