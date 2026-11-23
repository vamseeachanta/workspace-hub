"""
Tests for WRK-1119: defined permission model.

Validates that .claude/settings.json deny-list and allow-list are correctly structured
and cover the minimum required patterns (AC4, AC7).
"""
import json
from pathlib import Path
import pytest

SETTINGS_PATH = Path(__file__).parents[2] / ".claude" / "settings.json"


@pytest.fixture(scope="module")
def settings():
    return json.loads(SETTINGS_PATH.read_text())


@pytest.fixture(scope="module")
def permissions(settings):
    return settings.get("permissions", {})


@pytest.fixture(scope="module")
def allow_list(permissions):
    return permissions.get("allow", [])


@pytest.fixture(scope="module")
def deny_list(permissions):
    return permissions.get("deny", [])


# ---------------------------------------------------------------------------
# AC4: Deny list covers minimum required dangerous patterns
# ---------------------------------------------------------------------------

class TestDenyList:
    REQUIRED_DENY_PATTERNS = [
        "Bash(rm -rf /)",
        "Bash(chmod 777:*)",
        "Bash(sudo:*)",
        "Bash(git push --force:*)",
        "Bash(git push -f:*)",
        "Bash(eval:*)",
    ]

    def test_deny_list_exists(self, deny_list):
        """Deny list must be non-empty."""
        assert len(deny_list) > 0, "permissions.deny must not be empty"

    @pytest.mark.parametrize("pattern", REQUIRED_DENY_PATTERNS)
    def test_required_deny_pattern_present(self, deny_list, pattern):
        """Each minimum-required dangerous pattern must appear in the deny list."""
        assert pattern in deny_list, (
            f"Required deny pattern missing: {pattern}\n"
            f"Current deny list: {deny_list}"
        )

    def test_no_wildcard_allow_all(self, deny_list):
        """Deny list must not contain a catch-all that blocks everything."""
        assert "Bash(*)" not in deny_list, "Deny list must not block all Bash commands"


# ---------------------------------------------------------------------------
# AC1: Allow list covers the essential ecosystem commands
# ---------------------------------------------------------------------------

class TestAllowList:
    REQUIRED_ALLOW_PATTERNS = [
        "Bash(uv run:*)",       # Python runtime (python-runtime.md)
        "Bash(git:*)",          # Git operations
        "Bash(grep:*)",         # File search
        "Bash(find:*)",         # File search
        "Bash(ls:*)",           # Directory listing
        "Bash(bash:*)",         # Shell scripts
        "Bash(gh:*)",           # GitHub CLI
    ]

    def test_allow_list_has_minimum_entries(self, allow_list):
        """Allow list must have at least 20 entries to be useful."""
        assert len(allow_list) >= 20, (
            f"Allow list too sparse: {len(allow_list)} entries (need >= 20)"
        )

    @pytest.mark.parametrize("pattern", REQUIRED_ALLOW_PATTERNS)
    def test_required_allow_pattern_present(self, allow_list, pattern):
        """Each critical ecosystem command must be in the allow list."""
        assert pattern in allow_list, (
            f"Required allow pattern missing: {pattern}\n"
            f"Current allow list: {allow_list}"
        )


# ---------------------------------------------------------------------------
# AC2: settings.json is well-formed and has the required top-level structure
# ---------------------------------------------------------------------------

class TestSettingsStructure:
    def test_settings_file_exists(self):
        assert SETTINGS_PATH.exists(), f"settings.json not found at {SETTINGS_PATH}"

    def test_settings_is_valid_json(self):
        content = SETTINGS_PATH.read_text()
        parsed = json.loads(content)
        assert isinstance(parsed, dict)

    def test_permissions_block_present(self, settings):
        assert "permissions" in settings, "settings.json must have a 'permissions' key"

    def test_both_allow_and_deny_present(self, permissions):
        assert "allow" in permissions, "permissions must have 'allow' list"
        assert "deny" in permissions, "permissions must have 'deny' list"

    def test_allow_and_deny_are_lists(self, permissions):
        assert isinstance(permissions["allow"], list)
        assert isinstance(permissions["deny"], list)

    def test_no_duplicate_allow_entries(self, allow_list):
        duplicates = [p for p in allow_list if allow_list.count(p) > 1]
        assert not duplicates, f"Duplicate allow patterns: {set(duplicates)}"

    def test_no_duplicate_deny_entries(self, deny_list):
        duplicates = [p for p in deny_list if deny_list.count(p) > 1]
        assert not duplicates, f"Duplicate deny patterns: {set(duplicates)}"
