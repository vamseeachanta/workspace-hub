---
name: feedback_third_party_skill_pack_screening
description: Screening heuristic before adopting third-party skill packs into the ecosystem skills tree
metadata: 
  node_type: memory
  type: feedback
  originSessionId: be1efb2f-7da6-40d6-aad5-6d430bae3330
---

Before importing any third-party skill pack (e.g. `mattpocock/skills`) into `.claude/skills/`, screen each skill against ecosystem conflicts — do NOT bulk-install.

**Why:** third-party packs encode the author's workflow assumptions, some of which actively break ours. From the 2026-05-23 mattpocock/skills review (Core 6 adopted, 4 rejected):
- `git-guardrails-claude-code` blocks `git push`/`reset` via hooks → would break our push-based autosync + feature-branch preservation (`push --no-verify`).
- `setup-pre-commit` installs Husky/lint-staged/Prettier (JS/TS) → conflicts with our Python+`uv` toolchain and existing Iron-Law/secrets-scan hooks.
- `to-prd`/`to-issues`/`triage`/`review` → duplicate/conflict with GSD (our sole workflow), GitHub-issues-only rule, and existing cross-review policy. The pack's README is explicitly anti-GSD.

**How to apply:** adopt only composable, model-agnostic, gap-filling skills (e.g. diagnose, grill-me, zoom-out, handoff, tdd, improve-codebase-architecture). Reject anything that (a) installs push/git-blocking hooks, (b) assumes a JS/TS toolchain, or (c) owns process steps GSD already owns. Inject `source:`/`license:` provenance frontmatter on import. `SKILLS_GRAPH.yaml` + category `INDEX.md` are generated artifacts — don't hand-edit; regenerate. See [[feedback_skill_before_code]], [[project_gsd_migration]].
