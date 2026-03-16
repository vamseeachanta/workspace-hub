---
name: file-taxonomy-specs-vs-docs-vs-plans
description: 'Sub-skill of file-taxonomy: specs/ vs docs/ vs plans/ (+4).'
version: 1.6.0
category: workspace
type: reference
scripts_exempt: true
---

# specs/ vs docs/ vs plans/ (+4)

## specs/ vs docs/ vs plans/


- `specs/wrk/WRK-NNN/` — Execution spec for a specific work item (Route C only)
- `specs/repos/<repo>/` — Formal design decisions / ADRs for a repo
- `specs/modules/` — System-level module specs (pre-build design)
- `docs/modules/<domain>/` — Reference docs written *after* build
- `docs/guides/` — How-to guides for humans
- `.claude/work-queue/` — WRK item tracking only (no specs or docs)

**`plans/` does not exist.** Planning lives in WRK item body (Route A/B) or `specs/wrk/` (Route C).


## Where WRK items reside


Single location: `workspace-hub/.claude/work-queue/` only.
Submodule repos must NOT have their own WRK items.


## Module-based folder structure (canonical)


```
src/<package>/<domain>/<component>/   ← source code
tests/<domain>/unit/                  ← fast unit tests
tests/<domain>/integration/           ← component tests
tests/<domain>/fixtures/              ← test data
docs/modules/<domain>/                ← reference docs
data/modules/<domain>/                ← input data
```

NOT `tests/modules/<domain>/` — the `modules/` wrapper in tests is redundant.


## Provider adapter directories (canonical 2026-02-18)


```
.codex/
  skills → ../.claude/skills  (symlink)
  prompts/                     ← provider-specific prompt templates
  settings.json
.gemini/
  skills → ../.claude/skills  (symlink)
  prompts/                     ← provider-specific prompt templates
  settings.json
```

- Skills live in `.claude/skills/` only — `.codex/skills` and `.gemini/skills` are symlinks
- Provider prompts compensate for lack of skill marketplace in Codex/Gemini
- `config/agents/` holds: `model-registry.yaml`, `provider-capabilities.yaml`, `ai-agents-registry.json`, `behavior-contract.yaml`


## Shell agent test scripts


- `scripts/agents/tests/test-*.sh` — harness tests for workflow-guards.sh, execute.sh routing
- Run with `bash scripts/agents/tests/test-name.sh`; exit 0 = pass, 1 = fail
- NOT placed in `tests/` (which is for Python packages); shell scripts stay under their `scripts/` home

---
