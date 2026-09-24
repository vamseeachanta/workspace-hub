---
name: crossprovider codex hermes-partially-installed-but-not-integrated-pr
description: Hermes partially installed but not integrated; prior decision to avoid adoption
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hermes, installation-debt, provider-evaluation]
---

Hermes CLI launcher exists at `~/.local/bin/hermes` and source at `~/.hermes/hermes-agent/`, but fails at startup with `ModuleNotFoundError: prompt_toolkit`. Workspace control plane does not recognize Hermes (only Claude, Codex, Gemini). Prior evaluation issue #1467 concluded 2026-03-28: extract useful patterns, do not adopt Hermes as the framework. Any future Hermes use requires dependency fix, control-plane decision, and justification against that prior conclusion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
