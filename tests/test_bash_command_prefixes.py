from __future__ import annotations

from scripts.bash_command_prefixes import cleanup_bash_command, normalize_command_to_prefix


def test_cleanup_bash_command_removes_comments_and_cd_wrapper() -> None:
    raw = "# comment\ncd /tmp/repo && uv run --no-project python tool.py\n"

    assert cleanup_bash_command(raw) == "uv run --no-project python tool.py"


def test_normalize_command_to_prefix_without_cleanup_preserves_first_token() -> None:
    assert normalize_command_to_prefix("cd /tmp/repo && uv run --no-project python tool.py") == "cd"


def test_normalize_command_to_prefix_with_cleanup_uses_multiword_prefix() -> None:
    assert normalize_command_to_prefix(
        "cd /tmp/repo && uv run --no-project python tool.py", cleanup=True
    ) == "uv run"


def test_cleanup_bash_command_strips_inline_env_assignments() -> None:
    raw = "cd /tmp/repo && GIT_PAGER=cat git status --short"

    assert cleanup_bash_command(raw) == "git status --short"


def test_normalize_command_to_prefix_with_cleanup_ignores_env_prefixed_command() -> None:
    assert normalize_command_to_prefix(
        "GIT_OPTIONAL_LOCKS=0 git status --short",
        cleanup=True,
    ) == "git status"
