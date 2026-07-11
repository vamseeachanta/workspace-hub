"""Descriptor-bound finalization and recovery for issue #3449."""
from __future__ import annotations
import inspect
import hashlib
import json
from pathlib import Path
import subprocess
import pytest
import yaml

from client_llm_wiki import bootstrap_contract, bootstrap_finalizer
from client_llm_wiki.bootstrap_manifest import persist_render_manifest
from client_llm_wiki.bootstrap_layout import bind_clone
from client_llm_wiki.bootstrap_renderer import RenderTokens, bind_empty_clone, render_committed_template


def test_public_finalizer_has_only_trusted_inputs():
    assert tuple(inspect.signature(bootstrap_finalizer.finalize_scaffold).parameters) == (
        "registry_path",
        "short_name",
        "manifest_path",
    )


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True,
    ).stdout.strip()


def _fixture(tmp_path: Path, object_format: str | None = None):
    workspace = tmp_path / "ecosystem" / "workspace-hub"
    template = workspace / "templates" / "client-llm-wiki"
    (template / ".claude").mkdir(parents=True)
    (template / ".gitignore").write_text("private-output/\n")
    (template / ".claude" / "CLAUDE.md").write_text("private\n")
    (template / "README.md").write_text("# <CLIENT_SHORT_NAME>\n")
    subprocess.run(["git", "init", str(workspace)], check=True, capture_output=True)
    _git(workspace, "config", "user.name", "Fixture")
    _git(workspace, "config", "user.email", "fixture@example.test")
    _git(workspace, "add", ".")
    _git(workspace, "commit", "-m", "test: template")
    clone = workspace.parent / "llm-wiki-client"
    command = ["git", "init", "-b", "main"]
    if object_format:
        command.append(f"--object-format={object_format}")
    subprocess.run([*command, str(clone)], check=True, capture_output=True)
    repo = "org/llm-wiki-client"
    _git(clone, "remote", "add", "origin", f"https://github.com/{repo}.git")
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    manifest = evidence / "render.json"
    with bind_empty_clone(clone) as bound:
        rendered = render_committed_template(
            bound, workspace, RenderTokens("client", "CLIENT", repo, "not-mounted", False),
        )
        persist_render_manifest(
            bound, manifest, registered_repo=repo,
            allowed_origins=(f"git@github.com:{repo}.git", f"https://github.com/{repo}.git"),
            template_commit=rendered.template_commit, template_tree=rendered.template_tree,
        )
    registry = tmp_path / "registry.yml"
    registry.write_text(yaml.safe_dump({"registry_version": "0.2", "wikis": [{
        "short_name": "client", "repo": repo, "visibility": "PRIVATE",
        "posture": "client-private", "status": "planned", "raw_roots": [],
        "raw_source_status": "not-mounted", "ingestion_enabled": False,
    }]}))
    return workspace, clone, registry, manifest


def test_initial_success_constructs_exact_root_commit_and_index(tmp_path, monkeypatch):
    workspace, clone, registry, manifest = _fixture(tmp_path)
    monkeypatch.setattr(bootstrap_contract, "_template_worktree", lambda: workspace)
    states = iter((("absent", None), ("equal", "unused"), ("equal", "unused")))
    monkeypatch.setattr(bootstrap_finalizer, "_remote", lambda *_args: next(states))
    monkeypatch.setattr(bootstrap_finalizer, "_push", lambda *_args: None)
    monkeypatch.setenv("CLIENT_WIKI_GIT_AUTHOR_NAME", "Client Wiki Bot")
    monkeypatch.setenv("CLIENT_WIKI_GIT_AUTHOR_EMAIL", "client-wiki@example.com")

    result = bootstrap_finalizer.finalize_scaffold(registry, "client", manifest)

    assert result == {
        "commit_oid": result["commit_oid"], "remote": "equal", "repo": "org/llm-wiki-client",
        "short_name": "client", "status": "finalized", "tree_oid": result["tree_oid"],
    }
    assert _git(clone, "rev-list", "--parents", "-1", "HEAD").split() == [result["commit_oid"]]
    assert _git(clone, "write-tree") == result["tree_oid"]
    raw = subprocess.run(
        ["git", "-C", str(clone), "cat-file", "commit", result["commit_oid"]],
        check=True, capture_output=True,
    ).stdout
    assert raw.endswith(b"\n\nchore: initialize metadata-only client wiki\n")


