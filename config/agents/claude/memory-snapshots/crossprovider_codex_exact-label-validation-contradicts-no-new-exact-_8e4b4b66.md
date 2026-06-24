---
name: crossprovider codex exact-label-validation-contradicts-no-new-exact-
description: Exact-label validation contradicts no-new-exact-label-map requirement
metadata:
  type: reference
  source: codex
  bridged: 2026-06-23
  tags: [privacy-governance-risk, exact-label-containment, llm-wiki-dnv]
---

Sessions #759–#762 all found the same contradiction: plans ban storing new exact-label maps in tracked config/tests while also requiring exact source-label identity validation. Current updater stores `source_label` in config fields (dnv_batch_models.py:14, :155) and compares report rows against them, making validation inseparable from map persistence. Proposals to use 'non-reversible commitments/oracles' remained underspecified. Resolve by either (a) defining a concrete non-reversible scheme (keyed HMAC with external key, fail-closed real runs, synthetic-only tests), or (b) downgrading the claim to root/syntax validation only, not per-row identity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
