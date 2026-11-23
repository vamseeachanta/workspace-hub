# Skill Eval Framework

> WRK-1009 | Version 1

## Purpose

Provide a deterministic, schema-validated mechanism to verify that SKILL.md files meet
documented capability and procedural contracts without requiring LLM reasoning.

## Schema Versioning

All eval YAML files must include `version: 1` at the top level. Schema changes that break
backward compatibility require a version bump and migration note here.

## Eval YAML Structure

```yaml
version: 1
wrk_id: WRK-NNNN             # WRK that owns this eval definition
skill_name: <name>            # Must match `name:` in SKILL.md frontmatter
skill_path: <relative-path>   # Path to SKILL.md from repo root
evals:
  - eval_id: <short-id>       # Unique within this file (e.g. wq-cap-01)
    eval_type: capability | procedural
    description: <human-readable purpose>
    checks:
      required_sections:      # List of strings that must appear verbatim in body
        - "## Section Name"
      required_commands:      # List of command strings that must appear in body
        - "/work add"
```

## Eval Types

| Type | Meaning |
|------|---------|
| `capability` | Checks that the skill documents a specific command or feature |
| `procedural` | Checks that the skill documents a workflow section or process |

## Result Semantics

| Result | Meaning |
|--------|---------|
| `pass` | All checks in the eval passed |
| `fail` | One or more checks not found in the SKILL.md body |
| `skip` | Skill file not found at `skill_path` (non-blocking) |

## JSONL Output Fields

Each eval check emits one record to `.claude/state/skill-eval-results/YYYY-MM-DD.jsonl`:

```json
{
  "run_id": "<uuid4>",
  "skill_name": "<name>",
  "skill_path": "<path>",
  "eval_id": "<eval-id>",
  "eval_type": "capability|procedural",
  "result": "pass|fail|skip",
  "reason": "<human-readable explanation>",
  "timestamp": "<ISO8601-UTC>",
  "source_eval": "<path-to-eval-yaml>"
}
```

## Retirement Threshold

A skill is flagged as a RETIREMENT CANDIDATE when **both** conditions hold:

- `baseline_usage_rate < 0.05` (less than 5% of sessions)
- `calls_in_period < 10` (fewer than 10 invocations in the tracked period)

If either field is absent or null in `skill-scores.yaml`, the result is **SKIP** (no data).

## Atomic Write Policy

All state files are written atomically:
1. Write to `<target>.tmp`
2. `mv <target>.tmp <target>`

This prevents partial reads from concurrent processes.

## Cron Failure Policy

`skill-curation-nightly.sh` uses `set -uo pipefail` (no `-e`) and every sub-step uses
`|| true` or `|| echo WARNING` to ensure one failure does not abort the full pipeline.
The nightly pipeline is non-blocking — failures are logged, not fatal.

## Eval Definitions Location

All eval YAML files live in `specs/skills/evals/`. File naming: `<skill-name>.yaml`.

## Candidate Proposals on FAIL

When `run_skill_evals.py` records a `fail` result, it writes a proposal to:
`.claude/state/skill-eval-candidates/YYYY-MM-DD-<skill_name>.yaml`

Fields: `skill_name`, `skill_path`, `failing_evals[]`, `suggested_action`, `wrk_id`.
