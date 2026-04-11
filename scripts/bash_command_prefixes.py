from __future__ import annotations

BASH_MULTI_WORD_PREFIXES: tuple[tuple[str, ...], ...] = (
    ("git", "diff"),
    ("git", "log"),
    ("git", "add"),
    ("git", "commit"),
    ("git", "push"),
    ("git", "pull"),
    ("git", "fetch"),
    ("git", "checkout"),
    ("git", "status"),
    ("git", "rebase"),
    ("git", "merge"),
    ("git", "stash"),
    ("git", "show"),
    ("git", "branch"),
    ("git", "reset"),
    ("git", "tag"),
    ("git", "cherry-pick"),
    ("git", "rev-parse"),
    ("git", "rev-list"),
    ("git", "hash-object"),
    ("git", "update-index"),
    ("git", "write-tree"),
    ("git", "commit-tree"),
    ("git", "update-ref"),
    ("uv", "run"),
    ("uv", "tool"),
    ("uv", "add"),
    ("uv", "sync"),
    ("python", "-m"),
    ("python3", "-m"),
)


def cleanup_bash_command(command: str) -> str:
    text = command.strip()
    if not text:
        return text
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
    text = " ".join(lines).strip()
    if text.startswith("cd ") and "&&" in text:
        before, after = text.split("&&", 1)
        if before.strip().startswith("cd "):
            return after.strip()
    return text


def normalize_command_to_prefix(command: str, *, cleanup: bool = False) -> str:
    if cleanup:
        command = cleanup_bash_command(command)
    command = command.strip()
    if not command:
        return command

    tokens = command.split()
    first_token = tokens[0]
    if first_token.startswith("./") or first_token.startswith("/"):
        return first_token

    for prefix_words in BASH_MULTI_WORD_PREFIXES:
        n = len(prefix_words)
        if len(tokens) >= n and tuple(tokens[:n]) == prefix_words:
            return " ".join(prefix_words)

    return tokens[0]
