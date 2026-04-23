"""Shared types for the ecosystem-sync cron."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Literal

SignalKind = Literal["release", "case-study", "readme-diff", "showcase"]


@dataclass(frozen=True)
class Signal:
    repo: str
    kind: SignalKind
    title: str
    body: str
    dedupe_key: str
    payload: dict[str, Any] = field(default_factory=dict)
