---
name: crossprovider codex cross-repo-ci-dependencies-need-explicit-install
description: Cross-repo CI dependencies need explicit installation mechanism on hosted runners
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ci, dependencies, github-actions]
---

When a workflow depends on a sibling repository (e.g., `assetutilities` via path source in `pyproject.toml`), the plan must specify how the runner makes that available: checkout step, git URL, or published package. Leaving it as a risk item or phase-2 conditional means the plan has identified the problem but not solved it.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
