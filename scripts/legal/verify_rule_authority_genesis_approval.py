"""Strict parser for the canonical rule-authority genesis approval record."""

from __future__ import annotations

import json
import posixpath
import re
import uuid


MAX_APPROVAL = 16_384
_OID = re.compile(r"[0-9a-f]{40}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_FINGERPRINT = re.compile(r"SHA256:[A-Za-z0-9+/]{43}\Z")
_MAJOR_MINOR = re.compile(r"[0-9]+:[0-9]+\Z")


def _error() -> ValueError:
    return ValueError("invalid canonical genesis approval")


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise _error()
        result[key] = value
    return result


def _keys(value, expected):
    if type(value) is not dict or set(value) != set(expected):
        raise _error()


def _string(value, pattern=None, *, absolute=False):
    if type(value) is not str or not value or len(value.encode("utf-8")) > 4096:
        raise _error()
    if any(ord(char) < 0x20 or ord(char) == 0x7F for char in value):
        raise _error()
    if absolute and not value.startswith("/"):
        raise _error()
    if pattern is not None and pattern.fullmatch(value) is None:
        raise _error()


def _identity(value):
    _keys(value, {"path", "blob_oid", "sha256"})
    _string(value["path"], absolute=False)
    if value["path"].startswith("/") or posixpath.normpath(value["path"]) != value["path"]:
        raise _error()
    _string(value["blob_oid"], _OID)
    _string(value["sha256"], _SHA256)


def _uuid4(value):
    _string(value)
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError) as exc:
        raise _error() from exc
    if parsed.version != 4 or str(parsed) != value:
        raise _error()


def _host(value):
    _keys(value, {"hostname", "machine_id_sha256", "ssh_host_key", "account", "output_parent", "mount"})
    if value["hostname"] != "ace-linux-1":
        raise _error()
    _string(value["hostname"])
    _string(value["machine_id_sha256"], _SHA256)
    key = value["ssh_host_key"]
    _keys(key, {"path", "key_type", "sha256_fingerprint"})
    _string(key["path"], absolute=True)
    _string(key["key_type"])
    _string(key["sha256_fingerprint"], _FINGERPRINT)
    account = value["account"]
    _keys(account, {"name", "uid", "home"})
    _string(account["name"])
    if type(account["uid"]) is not int or not 1 <= account["uid"] <= 2**31 - 1:
        raise _error()
    _canonical_absolute(account["home"])
    _canonical_absolute(value["output_parent"])
    home = account["home"].rstrip("/")
    if not value["output_parent"].startswith(home + "/"):
        raise _error()
    mount = value["mount"]
    _keys(mount, {"mount_id", "major_minor", "root", "mountpoint", "filesystem_type", "source", "options"})
    if type(mount["mount_id"]) is not int or mount["mount_id"] <= 0:
        raise _error()
    _string(mount["major_minor"], _MAJOR_MINOR)
    for field in ("root", "mountpoint", "source"):
        _canonical_absolute(mount[field])
    if mount["filesystem_type"] not in {"ext4", "xfs", "btrfs"}:
        raise _error()
    _string(mount["filesystem_type"])
    options = mount["options"]
    if type(options) is not list or any(type(item) is not str or not item for item in options):
        raise _error()
    if options != sorted(options) or len(options) != len(set(options)):
        raise _error()


def _canonical_absolute(value):
    _string(value, absolute=True)
    if posixpath.normpath(value) != value or "//" in value:
        raise _error()


def parse_canonical_approval(data: bytes):
    if type(data) is not bytes or not data or len(data) > MAX_APPROVAL:
        raise _error()
    if data.startswith(b"\xef\xbb\xbf") or not data.endswith(b"\n") or b"\r" in data:
        raise _error()
    try:
        value = json.loads(
            data.decode("utf-8"),
            object_pairs_hook=_pairs,
            parse_float=lambda _: (_ for _ in ()).throw(_error()),
            parse_constant=lambda _: (_ for _ in ()).throw(_error()),
        )
    except (UnicodeError, json.JSONDecodeError, ValueError):
        raise _error()
    try:
        canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii") + b"\n"
    except (TypeError, ValueError) as exc:
        raise _error() from exc
    if canonical != data:
        raise _error()
    _keys(value, {"schema_id", "git_object_format", "plan_commit", "tool_commit_a", "caller_commit_b", "post_merge_main", "transaction_id", "contract", "launcher", "execution_manifest", "approval_verifier", "outer_bootstrap", "python", "host"})
    if value["schema_id"] != "legal-rule-genesis-approval-v1" or value["git_object_format"] != "sha1":
        raise _error()
    for field in ("plan_commit", "tool_commit_a", "caller_commit_b", "post_merge_main"):
        _string(value[field], _OID)
    _uuid4(value["transaction_id"])
    for field in ("contract", "launcher", "execution_manifest", "approval_verifier"):
        _identity(value[field])
    _keys(value["outer_bootstrap"], {"sha256"})
    _string(value["outer_bootstrap"]["sha256"], _SHA256)
    _keys(value["python"], {"realpath", "sha256"})
    _canonical_absolute(value["python"]["realpath"])
    _string(value["python"]["sha256"], _SHA256)
    _host(value["host"])
    return value