def test_forged_self_consistent_manifest_and_clone_are_rejected(tmp_path, monkeypatch):
    workspace, clone, registry, manifest = _fixture(tmp_path)
    forged = b"# forged but self-consistent\n"
    (clone / "README.md").write_bytes(forged)
    claims = json.loads(manifest.read_bytes())
    claims["members"]["README.md"].update(
        size=len(forged), sha256=hashlib.sha256(forged).hexdigest(),
    )
    manifest.write_text(json.dumps(claims, sort_keys=True, separators=(",", ":")) + "\n")
    monkeypatch.setattr(bootstrap_contract, "_template_worktree", lambda: workspace)
    monkeypatch.setenv("CLIENT_WIKI_GIT_AUTHOR_NAME", "Client Wiki Bot")
    monkeypatch.setenv("CLIENT_WIKI_GIT_AUTHOR_EMAIL", "client-wiki@example.com")

    with pytest.raises(bootstrap_finalizer.BootstrapFinalizerError):
        bootstrap_finalizer.finalize_scaffold(registry, "client", manifest)

    head = subprocess.run(
        ["git", "-C", str(clone), "rev-parse", "--verify", "HEAD"],
        check=False, capture_output=True,
    )
    assert head.returncode != 0


def test_exact_local_only_retry_repairs_index_then_pushes(tmp_path, monkeypatch):
    workspace, clone, registry, manifest = _fixture(tmp_path)
    monkeypatch.setattr(bootstrap_contract, "_template_worktree", lambda: workspace)
    monkeypatch.setenv("CLIENT_WIKI_GIT_AUTHOR_NAME", "Client Wiki Bot")
    monkeypatch.setenv("CLIENT_WIKI_GIT_AUTHOR_EMAIL", "client-wiki@example.com")
    states = iter((("absent", None), ("absent", None), ("equal", None)))
    monkeypatch.setattr(bootstrap_finalizer, "_remote", lambda *_args: next(states))
    monkeypatch.setattr(bootstrap_finalizer, "_push", lambda *_args: None)
    first = bootstrap_finalizer.finalize_scaffold(registry, "client", manifest)
    _git(clone, "read-tree", "--empty")
    pushed = []
    states = iter((("absent", None), ("equal", first["commit_oid"])))
    monkeypatch.setattr(bootstrap_finalizer, "_remote", lambda *_args: next(states))
    monkeypatch.setattr(
        bootstrap_finalizer, "_push", lambda _context, _repo, oid: pushed.append(oid),
    )

    retried = bootstrap_finalizer.finalize_scaffold(registry, "client", manifest)

    assert retried == first
    assert pushed == [first["commit_oid"]]
    assert _git(clone, "write-tree") == first["tree_oid"]
    states = iter((("equal", first["commit_oid"]), ("equal", first["commit_oid"])))
    monkeypatch.setattr(bootstrap_finalizer, "_remote", lambda *_args: next(states))
    pushed.clear()
    idempotent = bootstrap_finalizer.finalize_scaffold(registry, "client", manifest)
    assert idempotent == first
    assert pushed == []


def test_cli_exposes_exact_finalize_arguments():
    args = bootstrap_contract.build_parser().parse_args([
        "finalize-scaffold", "--registry", "registry.yml", "--short-name", "client",
        "--manifest", "render.json",
    ])
    assert str(args.registry) == "registry.yml"
    assert str(args.manifest) == "render.json"


def test_author_name_rejects_surrounding_whitespace(monkeypatch):
    monkeypatch.setenv("CLIENT_WIKI_GIT_AUTHOR_NAME", " Client Wiki Bot")
    monkeypatch.setenv("CLIENT_WIKI_GIT_AUTHOR_EMAIL", "client-wiki@example.com")
    with pytest.raises(bootstrap_finalizer.BootstrapFinalizerError, match="name grammar"):
        bootstrap_finalizer._identity()


@pytest.mark.parametrize("oid", ["a" * 40, "b" * 64])
def test_zero_old_oid_matches_repository_object_width(oid):
    assert bootstrap_finalizer._zero_oid(oid) == "0" * len(oid)


