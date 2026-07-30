---
name: crossprovider codex headless-automation-requires-pats-not-browser-ba
description: Headless automation requires PATs, not browser-based auth; plan for gh --with-token upfront
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [automation, headless, github]
---

SSH-provisioned headless boxes cannot run `gh auth login` (browser-based OAuth). Must provide a GitHub PAT via `--with-token` flag as a precondition for provisioning scripts. This is non-obvious for code that assumes local interactive auth will work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
