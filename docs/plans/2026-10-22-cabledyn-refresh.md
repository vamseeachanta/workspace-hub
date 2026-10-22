# CableDyn catalog refresh plan

Tracking: Refs #3931. Scope will remain documentation and catalog metadata.

## Proposed work

- Slice 1 will refresh `cabledyn_inha` in the existing online resource registry
  against the upstream release, retaining its identity and reference-only status.
- Slice 2 will add `docs/research/cabledyn-assessment.md` with an own-words public
  assessment, pinned primary sources, retrieval evidence and validation limits.
  The existing private wiki source will remain externally owned and linked.
- Slice 3 will document the upstream coupling-step example and add offline
  regression checks in `tests/data/test_cabledyn_catalog.py`.
- The equation will be the approximate mean load delay, committed `dtM / 2`,
  from CableDyn v0.2.0 (2026), `doc/openfast.rst`, Time step. The example's
  inputs and step rounding will come from that same section. No solver response
  calculation, engineering coefficients or acceptance limits will be introduced.

## Tests and acceptance

Tests will check catalog uniqueness and counted summaries, agreement between
catalog and assessment, pinned source coverage, link resolution and the worked
example. Its hand calculation will be written in the test docstring. The new
tests and existing registry-builder tests will run with pytest; ruff will check
the new Python file. Engineering-register and whitespace checks will run directly.
No solver will be installed, imported, queried or executed.

## Adversarial plan review

The implementing provider's review identifies stale version claims, accidental
duplicate registration, conflating upstream comparisons with qualification, and
copying private wiki content into public documentation as the main risks. The
change will preserve the existing identity, cite opened public source bytes at
the release commit, and keep local qualification `NOT_EVALUATED`. The current
changelog will be checked before repeating older integration restrictions.
Independent provider review will remain pending under the task's restriction on
calling other assistants. No independent approval will be claimed.