TREE = "a" * 40
PERSON = b"Client Wiki Bot <client-wiki@example.com> 1 +0000"


def _raw_commit(*headers: bytes, message: bytes = bootstrap_finalizer.MESSAGE) -> bytes:
    return b"\n".join(headers) + b"\n\n" + message


@pytest.mark.parametrize("raw", [
    _raw_commit(b"tree " + TREE.encode(), b"committer " + PERSON),
    _raw_commit(b"tree " + TREE.encode(), b"author " + PERSON,
                b"author " + PERSON, b"committer " + PERSON),
    _raw_commit(b"tree " + TREE.encode(), b"author " + PERSON,
                b"committer " + PERSON, b"committer " + PERSON),
    _raw_commit(b"author " + PERSON, b"committer " + PERSON),
    _raw_commit(b"tree " + TREE.encode(), b"tree " + TREE.encode(),
                b"author " + PERSON, b"committer " + PERSON),
    _raw_commit(b"author " + PERSON, b"tree " + TREE.encode(), b"committer " + PERSON),
    _raw_commit(b"tree " + TREE.encode(), b"committer " + PERSON, b"author " + PERSON),
    _raw_commit(b"tree " + TREE.encode(), b"author " + PERSON),
    _raw_commit(b"tree " + TREE.encode(), b"author " + PERSON, b"committer Other <x@y.z> 1 +0000"),
    _raw_commit(b"tree " + TREE.encode(), b"parent " + b"b" * 40,
                b"author " + PERSON, b"committer " + PERSON),
    _raw_commit(b"tree " + TREE.encode(), b"encoding UTF-8",
                b"author " + PERSON, b"committer " + PERSON),
    _raw_commit(b"tree " + TREE.encode(), b"gpgsig forged",
                b" continuation", b"author " + PERSON, b"committer " + PERSON),
    _raw_commit(b"tree " + TREE.encode(), b"author " + PERSON, b"committer " + PERSON,
                message=b"\n" + bootstrap_finalizer.MESSAGE),
    _raw_commit(b"tree " + TREE.encode(), b"author " + PERSON, b"committer " + PERSON) + b"\0",
    _raw_commit(b"tree " + TREE.encode(), b"author " + PERSON, b"committer " + PERSON).replace(b"\n", b"\r\n", 1),
    _raw_commit(b"tree " + b"b" * 40, b"author " + PERSON, b"committer " + PERSON),
    _raw_commit(b"tree " + TREE.encode(), b"author malformed", b"committer " + PERSON),
    _raw_commit(b"tree " + TREE.encode(), b"author Client Wiki Bot <client-wiki@example.com> 1 +2400", b"committer " + PERSON),
    _raw_commit(b"tree " + TREE.encode(), b"author Client Wiki Bot <client-wiki@example.com> 1 +0060", b"committer " + PERSON),
    _raw_commit(b"tree " + TREE.encode(), b"author Client Wiki Bot <client-wiki@example.com> 9223372036854775808 +0000", b"committer " + PERSON),
])
def test_recovery_rejects_every_noncanonical_raw_commit(monkeypatch, raw):
    monkeypatch.setattr(bootstrap_finalizer, "_git", lambda *_args, **_kwargs: raw)
    monkeypatch.setattr(bootstrap_finalizer, "_independent_attestation", lambda *_args: None)
    context = type("Context", (), {"clone": object()})()
    with pytest.raises(bootstrap_finalizer.BootstrapFinalizerError):
        bootstrap_finalizer._validate_commit(
            context, "c" * 40, TREE, ("Client Wiki Bot", "client-wiki@example.com"),
        )


def test_recovery_accepts_exact_raw_root_commit(monkeypatch):
    raw = _raw_commit(
        b"tree " + TREE.encode(), b"author " + PERSON,
        b"committer Client Wiki Bot <client-wiki@example.com> 2 +0130",
    )
    monkeypatch.setattr(bootstrap_finalizer, "_git", lambda *_args, **_kwargs: raw)
    monkeypatch.setattr(bootstrap_finalizer, "_independent_attestation", lambda *_args: None)
    context = type("Context", (), {"clone": object()})()
    bootstrap_finalizer._validate_commit(
        context, "c" * 40, TREE, ("Client Wiki Bot", "client-wiki@example.com"),
    )


