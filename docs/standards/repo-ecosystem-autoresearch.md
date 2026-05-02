# Repo Ecosystem Autoresearch

Issue #2417 generalizes the old skill-only autoresearch loop into a bounded
runner for prompt-bearing repo assets.

## Runner

Use:

```bash
uv run --no-project python scripts/skills/repo_ecosystem_autoresearch.py --target-type skill --dry-run
uv run --no-project python scripts/skills/repo_ecosystem_autoresearch.py --target-type agent --dry-run
uv run --no-project python scripts/skills/repo_ecosystem_autoresearch.py --target-type template --dry-run
uv run --no-project python scripts/skills/repo_ecosystem_autoresearch.py --target-type workflow-config --dry-run
```

The legacy skill entry point remains:

```bash
bash scripts/cron/skill-autoresearch-nightly.sh --dry-run
```

That wrapper delegates to the generic runner with `--target-type skill`.

## Supported Targets

| Target type | Discovery rule | Evaluator |
|---|---|---|
| `skill` | `.claude/skills/**/SKILL.md` | existing skill-eval script when available; static text fallback |
| `agent` | `.claude/agents/**/*.md` excluding `README.md` | frontmatter/name metadata plus static text checks |
| `template` | `.claude/get-shit-done/templates/**/*` text assets | static text checks plus placeholder-marker check |
| `workflow-config` | explicit allowlist only | syntax checks for YAML/JSON plus static text checks |

The v1 `workflow-config` allowlist is intentionally tight:

- `config/scheduled-tasks/schedule-tasks.yaml`
- `.planning/gsd-defaults.json`
- `.planning/ROADMAP.md`
- `.planning/milestones/v1.0-ROADMAP.md`

Do not broaden workflow-config discovery without a new plan/review, because
unbounded config scanning was a prior review blocker.

## Evaluator Contract

Each evaluator is a callable that accepts a `Path` and returns:

```python
Evaluation(warnings=int, criticals=int, findings=list[str])
```

The keep/revert predicate is deterministic:

- revert if `criticals_after > 0`
- keep if criticals decrease
- keep if warnings decrease without criticals
- otherwise revert as `revert-no-improve`

This preserves the old safety behavior while allowing target-specific
evaluators to supply their own findings.

## Results

The generalized artifact is additive JSONL at:

```text
.claude/state/skill-autoresearch/results.jsonl
```

Each row includes:

- `target_type`
- `target_path`
- `warnings_before`
- `warnings_after`
- `criticals_before`
- `criticals_after`
- `result`
- `duration_s`
- before/after finding lists

The legacy skill wrapper also appends the old TSV schema at:

```text
.claude/state/skill-autoresearch/results.tsv
```

This avoids breaking downstream consumers that still expect a `skill` column.

## Safety Model

Non-dry runs create or resume an `autoresearch/*` branch from `main`, stash dirty
state before switching branches, commit kept improvements through
`scripts/cron/lib/git-safe.sh`, and never auto-merge. Rejected candidates restore
the original file content and are still recorded in the JSONL result artifact.
