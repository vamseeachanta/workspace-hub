---
name: digitalmodel-worktree-test-execution-with-shared-venv
description: Run digitalmodel tests from isolated worktrees without uv editable-dependency failures by using the main repo's existing virtualenv and PYTHONPATH.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# digitalmodel worktree test execution with shared venv

> Paths below use `$WORKROOT` = the directory holding your sibling repo checkouts and worktrees
> (`/mnt/local-analysis` on Linux dev machines; adjust for your platform). `digitalmodel`,
> `assetutilities`, and `worktrees/` are siblings under `$WORKROOT`.

## When to use

Use this when:
- you are working in a git worktree of `digitalmodel`
- `uv run` in that worktree fails or tries to rebuild the environment
- the failure mentions editable/local dependencies like `assetutilities==0.1.0 @ editable+../assetutilities`
- you need fast, deterministic test execution from a side worktree

Typical symptom:
- `uv run python -m pytest ...` fails in the worktree because `../assetutilities` resolves relative to the worktree path rather than the main repo layout
- or `uv run` creates a fresh `.venv` in the worktree and breaks because sibling editable paths are missing

## Why this happens

`digitalmodel` depends on local editable sibling repos. In an isolated worktree, relative editable paths can stop resolving the way they do in the main checkout. The main repo already has a working environment, so reusing it is safer than rebuilding from the worktree.

## Preferred fix

Run tests from the worktree using the main repo's existing virtualenv interpreter and explicit `PYTHONPATH=src`.

Canonical pattern:

```bash
cd $WORKROOT/worktrees/<digitalmodel-worktree>
PYTHONPATH=src $WORKROOT/digitalmodel/.venv/bin/python -m pytest <target> -q
```

Examples:

```bash
cd $WORKROOT/worktrees/digitalmodel-issue-26
PYTHONPATH=src $WORKROOT/digitalmodel/.venv/bin/python -m pytest tests/solvers/blender_automation/test_blender_wrapper.py -q

cd $WORKROOT/worktrees/digitalmodel-issue-26
PYTHONPATH=src $WORKROOT/digitalmodel/.venv/bin/python -m pytest tests/solvers/blender_automation/ -q
```

## Decision rules

1. First try the shared-venv command above before debugging package resolution.
2. If the shared-venv command passes, prefer it over `uv run` for that worktree session.
3. If the shared-venv command hangs during import/collection, treat the shared environment as broken for that worktree session rather than debugging product code first.
4. Only fall back to environment surgery if the shared venv is genuinely missing or broken.

## Shared-venv hang fallback

Sometimes the main repo `.venv` exists but hangs during `pytest` collection or even simple imports from an isolated worktree. Quick diagnosis:

```bash
cd $WORKROOT/worktrees/<digitalmodel-worktree>
timeout 30s PYTHONPATH=src $WORKROOT/digitalmodel/.venv/bin/python -c "import digitalmodel; print('ok')"
timeout 30s PYTHONPATH=src $WORKROOT/digitalmodel/.venv/bin/python -S -c "import sys; print('site-disabled-ok')"
```

If normal startup hangs but `-S` succeeds, avoid the shared venv for the targeted slice and create a local minimal test venv in the worktree:

```bash
cd $WORKROOT/worktrees/<digitalmodel-worktree>
uv venv .venv<issue>
./.venv<issue>/bin/python -m pip install 'pytest>=7,<9' 'pydantic>=2.7,<3' 'ruamel.yaml>=0.18,<1'
PYTHONPATH=src ./.venv<issue>/bin/python -m pytest <target> -q
```

Keep the local venv untracked. Remove any temporary sibling symlink workarounds after use. If `git status` is slow or times out in the worktree, retry with `git -c core.fsmonitor=false status --short --untracked-files=all` before assuming the tree is unusable.

## Good verification sequence

1. Confirm the main repo venv exists:

```bash
test -x $WORKROOT/digitalmodel/.venv/bin/python
```

2. Run the narrow failing slice from the worktree:

```bash
PYTHONPATH=src $WORKROOT/digitalmodel/.venv/bin/python -m pytest <target> -q
```

3. Run the smallest nearby regression slice after the fix.

## Optional fallback

If a tool absolutely insists on `uv run` in the worktree, a temporary symlink for the sibling dependency may unblock it, but this is not preferred:

```bash
ln -s $WORKROOT/assetutilities $WORKROOT/worktrees/assetutilities
```

Use this only as a stopgap. Prefer the shared-venv command because it is simpler and less stateful.

## Pitfalls

- Do not assume `uv run` from a worktree will reuse the main repo environment.
- Do not waste time debugging unrelated test failures until you have ruled out the editable-dependency path problem.
- Remove temporary symlink workarounds after use if you created them.

## What this pattern saved

This pattern avoided a false debugging path during a digitalmodel Blender automation hardening task where `uv run` from the worktree failed on editable `assetutilities` resolution. Using the main repo `.venv` plus `PYTHONPATH=src` made the targeted and regression test slices run cleanly from the isolated worktree.