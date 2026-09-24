---
name: crossprovider codex scope-inconsistency-in-acceptance-criteria-enabl
description: Scope inconsistency in acceptance criteria enables implementer discretion
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [acceptance-criteria, scope, mandatory-vs-optional, task-consistency]
---

Using conditional language ('if included') in acceptance criteria while task lists make the same item mandatory creates discretion where the issue author intended none. Example: plan #607 marked `run-orcawave-from-mesh` as both required (task line 72-74) and optional (acceptance line 152). Implementation can omit without violating stated acceptance.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
