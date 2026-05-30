"""#2814: context.md must stay in sync with the bridge heredoc, and describe the
real (sibling) repo layout.

`.claude/memory/context.md` is generated verbatim from the QUOTED heredoc
(`cat > context.md << 'CONTEXT_EOF' ... CONTEXT_EOF`) in `bridge-hermes-claude.sh` —
a quoted heredoc does NO variable expansion, so the committed file must be byte-identical
to the template body. Drift between them (the bridge not re-run after a template edit) is
exactly the #2814 bug: the committed context.md carried a stale *nested* repo-layout claim
while the repos are siblings at `/mnt/local-analysis/`.
"""

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BRIDGE = REPO / "scripts" / "memory" / "bridge-hermes-claude.sh"
CONTEXT = REPO / ".claude" / "memory" / "context.md"

TIER1_SIBLINGS = ("digitalmodel", "worldenergydata", "assetutilities", "assethold",
                  "aceengineer-strategy")


def _extract_heredoc(text: str) -> str:
    """Return the literal body of the `context.md` heredoc in the bridge script."""
    out, capturing = [], False
    for ln in text.splitlines():
        if not capturing:
            if "context.md" in ln and "<< 'CONTEXT_EOF'" in ln:
                capturing = True
            continue
        if ln == "CONTEXT_EOF":
            break
        out.append(ln)
    return "\n".join(out)


def test_context_md_matches_bridge_heredoc():
    # The generated file must equal its template body — else the bridge wasn't re-run and
    # context.md is stale (the root-cause drift behind #2814).
    heredoc = _extract_heredoc(BRIDGE.read_text())
    assert heredoc, "could not locate the context.md heredoc in bridge-hermes-claude.sh"
    committed = CONTEXT.read_text().rstrip("\n")
    assert committed == heredoc.rstrip("\n"), (
        "context.md has drifted from the bridge heredoc template — regenerate it from the "
        "template (re-run the bridge or re-extract the heredoc) so they match (#2814)")


def test_context_md_layout_is_sibling_not_nested():
    txt = CONTEXT.read_text()
    assert "SIBLINGS at `/mnt/local-analysis/<repo>`" in txt
    for repo in TIER1_SIBLINGS:
        assert f"/mnt/local-analysis/{repo}/" in txt, f"missing sibling path for {repo}"
    # the stale nested framing must be gone
    assert "energy data sub-repo" not in txt
    assert "private GTM strategy repo, nested" not in txt
