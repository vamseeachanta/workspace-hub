---
name: crossprovider gemini pep-735-dependency-groups-require-all-groups-wit
description: PEP 735 dependency-groups require --all-groups with uv sync
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [uv, dependency-management, pep735, ci-workflow]
---

When packages are declared in both `[project.optional-dependencies]` and `[dependency-groups]` (PEP 735), `uv sync --all-extras` installs optional-deps but NOT PEP 735 groups. CI workflows must explicitly use `--all-groups` or `--group <name>` to install them. Local dev envs may have different install paths, masking the gap until CI runs.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
