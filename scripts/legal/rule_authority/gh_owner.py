"""Owner-attended GitHub transport for a dual-slot authority promotion."""

from __future__ import annotations

import json
import os
import re
import subprocess

from .codec import AuthorityError


ENVIRONMENT = "legal-rule-authority"
NAME = re.compile(r"[A-Z][A-Z0-9_]{0,99}")
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
OID = re.compile(r"[0-9a-f]{40}")
MAX_OUTPUT = 65536


class GhOwnerTransport:
    """Use ``gh`` for remote metadata CAS and secret mutation.

    GitHub does not return Actions secret values. The exact values therefore
    remain in the owner process, while remote secret metadata supplies the
    compare/write/readback boundary. Secret bodies travel only over stdin.
    """

    def __init__(self, current_name, pending_name, repository=None, runner=None):
        if (
            os.environ.get("GITHUB_ACTIONS")
            or os.environ.get("LEGAL_RULE_OWNER_PROMOTE") != "1"
            or not NAME.fullmatch(current_name)
            or not NAME.fullmatch(pending_name)
            or current_name == pending_name
        ):
            raise AuthorityError("config")
        if repository is not None and not REPOSITORY.fullmatch(repository):
            raise AuthorityError("config")
        self.current_name = current_name
        self.pending_name = pending_name
        self._repository = repository
        self._runner = runner or subprocess.run
        self._baseline = None
        self._values = {}
        self._written = None

    def _run(self, *arguments, input_value=None):
        environment = os.environ.copy()
        environment.pop(self.current_name, None)
        environment.pop(self.pending_name, None)
        try:
            result = self._runner(
                ["gh", *arguments],
                input=input_value,
                text=True,
                capture_output=True,
                check=False,
                timeout=30,
                env=environment,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise AuthorityError("integrity") from exc
        output = result.stdout
        if (
            result.returncode != 0
            or not isinstance(output, str)
            or len(output.encode("utf-8")) > MAX_OUTPUT
        ):
            raise AuthorityError("integrity")
        return output

    @property
    def repository(self):
        if self._repository is None:
            configured = os.environ.get("GITHUB_REPOSITORY", "")
            if configured:
                self._repository = configured
            else:
                self._repository = self._run(
                    "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"
                ).strip()
            if not REPOSITORY.fullmatch(self._repository):
                raise AuthorityError("integrity")
        return self._repository

    def _metadata(self):
        raw = self._run(
            "secret",
            "list",
            "--env",
            ENVIRONMENT,
            "--repo",
            self.repository,
            "--json",
            "name,updatedAt",
        )
        try:
            values = json.loads(raw)
        except (json.JSONDecodeError, UnicodeError) as exc:
            raise AuthorityError("integrity") from exc
        if not isinstance(values, list) or len(values) > 1000:
            raise AuthorityError("integrity")
        selected = {}
        for item in values:
            if not isinstance(item, dict) or set(item) != {"name", "updatedAt"}:
                raise AuthorityError("integrity")
            name, updated = item["name"], item["updatedAt"]
            if not isinstance(name, str) or not isinstance(updated, str) or not updated:
                raise AuthorityError("integrity")
            if name in selected:
                raise AuthorityError("integrity")
            if name in {self.current_name, self.pending_name}:
                selected[name] = updated
        return selected

    def _snapshot(self):
        current = self._metadata()
        if self._baseline is None:
            if set(current) != {self.current_name, self.pending_name}:
                raise AuthorityError("integrity")
            self._baseline = current
        return current

    def read_slot(self, name):
        if name not in {self.current_name, self.pending_name}:
            raise AuthorityError("config")
        metadata = self._snapshot()
        if self._written is None:
            if metadata != self._baseline:
                raise AuthorityError("integrity")
            value = os.environ.get(name)
            if not value:
                raise AuthorityError("config")
            if name in self._values and self._values[name] != value:
                raise AuthorityError("integrity")
            self._values[name] = value
            return value

        if name == self.current_name:
            if (
                metadata.get(self.current_name) == self._baseline[self.current_name]
                or metadata.get(self.pending_name) != self._baseline[self.pending_name]
            ):
                raise AuthorityError("integrity")
            return self._written
        if metadata.get(self.pending_name) != self._baseline[self.pending_name]:
            raise AuthorityError("integrity")
        return self._values[self.pending_name]

    def read_main(self):
        head = self._run(
            "api",
            f"repos/{self.repository}/git/ref/heads/main",
            "--jq",
            ".object.sha",
        ).strip()
        if not OID.fullmatch(head):
            raise AuthorityError("integrity")
        tree = self._run(
            "api",
            f"repos/{self.repository}/git/commits/{head}",
            "--jq",
            ".tree.sha",
        ).strip()
        if not OID.fullmatch(tree):
            raise AuthorityError("integrity")
        return {"head_oid": head, "tree_oid": tree}

    def write_slot(self, name, value):
        if (
            name != self.current_name
            or self._written is not None
            or value != self._values.get(self.pending_name)
        ):
            raise AuthorityError("integrity")
        self._run(
            "secret",
            "set",
            name,
            "--env",
            ENVIRONMENT,
            "--repo",
            self.repository,
            input_value=value,
        )
        self._written = value

    def delete_slot(self, name):
        if name != self.pending_name or self._written is None:
            raise AuthorityError("integrity")
        before = self._snapshot()
        if (
            before.get(self.current_name) == self._baseline[self.current_name]
            or before.get(self.pending_name) != self._baseline[self.pending_name]
        ):
            raise AuthorityError("integrity")
        self._run(
            "secret",
            "delete",
            name,
            "--env",
            ENVIRONMENT,
            "--repo",
            self.repository,
        )
        after = self._metadata()
        if name in after or after.get(self.current_name) != before.get(
            self.current_name
        ):
            raise AuthorityError("integrity")
