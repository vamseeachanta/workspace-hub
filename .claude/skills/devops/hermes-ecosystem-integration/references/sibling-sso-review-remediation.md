# Sibling SSoT Review Remediation Notes

Use this when a sibling single-source-of-truth (SSoT) implementation has green targeted tests but adversarial review still returns MAJOR.

## Failure Pattern

A live checker and repair helper can both iterate the full workstation registry while the implementation/test fixture only covers starter repos. If acceptance criteria say `check-sibling-sso-flow.py --machine <machine> --json` must PASS for memory/skills/harness_contracts/registry, do not close on a partial starter-repo pass.

## AGENTS.md Contract Rewrite Edge Case

Real sibling repos may express canonical contract inheritance as prose split across two lines:

```md
This repository inherits the canonical contract from:
../AGENTS.md
```

The repair manifest should treat this as a safe contract pointer rewrite to `../workspace-hub/AGENTS.md`, but it must still block arbitrary prose such as:

```md
Notes: literal ../AGENTS.md in prose should not be auto-rewritten.
```

Recommended TDD shape:

1. Add a manifest test that a repo with the two-line inheritance phrase emits `kind == "rewrite_agents_pointer"`.
2. Add a rewrite test proving only the target line after the inheritance phrase is rewritten.
3. Keep/verify the arbitrary-prose blocker test remains red/blocked for unrelated mentions.

## PyYAML Fallback Guard

If a Bash sync script feeds Python on stdin and imports `yaml`, every render/validate/merge path must use the same dependency-aware launcher. Do not fix only render while leaving validate/merge on `uv run --no-project python` or bare `python3` when PyYAML may be absent.

Expected launcher shape:

```bash
uv run --with pyyaml --no-project python "$@"
```

Use it consistently anywhere inline Python imports `yaml`.

## Closeout Gate

Before commit/push/issue closeout after a MAJOR review:

- rerun the exact modified test file(s), not only the previously green suite;
- rerun the live checker for the named machine;
- rerun dry-run repair manifest and inspect any remaining blocked repos;
- explicitly classify each previous MAJOR finding as fixed, stale-with-evidence, or accepted-by-user;
- do not claim PASS if full registry acceptance still fails.
