# WRK-1094 Cross-Review — Codex — Phase 1

Verdict: REQUEST_CHANGES

## MAJOR Findings (addressed in plan v2)

1. AGENTS.md contract ambiguity (validate_agent_contract.sh vs YAML frontmatter) → RESOLVED:
   clarified that both coexist; script checks YAML, validate_agent_contract.sh checks pointer.

2. Severity inconsistency (FAIL vs WARN) → RESOLVED: explicit per-rule severity table added to plan.

3. Hard-FAIL on known violations blocks pushes immediately → RESOLVED: ratchet/baseline approach
   — only NEW regressions beyond baseline are FAIL; existing debt is WARN.

4. Propagation check underspecified → RESOLVED: dropped from Route A scope.

5. Pre-push scope too narrow (hub only) → RESOLVED: changed to check all changed harness files
   in push set (hub + submodules) using existing changed-repo detection.

## MINOR Findings (addressed)

- Timestamped report + stable `latest` symlink → RESOLVED: added to plan.

## Disposition
All MAJOR findings addressed in plan v2. No deferred items.