@pytest.mark.parametrize("surface", [
    "alternates", "http-alternates", "grafts", "shallow", "hook", "loose-replace",
    "packed-replace", "mixed-replace", "malformed-replace",
])
def test_forbidden_git_authority_surface_is_rejected(tmp_path, surface):
    clone = tmp_path / "clone"
    subprocess.run(["git", "init", "-b", "main", str(clone)], check=True, capture_output=True)
    git = clone / ".git"
    paths = {
        "alternates": git / "objects/info/alternates",
        "http-alternates": git / "objects/info/http-alternates",
        "grafts": git / "info/grafts",
        "shallow": git / "shallow",
        "hook": git / "hooks/pre-commit",
        "loose-replace": git / f"refs/replace/{'a' * 40}",
        "packed-replace": git / "packed-refs",
        "mixed-replace": git / "packed-refs",
        "malformed-replace": git / "packed-refs",
    }
    path = paths[surface]
    path.parent.mkdir(parents=True, exist_ok=True)
    data = "x\n"
    if surface == "packed-replace":
        data = f"{'b' * 40} refs/replace/{'a' * 40}\n"
    elif surface == "mixed-replace":
        (git / f"refs/replace/{'c' * 40}").parent.mkdir(parents=True, exist_ok=True)
        (git / f"refs/replace/{'c' * 40}").write_text("d" * 40 + "\n")
        data = f"{'b' * 40} refs/replace/{'a' * 40}\n"
    elif surface == "malformed-replace":
        data = f"{'b' * 40} refs/replace\n"
    path.write_text(data)
    if surface == "hook":
        path.chmod(0o755)
    with bind_clone(clone) as bound:
        with pytest.raises(bootstrap_finalizer.BootstrapFinalizerError):
            bootstrap_finalizer._reject_git_surfaces(bound)


def _initial_unit(monkeypatch, failing: str | None = None):
    calls = []
    monkeypatch.setenv("CLIENT_WIKI_GIT_AUTHOR_NAME", "Client Wiki Bot")
    monkeypatch.setenv("CLIENT_WIKI_GIT_AUTHOR_EMAIL", "client-wiki@example.com")
    tree = "a" * 40
    commit = bootstrap_finalizer._expected_commit(tree)
    monkeypatch.setattr(bootstrap_finalizer, "_remote", lambda *_args: ("absent", None))
    monkeypatch.setattr(bootstrap_finalizer, "_build_tree", lambda *_args: ("b" * 40, tree))
    monkeypatch.setattr(bootstrap_finalizer, "_independent_attestation", lambda *_args: calls.append("attest"))

    def git(_bound, *args, **_kwargs):
        calls.append(args)
        if args[0] == failing:
            raise bootstrap_finalizer.BootstrapFinalizerError("injected")
        if args[0] == "commit-tree":
            return (commit + "\n").encode()
        return b""

    monkeypatch.setattr(bootstrap_finalizer, "_git", git)
    entry = type("Entry", (), {"repo": "org/llm-wiki-client"})()
    context = type("Context", (), {"clone": object()})()
    return calls, commit, tree, entry, context


def test_cas_precedes_index_and_uses_object_width_zero(monkeypatch):
    calls, commit, tree, entry, context = _initial_unit(monkeypatch)
    bootstrap_finalizer._initial_commit(
        context, entry, object(), (), tree,
    )
    update = next(call for call in calls if isinstance(call, tuple) and call[0] == "update-ref")
    assert update == ("update-ref", "refs/heads/main", commit, "0" * 40)
    assert calls.index(update) < calls.index(("read-tree", tree))


@pytest.mark.parametrize(("failure", "kind"), [
    ("update-ref", "git_objects_cas_failed"),
    ("read-tree", "local_commit_index_incomplete"),
])
def test_object_and_index_failure_have_exact_bounded_residue(monkeypatch, failure, kind):
    calls, _commit, tree, entry, context = _initial_unit(monkeypatch, failure)
    with pytest.raises(bootstrap_finalizer.BootstrapFinalizerError) as caught:
        bootstrap_finalizer._initial_commit(
            context, entry, object(), (), tree,
        )
    assert caught.value.residue.kind == kind
    assert caught.value.residue.object_oids == ("b" * 40, tree, _commit)


