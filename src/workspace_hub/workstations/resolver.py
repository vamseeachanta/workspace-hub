from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import yaml


@dataclass(frozen=True)
class MachineRecord:
    key: str
    hostname: str
    hostname_aliases: tuple[str, ...]
    os: str
    workspace_root: str | None
    ssh: str | None
    raw: dict[str, Any]

    @property
    def identifiers(self) -> tuple[str, ...]:
        values = [self.key, self.hostname, *self.hostname_aliases]
        if self.ssh:
            values.append(self.ssh)
        return tuple(values)


class WorkstationPathResolver:
    def __init__(self, machines: dict[str, MachineRecord]) -> None:
        self._machines = machines
        self._id_to_key: dict[str, str] = {}
        for key, machine in machines.items():
            for identifier in machine.identifiers:
                if identifier:
                    self._id_to_key[identifier.lower()] = key

    @classmethod
    def from_registry_path(cls, registry_path: Path) -> "WorkstationPathResolver":
        payload = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
        raw_machines = payload.get("machines", {}) or {}
        machines: dict[str, MachineRecord] = {}
        for key, raw in raw_machines.items():
            machine = MachineRecord(
                key=key,
                hostname=str(raw.get("hostname", "")),
                hostname_aliases=tuple(raw.get("hostname_aliases", []) or []),
                os=str(raw.get("os", "")),
                workspace_root=raw.get("workspace_root"),
                ssh=raw.get("ssh"),
                raw=dict(raw),
            )
            machines[key] = machine
        return cls(machines)

    @classmethod
    def for_repo(cls, repo_root: Path) -> "WorkstationPathResolver":
        return cls.from_registry_path(repo_root / "config" / "workstations" / "registry.yaml")

    def resolve_machine(self, identifier: str | None) -> MachineRecord | None:
        if not identifier:
            return None
        key = self._id_to_key.get(str(identifier).strip().lower())
        if key is None:
            return None
        return self._machines[key]

    def field_for(self, identifier: str | None, field: str) -> Any:
        machine = self.resolve_machine(identifier)
        if machine is None:
            return ""
        if field == "key":
            return machine.key
        return machine.raw.get(field, "")

    def valid_machine_identifiers(self) -> list[str]:
        identifiers: set[str] = set()
        for machine in self._machines.values():
            identifiers.update(filter(None, machine.identifiers))
        return sorted(identifiers)

    def rewrite_workspace_path(self, raw_path: str | None, current_repo_root: Path) -> str:
        text = str(raw_path or "").strip()
        if not text:
            return ""
        current_repo_root = current_repo_root.resolve()
        for machine in self._machines.values():
            suffix = self._workspace_suffix(text, machine)
            if suffix is None:
                continue
            if not suffix:
                return "."
            # This shared normalizer intentionally strips only known machine
            # workspace prefixes. Callers still decide whether the rewritten
            # suffix belongs to the current checkout/worktree.
            return suffix
        return text

    def _workspace_suffix(self, raw_path: str, machine: MachineRecord) -> str | None:
        root = machine.workspace_root
        if not root:
            return None
        normalized_path = self._normalize_for_matching(raw_path)
        for prefix in self._workspace_prefixes(machine):
            normalized_prefix = self._normalize_for_matching(prefix)
            if normalized_path == normalized_prefix:
                return ""
            prefix_slash = normalized_prefix.rstrip("/") + "/"
            if normalized_path.startswith(prefix_slash):
                suffix = normalized_path[len(prefix_slash) :]
                return PurePosixPath(suffix).as_posix()
        return None

    def _workspace_prefixes(self, machine: MachineRecord) -> tuple[str, ...]:
        root = str(machine.workspace_root or "").strip()
        if not root:
            return ()
        prefixes = {root, root.rstrip("/\\")}
        if machine.os.lower() == "windows":
            normalized = root.replace("\\", "/")
            prefixes.add(normalized)
            drive, _, tail = normalized.partition(":/")
            if drive and tail:
                prefixes.add(f"/{drive.lower()}/{tail}")
        return tuple(filter(None, prefixes))

    @staticmethod
    def _normalize_for_matching(value: str) -> str:
        normalized = str(value).replace("\\", "/")
        while "//" in normalized:
            normalized = normalized.replace("//", "/")
        if len(normalized) >= 2 and normalized[1] == ":":
            normalized = normalized[0].lower() + normalized[1:]
        elif len(normalized) >= 3 and normalized[0] == "/" and normalized[2] == "/" and normalized[1].isalpha():
            normalized = f"/{normalized[1].lower()}{normalized[2:]}"
        return normalized.rstrip("/") or "/"
