"""Descriptor-bound, manifest-attested first-commit finalization."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import unicodedata

from .bootstrap_git import (
    BootstrapGitError, author_env, isolated_env, mutation_command, push_command,
    validate_clone_config,
)
from .bootstrap_layout import BoundCloneLayout, bind_clone
from .bootstrap_bound_manifest import (
    BoundManifestError, BoundValidationContext, bind_validation_context,
    validate_bound_context,
)
from .bootstrap_objects import expected_tree
from .bootstrap_remote import remote_state as _remote
from .bootstrap_renderer import RenderTokens, _render_member
from .bootstrap_schema import get_entry, load_registry, validate_root_disjointness
from .bootstrap_snapshot import TemplateMember, load_committed_snapshot


MESSAGE = b"chore: initialize metadata-only client wiki\n"
_OID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
_EMAIL = re.compile(
    r"[A-Za-z0-9][A-Za-z0-9._+-]{0,63}@[A-Za-z0-9]"
    r"(?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+"
)
_ATTESTED_OPERATIONS = frozenset({
    "hash_object", "mktree", "commit_tree", "cas", "read_tree",
    "push", "api_query", "final_return",
})
@dataclass(frozen=True, slots=True)
class FinalizeResidue:
    kind: str
    commit_oid: str | None
    tree_oid: str | None
    object_oids: tuple[str, ...]
    instruction: str = "preserve clone; inspect and retry only through finalize-scaffold"
class BootstrapFinalizerError(RuntimeError):
    def __init__(self, message: str, *, residue: FinalizeResidue | None = None):
        super().__init__(message)
        self.residue = residue
def _run(command: list[str], *, env: dict[str, str], fds: tuple[int, ...],
         input: bytes | None = None, timeout: int = 15) -> subprocess.CompletedProcess[bytes]:
    """Private fixed operation seam; all children remain bounded and isolated."""
    return subprocess.run(
        command, input=input, check=False, capture_output=True, env=env,
        pass_fds=fds, timeout=timeout,
    )
def _git(bound: BoundCloneLayout, *args: str, input: bytes | None = None,
         author: bool = False) -> bytes:
    command = mutation_command(bound.git_fd, *args)
    try:
        result = _run(
            command, env=author_env() if author else isolated_env(),
            fds=(bound.git_fd, bound.root_fd, bound.config_fd), input=input,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BootstrapFinalizerError("bounded Git operation failed") from exc
    if result.returncode:
        raise BootstrapFinalizerError("bounded Git operation rejected")
    return result.stdout
def _identity() -> tuple[str, str]:
    values = author_env()
    name, email = values["GIT_AUTHOR_NAME"], values["GIT_AUTHOR_EMAIL"]
    if (name != unicodedata.normalize("NFC", name) or name != name.strip()
            or not 1 <= len(name) <= 100):
        raise BootstrapFinalizerError("author name grammar is invalid")
    if any(unicodedata.category(char) == "Cc" for char in name) or any(
        char in "<>\r\n\0" for char in name
    ):
        raise BootstrapFinalizerError("author name grammar is invalid")
    try:
        name.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise BootstrapFinalizerError("author name grammar is invalid") from exc
    try:
        encoded = email.encode("ascii")
    except UnicodeEncodeError as exc:
        raise BootstrapFinalizerError("author email grammar is invalid") from exc
    if not 3 <= len(encoded) <= 254 or _EMAIL.fullmatch(email) is None:
        raise BootstrapFinalizerError("author email grammar is invalid")
    return name, email
def _rendered_members(template: Path, entry) -> tuple[object, tuple[TemplateMember, ...]]:
    snapshot = load_committed_snapshot(template)
    tokens = RenderTokens(
        entry.short_name, entry.short_name.upper(), entry.repo,
        entry.raw_source_status, entry.ingestion_enabled,
    )
    rendered = tuple(_render_member(member, tokens) for member in snapshot.members)
    return snapshot, rendered
def _independent_attestation(context: BoundValidationContext) -> None:
    try:
        validate_bound_context(context)
    except Exception as exc:
        raise BootstrapFinalizerError("independent bound attestation failed") from exc


def _with_attestation(context, operation: str, callback):
    """Private named seam bracketing one external or mutating operation."""
    if operation not in _ATTESTED_OPERATIONS:
        raise BootstrapFinalizerError("unnamed attested operation")
    _independent_attestation(context)
    try:
        return callback()
    finally:
        _independent_attestation(context)
def _reject_git_surfaces(bound: BoundCloneLayout) -> None:
    paths = (
        "objects/info/alternates", "objects/info/http-alternates", "info/grafts", "shallow",
    )
    for path in paths:
        try:
            os.stat(path, dir_fd=bound.git_fd, follow_symlinks=False)
        except FileNotFoundError:
            continue
        raise BootstrapFinalizerError(f"forbidden Git authority surface: {path}")
    _reject_hooks(bound)
    _reject_replacements(bound)
def _reject_hooks(bound: BoundCloneLayout) -> None:
    hooks = os.open("hooks", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=bound.git_fd)
    try:
        for name in os.listdir(hooks):
            info = os.stat(name, dir_fd=hooks, follow_symlinks=False)
            sample = name.endswith(".sample") and stat.S_ISREG(info.st_mode)
            if not sample and (not stat.S_ISREG(info.st_mode) or info.st_mode & 0o111):
                raise BootstrapFinalizerError("executable or non-regular Git hook rejected")
    finally:
        os.close(hooks)
def _reject_replacements(bound: BoundCloneLayout) -> None:
    try:
        replace = os.open("refs/replace", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                          dir_fd=bound.git_fd)
    except FileNotFoundError:
        replace = -1
    if replace >= 0:
        try:
            if os.listdir(replace):
                raise BootstrapFinalizerError("loose replacement refs rejected")
        finally:
            os.close(replace)
    try:
        packed = os.open("packed-refs", os.O_RDONLY | os.O_NOFOLLOW, dir_fd=bound.git_fd)
    except FileNotFoundError:
        return
    try:
        data = os.read(packed, 8 * 1024 * 1024 + 1)
    finally:
        os.close(packed)
    if len(data) > 8 * 1024 * 1024 or b"refs/replace" in data:
        raise BootstrapFinalizerError("packed or malformed replacement refs rejected")


def _build_tree(context: BoundValidationContext, members: tuple[TemplateMember, ...]) -> tuple[str, ...]:
    bound = context.clone
    blobs: dict[str, tuple[int, str]] = {}
    created: list[str] = []
    for member in members:
        if member.data is None:
            continue
        oid = _with_attestation(context, "hash_object", lambda: _git(
            bound, "hash-object", "-w", "--stdin", input=member.data,
        )).strip().decode()
        if _OID.fullmatch(oid) is None:
            raise BootstrapFinalizerError("Git returned malformed blob OID")
        blobs[member.path] = (member.mode, oid)
        created.append(oid)
    tree = _mktree(context, blobs, "", created)
    return (*created, tree)


def _expected_tree(bound: BoundCloneLayout, members: tuple[TemplateMember, ...]) -> str:
    algorithm = _git(bound, "rev-parse", "--show-object-format").strip().decode()
    try:
        return expected_tree(algorithm, members)
    except ValueError as exc:
        raise BootstrapFinalizerError("repository object format is unsupported") from exc


def _mktree(context: BoundValidationContext, blobs: dict[str, tuple[int, str]], prefix: str,
            created: list[str]) -> str:
    bound = context.clone
    files: list[bytes] = []
    directories = sorted({PurePosixPath(path[len(prefix):]).parts[0] for path in blobs
                          if path.startswith(prefix) and "/" in path[len(prefix):]})
    for name in directories:
        oid = _mktree(context, blobs, f"{prefix}{name}/", created)
        files.append(f"040000 tree {oid}\t{name}\0".encode())
    for path, (mode, oid) in sorted(blobs.items()):
        suffix = path[len(prefix):] if path.startswith(prefix) else path
        if "/" not in suffix:
            files.append(f"{mode:o} blob {oid}\t{suffix}\0".encode())
    oid = _with_attestation(context, "mktree", lambda: _git(
        bound, "mktree", "-z", input=b"".join(files),
    )).strip().decode()
    if _OID.fullmatch(oid) is None:
        raise BootstrapFinalizerError("Git returned malformed tree OID")
    created.append(oid)
    return oid


def _head(bound: BoundCloneLayout) -> str | None:
    try:
        head_info = os.stat("HEAD", dir_fd=bound.git_fd, follow_symlinks=False)
    except OSError as exc:
        raise BootstrapFinalizerError("HEAD is unavailable") from exc
    if not stat.S_ISREG(head_info.st_mode):
        raise BootstrapFinalizerError("HEAD must be a regular file")
    symbolic = _run(
        mutation_command(bound.git_fd, "symbolic-ref", "-q", "HEAD"),
        env=isolated_env(), fds=(bound.git_fd,),
    )
    if symbolic.returncode or symbolic.stdout != b"refs/heads/main\n":
        raise BootstrapFinalizerError("HEAD must symbolically name refs/heads/main")
    result = _run(
        mutation_command(bound.git_fd, "rev-parse", "--verify", "HEAD^{commit}"),
        env=isolated_env(), fds=(bound.git_fd,),
    )
    if result.returncode:
        return None
    oid = result.stdout.strip().decode()
    if _OID.fullmatch(oid) is None:
        raise BootstrapFinalizerError("local HEAD OID is malformed")
    return oid


def _validate_commit(bound: BoundCloneLayout, oid: str, tree: str,
                     identity: tuple[str, str]) -> None:
    raw = _git(bound, "cat-file", "commit", oid)
    if b"\0" in raw or b"\r" in raw:
        raise BootstrapFinalizerError("root commit grammar is invalid")
    lines = raw.split(b"\n")
    if len(lines) != 6 or lines[3] != b"" or b"\n".join(lines[4:]) != MESSAGE:
        raise BootstrapFinalizerError("root commit grammar is invalid")
    if lines[0] != f"tree {tree}".encode():
        raise BootstrapFinalizerError("root commit tree differs")
    expected = f"{identity[0]} <{identity[1]}>"
    _person(lines[1], b"author ", expected)
    _person(lines[2], b"committer ", expected)


def _person(line: bytes, prefix: bytes, expected: str) -> tuple[str, str]:
    try:
        text = line.removeprefix(prefix).decode("utf-8")
    except UnicodeError as exc:
        raise BootstrapFinalizerError("root commit identity is malformed") from exc
    if not line.startswith(prefix):
        raise BootstrapFinalizerError("root commit headers are reordered")
    match = re.fullmatch(r"(.+) (-?[0-9]+) ([+-][0-9]{4})", text)
    if match is None or match.group(1) != expected:
        raise BootstrapFinalizerError("root commit identity is malformed")
    timestamp, zone = int(match.group(2)), match.group(3)
    hour, minute = int(zone[1:3]), int(zone[3:])
    if not -(2**63) <= timestamp <= 2**63 - 1 or hour > 23 or minute > 59:
        raise BootstrapFinalizerError("root commit timestamp is malformed")
    return match.group(1), match.group(2) + " " + zone


def _index_exact(bound: BoundCloneLayout, tree: str) -> bool:
    result = _run(mutation_command(bound.git_fd, "write-tree"), env=isolated_env(),
                  fds=(bound.git_fd,))
    return result.returncode == 0 and result.stdout.strip().decode() == tree


def _push(context: BoundValidationContext, repo: str, oid: str) -> None:
    bound = context.clone
    try:
        _run(push_command(bound.git_fd, repo, oid), env=isolated_env(),
             fds=(bound.git_fd,), timeout=60)
    except BaseException:
        pass


def _remote_attested(context: BoundValidationContext, repo: str, expected: str | None):
    return _with_attestation(context, "api_query", lambda: _remote(repo, expected))


def _initial_commit(context: BoundValidationContext,
                    entry, snapshot, members, tree: str) -> tuple[str, tuple[str, ...]]:
    bound = context.clone
    if _remote_attested(context, entry.repo, None)[0] != "absent":
        raise BootstrapFinalizerError("remote main is not authoritatively absent")
    if _git(bound, "ls-files", "-z"):
        raise BootstrapFinalizerError("unborn clone index is not empty")
    objects = _build_tree(context, members)
    if objects[-1] != tree:
        raise BootstrapFinalizerError("constructed tree differs from independent tree")
    commit = _with_attestation(context, "commit_tree", lambda: _git(
        bound, "commit-tree", tree, input=MESSAGE, author=True,
    )).strip().decode()
    objects = (*objects, commit)
    try:
        _with_attestation(context, "cas", lambda: _git(
            bound, "update-ref", "refs/heads/main", commit, _zero_oid(commit),
        ))
    except BootstrapFinalizerError as exc:
        residue = FinalizeResidue("git_objects_cas_failed", commit, tree, objects)
        raise BootstrapFinalizerError("main CAS failed", residue=residue) from exc
    try:
        _with_attestation(context, "read_tree", lambda: _git(bound, "read-tree", tree))
    except BootstrapFinalizerError as exc:
        residue = FinalizeResidue("local_commit_index_incomplete", commit, tree, objects)
        raise BootstrapFinalizerError("index population failed", residue=residue) from exc
    return commit, objects


def _zero_oid(oid: str) -> str:
    if _OID.fullmatch(oid) is None:
        raise BootstrapFinalizerError("CAS object ID is malformed")
    return "0" * len(oid)


def _recover_commit(context: BoundValidationContext, head: str, tree: str,
                    identity: tuple[str, str]) -> str:
    bound = context.clone
    raw_tree = _git(bound, "show", "-s", "--format=%T", head).strip().decode()
    if raw_tree != tree:
        raise BootstrapFinalizerError("local commit tree differs")
    _validate_commit(bound, head, tree, identity)
    if not _index_exact(bound, tree):
        _with_attestation(context, "read_tree", lambda: _git(bound, "read-tree", tree))
    return head


def _transport(context: BoundValidationContext,
               entry, snapshot, commit: str, tree: str) -> None:
    bound = context.clone
    _independent_attestation(context)
    if _head(bound) != commit:
        raise BootstrapFinalizerError("HEAD changed before transport")
    state, _ = _remote_attested(context, entry.repo, commit)
    if state == "absent":
        _with_attestation(context, "push", lambda: _push(context, entry.repo, commit))
    if _head(bound) != commit:
        raise BootstrapFinalizerError("HEAD changed during transport")
    state, _observed = _remote_attested(context, entry.repo, commit)
    if state != "equal":
        kind = "pushed_remote_advanced" if state == "different" else "remote_unknown"
        residue = FinalizeResidue(kind, commit, tree, (commit, tree))
        raise BootstrapFinalizerError(kind, residue=residue)


def finalize_scaffold(registry_path: Path, short_name: str,
                      manifest_path: Path) -> dict[str, object]:
    """Authorize, construct/recover, and publish exactly one root commit."""
    entry = get_entry(load_registry(Path(registry_path)), short_name)
    if entry.status != "planned":
        raise BootstrapFinalizerError("finalization requires a planned registry entry")
    from .bootstrap_contract import _template_worktree, derive_workspace_layout
    template = _template_worktree().absolute()
    layout = derive_workspace_layout(template, entry.repo)
    validate_root_disjointness(entry, [str(template), str(layout.canonical_checkout), str(layout.target)])
    snapshot, members = _rendered_members(template, entry)
    identity = _identity()
    with bind_clone(layout.target) as bound:
        try:
            validate_clone_config(bound, entry.repo)
        except BootstrapGitError as exc:
            raise BootstrapFinalizerError("clone config authorization failed") from exc
        _reject_git_surfaces(bound)
        try:
            with bind_validation_context(
                bound, Path(manifest_path), entry.repo, snapshot.commit_oid,
                snapshot.tree_oid, members,
            ) as context:
                head = _head(bound)
                tree = _expected_tree(bound, members)
                if head is None:
                    commit, _objects = _initial_commit(context, entry, snapshot, members, tree)
                else:
                    commit = _recover_commit(context, head, tree, identity)
                _transport(context, entry, snapshot, commit, tree)
                _with_attestation(context, "final_return", lambda: None)
        except BoundManifestError as exc:
            raise BootstrapFinalizerError("bound manifest validation failed") from exc
    return {"commit_oid": commit, "remote": "equal", "repo": entry.repo,
            "short_name": entry.short_name, "status": "finalized", "tree_oid": tree}


def residue_json(error: BootstrapFinalizerError) -> str:
    payload = {"error": "finalize_failed"}
    if error.residue is not None:
        payload["residue"] = asdict(error.residue)
    return json.dumps(payload, sort_keys=True)
