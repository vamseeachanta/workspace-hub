"""Exact CLI JSON contract for finalization success and residue failure."""
import json

from client_llm_wiki import bootstrap_contract, bootstrap_finalizer


SUCCESS = {
    "commit_oid": "c" * 40, "remote": "equal", "repo": "org/llm-wiki-client",
    "short_name": "client", "status": "finalized", "tree_oid": "t" * 40,
}


def test_finalize_cli_emits_exact_compact_sorted_success_json(monkeypatch, capsys):
    monkeypatch.setattr(bootstrap_contract, "finalize_scaffold", lambda *_args: SUCCESS)
    rc = bootstrap_contract.main([
        "finalize-scaffold", "--registry", "registry.yml", "--short-name", "client",
        "--manifest", "render.json",
    ])
    assert rc == 0
    assert capsys.readouterr().out == json.dumps(
        SUCCESS, sort_keys=True, separators=(",", ":"),
    ) + "\n"


def test_finalize_cli_emits_exact_error_and_residue_json(monkeypatch, capsys):
    residue = bootstrap_finalizer.FinalizeResidue(
        "remote_unknown", "c" * 40, "t" * 40, ("c" * 40, "t" * 40),
    )

    def fail(*_args):
        raise bootstrap_finalizer.BootstrapFinalizerError("secret detail", residue=residue)

    monkeypatch.setattr(bootstrap_contract, "finalize_scaffold", fail)
    rc = bootstrap_contract.main([
        "finalize-scaffold", "--registry", "registry.yml", "--short-name", "client",
        "--manifest", "render.json",
    ])
    assert rc == 1
    assert capsys.readouterr().err == json.dumps({
        "error": "finalize_failed",
        "residue": {
            "commit_oid": "c" * 40,
            "instruction": "preserve clone; inspect and retry only through finalize-scaffold",
            "kind": "remote_unknown", "object_oids": ["c" * 40, "t" * 40],
            "tree_oid": "t" * 40,
        },
    }, sort_keys=True) + "\n"
