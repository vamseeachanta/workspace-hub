"""Bridge context template contract after X02 private memory routing."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BRIDGE = REPO / "scripts" / "memory" / "bridge-hermes-claude.sh"


def _extract_heredoc(text: str) -> str:
    out, capturing = [], False
    for line in text.splitlines():
        if not capturing:
            if "context.md" in line and "<< 'CONTEXT_EOF'" in line:
                capturing = True
            continue
        if line == "CONTEXT_EOF":
            break
        out.append(line)
    return "\n".join(out)


def test_context_template_describes_private_memory_sink():
    heredoc = _extract_heredoc(BRIDGE.read_text(encoding="utf-8"))

    assert heredoc
    assert "private claude-memory-snapshots repository" in heredoc
    assert "hosts/<role-slug>/memory/" in heredoc
    assert "public workspace-hub repository is not a memory snapshot sink" in heredoc


def test_context_template_uses_role_slugs_not_physical_names():
    heredoc = _extract_heredoc(BRIDGE.read_text(encoding="utf-8"))

    assert "ace-win-1" in heredoc
    assert "licensed-win" not in heredoc
    assert "/mnt/local-analysis" not in heredoc
