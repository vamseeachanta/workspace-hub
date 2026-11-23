Another focused #2045 patch wave landed locally after Codex rereview13:

- narrowed the deliverable so it matches the actual tests more closely
- made the exemplar-plan handling decisively read-only for #2046/#2047 under #2045
- fixed the execution block so test failures propagate via `set -euo pipefail`
- clarified that the operational test validates allowed policy states, not one fixed label state

Launching another focused Codex rerun now.
