# Hermes Local Patches

Patches applied by harness-update.sh after each hermes update.
Replaces the need to fork NousResearch/hermes-agent.

## Creating a patch
cd ~/.hermes/hermes-agent
git diff > ~/workspace-hub/config/agents/hermes/patches/my-fix.patch

## Current patches
None — shebang is handled by hermes update itself.
