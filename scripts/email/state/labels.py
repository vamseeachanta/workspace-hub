from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from .accounts import AccountMappingError, AccountScope


LABEL_TAXONOMY = (
    "wh-email/extracted",
    "wh-email/awaiting-reply",
    "wh-email/completed",
    "wh-email/noise",
)


def ensure_labels(
    *,
    account_scope: AccountScope | None = None,
    clients_by_account: Mapping[str, Any] | None = None,
    gmail_client_factory: Callable[[str], Any] | None = None,
    helper_account_map: Mapping[str, str] | None = None,
    apply: bool = False,
) -> dict[str, Any]:
    scope = account_scope or AccountScope.default()
    _check_helper_mapping(scope, helper_account_map or {})
    operations = [
        {"account_id": alias, "label": label, "action": "create_if_missing"}
        for alias in sorted(scope.enabled_aliases())
        for label in LABEL_TAXONOMY
    ]

    if not apply:
        return {"applied": False, "operations": operations}

    clients = _resolve_clients(scope, clients_by_account, gmail_client_factory)
    for operation in operations:
        _ensure_client_label(clients[operation["account_id"]], operation["label"])
    return {"applied": True, "operations": operations}


def _check_helper_mapping(
    scope: AccountScope,
    helper_account_map: Mapping[str, str],
) -> None:
    for alias in scope.enabled_aliases():
        configured = scope.accounts[alias].email
        helper_email = helper_account_map.get(alias)
        if configured and helper_email and configured.lower() != helper_email.lower():
            raise AccountMappingError(
                f"queue-state account '{alias}' maps to {configured}, "
                f"but Gmail helper maps to {helper_email}"
            )


def _resolve_clients(
    scope: AccountScope,
    clients_by_account: Mapping[str, Any] | None,
    gmail_client_factory: Callable[[str], Any] | None,
) -> dict[str, Any]:
    clients = {}
    for alias in sorted(scope.enabled_aliases()):
        client = None
        if clients_by_account and alias in clients_by_account:
            client = clients_by_account[alias]
        elif gmail_client_factory is not None:
            client = gmail_client_factory(alias)
        if client is None:
            raise AccountMappingError(f"missing Gmail client for account '{alias}'")
        clients[alias] = client
    return clients


def _ensure_client_label(client: Any, label: str) -> None:
    if hasattr(client, "ensure_label"):
        client.ensure_label(label)
        return
    if hasattr(client, "create_label"):
        client.create_label(label)
        return
    users = getattr(client, "users", None)
    if callable(users):
        body = {"name": label, "labelListVisibility": "labelShow"}
        users().labels().create(userId="me", body=body).execute()
        return
    raise AccountMappingError("Gmail client lacks a supported label method")