def test_attestation_rechecks_forbidden_git_surfaces(monkeypatch):
    checked = []
    context = type("Context", (), {"clone": object()})()
    monkeypatch.setattr(bootstrap_finalizer, "validate_bound_context", lambda _c: None)
    monkeypatch.setattr(bootstrap_finalizer, "_reject_git_surfaces", lambda bound: checked.append(bound))
    bootstrap_finalizer._independent_attestation(context)
    assert checked == [context.clone]


def test_commit_tree_failure_preserves_constructed_objects(monkeypatch):
    _calls, _commit, tree, entry, context = _initial_unit(monkeypatch, "commit-tree")
    with pytest.raises(bootstrap_finalizer.BootstrapFinalizerError) as caught:
        bootstrap_finalizer._initial_commit(context, entry, object(), (), tree)
    assert caught.value.residue.kind == "git_objects_commit_tree_failed"
    assert caught.value.residue.tree_oid == tree
    assert caught.value.residue.object_oids == ("b" * 40, tree)


def test_transport_pushes_retained_literal_oid_and_attests_boundaries(monkeypatch):
    commit, tree = "c" * 40, "t" * 40
    states = iter((("absent", None), ("equal", commit)))
    pushed, attestations = [], []
    monkeypatch.setattr(bootstrap_finalizer, "_remote", lambda *_args: next(states))
    monkeypatch.setattr(bootstrap_finalizer, "_head", lambda *_args: commit)
    monkeypatch.setattr(bootstrap_finalizer, "_push", lambda _b, _r, oid: pushed.append(oid))
    monkeypatch.setattr(bootstrap_finalizer, "_independent_attestation", lambda *_args: attestations.append(1))
    entry = type("Entry", (), {"repo": "org/llm-wiki-client"})()
    context = type("Context", (), {"clone": object()})()
    bootstrap_finalizer._transport(
        context, entry, object(), commit, tree,
    )
    assert pushed == [commit]
    assert len(attestations) == 7


def test_head_substitution_after_transport_fails(monkeypatch):
    commit, tree = "c" * 40, "t" * 40
    heads = iter((commit, "d" * 40))
    monkeypatch.setattr(bootstrap_finalizer, "_head", lambda *_args: next(heads))
    monkeypatch.setattr(bootstrap_finalizer, "_remote", lambda *_args: ("absent", None))
    monkeypatch.setattr(bootstrap_finalizer, "_push", lambda *_args: None)
    monkeypatch.setattr(bootstrap_finalizer, "_independent_attestation", lambda *_args: None)
    entry = type("Entry", (), {"repo": "org/llm-wiki-client"})()
    context = type("Context", (), {"clone": object()})()
    with pytest.raises(bootstrap_finalizer.BootstrapFinalizerError, match="HEAD changed"):
        bootstrap_finalizer._transport(
            context, entry, object(), commit, tree,
        )


def test_each_named_operation_is_independently_attested(monkeypatch):
    events = []
    context = object()
    monkeypatch.setattr(
        bootstrap_finalizer, "_independent_attestation",
        lambda current: events.append(("attest", current)),
    )

    result = bootstrap_finalizer._with_attestation(
        context, "hash_object", lambda: events.append(("call", context)) or b"ok",
    )

    assert result == b"ok"
    assert events == [("attest", context), ("call", context), ("attest", context)]


def test_named_operation_attests_after_exception(monkeypatch):
    events = []
    monkeypatch.setattr(
        bootstrap_finalizer, "_independent_attestation", lambda _context: events.append("attest"),
    )

    with pytest.raises(RuntimeError, match="injected"):
        bootstrap_finalizer._with_attestation(
            object(), "push", lambda: (_ for _ in ()).throw(RuntimeError("injected")),
        )

    assert events == ["attest", "attest"]


def test_operation_seams_are_private_and_named():
    expected = {
        "hash_object", "mktree", "commit_tree", "cas", "read_tree",
        "push", "api_query", "final_return",
    }
    assert expected <= bootstrap_finalizer._ATTESTED_OPERATIONS
