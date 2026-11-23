# Root Artifact Classification

> Issue: #1534 | Date: 2026-03-31

## Classification Table

### Zero-Byte Malformed Files (DELETE — shell/workflow residue)

All are git-tracked, zero-byte, and appear to be mermaid diagram node names or markdown metadata that leaked into filenames during shell mishaps.

| File | Origin (likely) | Action |
|------|-----------------|--------|
| `-` | Shell argument parsing error | DELETE |
| `B[Resource` | Mermaid diagram node | DELETE |
| `C[Triage]` | Mermaid diagram node | DELETE |
| `Comprehensive` | Partial markdown text | DELETE |
| `D` | Mermaid diagram node | DELETE |
| `D[Plan` | Mermaid diagram node | DELETE |
| `E{User` | Mermaid diagram node | DELETE |
| `F1[Revise` | Mermaid diagram node | DELETE |
| `F[Multi-Agent` | Mermaid diagram node | DELETE |
| `G{Plan` | Mermaid diagram node | DELETE |
| `H` | Mermaid diagram node | DELETE |
| `H1[Recommend` | Mermaid diagram node | DELETE |
| `H[Claim]` | Mermaid diagram node | DELETE |
| `I{Best-Fit` | Mermaid diagram node | DELETE |
| `K` | Mermaid diagram node | DELETE |
| `K[Execute]` | Mermaid diagram node | DELETE |
| `M{Route` | Mermaid diagram node | DELETE |
| `N` | Mermaid diagram node | DELETE |
| `N[Close]` | Mermaid diagram node | DELETE |
| `O{Queue` | Mermaid diagram node | DELETE |
| `P[Archive]` | Mermaid diagram node | DELETE |
| `Shared` | Partial markdown text | DELETE |
| `Use` | Partial markdown text | DELETE |
| `**Date:**` | Markdown metadata leak | DELETE |
| `**Goal:**` | Markdown metadata leak | DELETE |
| `**Scope:**` | Markdown metadata leak | DELETE |
| `**Status:**` | Markdown metadata leak | DELETE |

### Non-Zero Shell Residue (DELETE)

| File | Size | Origin | Action |
|------|------|--------|--------|
| `echo` | 47B | Shell command captured as file | DELETE |
| `exit: ` (trailing space) | 47B | Shell command captured as file | DELETE |

### Application Residue (DELETE)

| File | Size | Origin | Action |
|------|------|--------|--------|
| `paraview.80s-478634,ace-linux-2.btr` | 1.2KB | ParaView crash dump | DELETE |
| `--version.cvg` | ? | CLI flag captured as file | DELETE |
| `--version.dat` | ? | CLI flag captured as file | DELETE |
| `--version.sta` | ? | CLI flag captured as file | DELETE |

### Development Scratch Files (DELETE — stale, git-tracked)

| File | Size | Origin | Action |
|------|------|--------|--------|
| `dummy-pre-commit-config.yaml` | 185B | Hook testing leftover | DELETE |
| `dummy-pre-push.sh` | 88B | Hook testing leftover | DELETE |
| `reproduce_bug.py` | 2.2KB | Bug repro script (stale) | DELETE |
| `test_regex.py` | 339B | Regex test (stale) | DELETE |
| `test-output.md` | 7.5KB | Test output dump | DELETE |
| `WRK-677-review.md` | 2.7KB | Work item review (stale local ref) | DELETE |

### Legitimate Root Files (KEEP)

| File | Size | Purpose |
|------|------|---------|
| `AGENTS.md` | 832B | Canonical workflow contract |
| `CLAUDE.md` | 473B | Claude configuration |
| `GEMINI.md` | 419B | Gemini configuration |
| `MEMORY.md` | 710B | Memory tracking |
| `README.md` | 3.5KB | Project overview |
| `pyproject.toml` | 774B | Python project metadata |
| `uv.lock` | 96KB | UV package lock |

---

## Recommended Guardrails

1. **Pre-commit hook**: Reject files with `[`, `{`, `*`, or zero-byte at root level
2. **Gitignore patterns**: Add patterns for common shell residue (`echo`, `exit*`, `*.btr`, `--version.*`)
3. **Periodic audit**: Run `find . -maxdepth 1 -size 0 -type f` as a CI check

## Execution

Safe to remove all DELETE items in a single commit. All are git-tracked, so they can be recovered from history if needed.
