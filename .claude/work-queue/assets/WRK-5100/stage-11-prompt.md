# Stage 11 Prompt Package — WRK-5100
## Stage: Artifact Generation
**Invocation:** task_agent
**Weight:** medium
**Context budget:** 8 KB

## Exit artifacts (must exist before calling exit-stage.sh)

## Stage Micro-Skill (rules for this stage)
```
Stage 11 · Artifact Generation | task_agent | medium | single-thread
Entry: evidence/execute.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Verify all evidence YAML files present for stages completed so far
2. Run: uv run --no-project python scripts/knowledge/update-github-issue.py WRK-NNN --update
3. Confirm GitHub issue body reflects current stage progress and evidence
4. Check required evidence files present (files changed, test results, gate summary)
Data formats:
- Evidence files: YAML (agent-written structured data); prose sections: Markdown
- Never use markdown tables for structured data agents write
- File extensions: .yaml (not .yml), .md, .json (script-generated deterministic output only)
- YAML comments allowed as inline instructions (e.g. `# HARD RULE: ...`)
Exit: GitHub issue updated with execution evidence

```

## Entry reads

### assets/WRK-NNN/evidence/execute.yaml
```
[entry_reads: assets/WRK-NNN/evidence/execute.yaml — file not found]
```

**Blocking condition:** GitHub Issue not updated with stage progress