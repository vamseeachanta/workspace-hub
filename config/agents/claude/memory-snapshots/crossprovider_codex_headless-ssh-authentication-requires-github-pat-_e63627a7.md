---
name: crossprovider codex headless-ssh-authentication-requires-github-pat-
description: Headless SSH authentication requires GitHub PAT, not browser login
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [ssh, github-cli, headless-auth]
---

On headless nodes without browser access, `gh auth login --with-token` requires a pre-generated GitHub PAT. Browser-based OAuth flow is not available; plan for HITL token provisioning before provisioning headless infrastructure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
