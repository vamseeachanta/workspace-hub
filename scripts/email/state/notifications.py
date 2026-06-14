from __future__ import annotations

import json
from typing import Any, Mapping

ATTENTION_JOB = "email-queue-attention"


def attention_notification_events(
    report: Mapping[str, Any],
    *,
    source: str = "email",
    job: str = ATTENTION_JOB,
) -> list[dict[str, str]]:
    events: list[dict[str, str]] = []
    for route in report.get("attention_routes", []):
        details = {
            "account": _safe_account_alias(str(route["account_id"])),
            "attention_channel": route.get("attention_channel"),
            "attention_method": route.get("attention_method"),
            "pending_count": int(route["pending_count"]),
        }
        events.append(
            {
                "source": source,
                "job": job,
                "status": "fail",
                "details": json.dumps(details, sort_keys=True),
            }
        )
    return events


def _safe_account_alias(account_id: str) -> str:
    if "@" in account_id:
        return "configured-account"
    return account_id
