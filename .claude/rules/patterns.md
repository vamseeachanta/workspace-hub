# Design Patterns Rules — Universal

## Enforcement Gradient

Rules exist on a maturity spectrum. Move rules toward stronger enforcement over time:

| Level | Mechanism | Reliability | When to use |
|---|---|---|---|
| 0 — Prose | Skill file | Lowest — only if invoked | Broad guidance |
| 1 — Micro-skill | Per-stage file, auto-loaded | Medium — guaranteed at stage entry | Stage-specific checklists |
| 2 — Script | Shell/Python, called from skill or CI | High — auditable, testable | Binary checks: did/didn't |
| 3 — Hook | pre-commit / stop-hook | Strongest — fires automatically | Must-never-miss enforcement |

Migration path: when a prose rule can be expressed as exit 0/1, write a script. When it must fire on every commit, promote to a hook.
