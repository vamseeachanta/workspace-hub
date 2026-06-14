from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import yaml

CLEANUP_ALIASES = frozenset({"ace", "personal"})
SKESTATES_ATTENTION_CHANNEL = "Telegram: Family - Finance"


class AccountMappingError(ValueError):
    """Raised when queue-state account config cannot safely target Gmail."""


@dataclass(frozen=True)
class Account:
    alias: str
    email: str | None = None
    enabled: bool = True
    cleanup_enabled: bool = False
    retention_policy: str = "keep_forever"
    attention_method: str | None = "starred"
    attention_channel: str | None = None


@dataclass(frozen=True)
class NormalizedAccount:
    raw: str
    alias: str | None
    status: str
    cleanup_enabled: bool = False


class AccountScope:
    def __init__(self, accounts: Mapping[str, Account]):
        self.accounts = dict(accounts)
        self._email_to_alias = {
            account.email.lower(): alias
            for alias, account in self.accounts.items()
            if account.email
        }

    @classmethod
    def default(cls) -> "AccountScope":
        return cls(
            {
                "ace": Account(
                    alias="ace",
                    enabled=True,
                    cleanup_enabled=True,
                    retention_policy="local_purge_after_grace",
                    attention_method=None,
                ),
                "personal": Account(
                    alias="personal",
                    enabled=True,
                    cleanup_enabled=True,
                    retention_policy="local_purge_after_grace",
                    attention_method=None,
                ),
                "skestates": Account(
                    alias="skestates",
                    email="skestatesinc@gmail.com",
                    enabled=True,
                    cleanup_enabled=False,
                    retention_policy="keep_forever",
                    attention_method="starred",
                    attention_channel=SKESTATES_ATTENTION_CHANNEL,
                ),
            }
        )

    def enabled_aliases(self) -> set[str]:
        return {
            alias
            for alias, account in self.accounts.items()
            if account.enabled
        }

    def cleanup_aliases(self) -> set[str]:
        return {
            alias
            for alias, account in self.accounts.items()
            if account.enabled and account.cleanup_enabled
        }

    def normalize(self, account_id: str) -> NormalizedAccount:
        raw = str(account_id)
        key = raw.lower()
        alias = raw if raw in self.accounts else self._email_to_alias.get(key)
        if alias is None:
            return NormalizedAccount(raw=raw, alias=None, status="config_missing")
        status = "enabled" if self.accounts[alias].enabled else "out_of_scope"
        return NormalizedAccount(
            raw=raw,
            alias=alias,
            status=status,
            cleanup_enabled=status == "enabled" and self.accounts[alias].cleanup_enabled,
        )

    def cleanup_enabled(self, account_id: str) -> bool:
        normalized = self.normalize(account_id)
        return bool(normalized.alias and normalized.cleanup_enabled)

    def require_enabled(self, account_id: str) -> str:
        normalized = self.normalize(account_id)
        if normalized.status != "enabled" or normalized.alias is None:
            raise AccountMappingError(
                f"account '{account_id}' is {normalized.status}"
            )
        return normalized.alias


def resolve_state_dir(env: Mapping[str, str] | None = None) -> Path:
    active_env = os.environ if env is None else env
    return Path(active_env.get("EMAIL_QUEUE_STATE_DIR", "~/.hermes/email-state")).expanduser()


def resolve_accounts_config(
    config_path: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> Path:
    active_env = os.environ if env is None else env
    if config_path is not None:
        return Path(config_path).expanduser()
    if active_env.get("EMAIL_QUEUE_ACCOUNTS_CONFIG"):
        return Path(active_env["EMAIL_QUEUE_ACCOUNTS_CONFIG"]).expanduser()
    return resolve_state_dir(active_env) / "accounts.yaml"


def load_account_scope(
    config_path: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> AccountScope:
    path = resolve_accounts_config(config_path, env)
    if not path.exists():
        return AccountScope.default()

    with path.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}

    accounts = dict(AccountScope.default().accounts)
    for alias, data in payload.get("accounts", {}).items():
        if data is None:
            data = {}
        enabled = bool(data.get("enabled", True))
        cleanup_enabled = (
            alias in CLEANUP_ALIASES
            and enabled
            and bool(data.get("cleanup_enabled", True))
        )
        accounts[alias] = Account(
            alias=alias,
            email=data.get("email"),
            enabled=enabled,
            cleanup_enabled=cleanup_enabled,
            retention_policy=data.get("retention_policy")
            or ("local_purge_after_grace" if cleanup_enabled else "keep_forever"),
            attention_method=data.get("attention_method")
            or (None if cleanup_enabled else "starred"),
            attention_channel=data.get("attention_channel")
            or (SKESTATES_ATTENTION_CHANNEL if alias == "skestates" else None),
        )
    return AccountScope(accounts or AccountScope.default().accounts)
