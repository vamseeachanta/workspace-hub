"""Tests for the model-ID sourcing ratchet guard (#3060, epic #3058)."""
import os
import re
import subprocess

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCRIPT = os.path.join(REPO, "scripts", "enforcement", "check-model-id-sourcing.sh")
WORKFLOW = os.path.join(REPO, ".github", "workflows", "enforcement-gate.yml")
PRECOMMIT = os.path.join(REPO, ".pre-commit-config.yaml")


def run(*args):
    p = subprocess.run(["bash", SCRIPT, *args], capture_output=True, text=True, cwd=REPO)
    return p.returncode, p.stdout + p.stderr


def write(tmp_path, name, content):
    f = tmp_path / name
    f.write_text(content)
    return str(f)


def empty_baseline(tmp_path):
    b = tmp_path / "baseline.txt"
    b.write_text("# empty\n")
    return str(b)


def test_new_literal_flagged_in_enforce_mode(tmp_path):
    f = write(tmp_path, "x.py", 'MODEL = "claude-opus-4-9"\n')
    rc, out = run("--enforce", "--baseline", empty_baseline(tmp_path), f)
    assert rc == 1
    assert "claude-opus-4-9" in out


def test_advisory_mode_never_fails(tmp_path):
    f = write(tmp_path, "x.py", 'MODEL = "claude-opus-4-9"\n')
    rc, out = run("--baseline", empty_baseline(tmp_path), f)  # advisory default
    assert rc == 0
    assert "claude-opus-4-9" in out  # still reported


def test_allow_token_sentinel_exempts(tmp_path):
    f = write(tmp_path, "x.py", 'MODEL = "claude-opus-4-9"  # model-id-ok\n')
    rc, out = run("--enforce", "--baseline", empty_baseline(tmp_path), f)
    assert rc == 0


def test_model_id_ok_does_not_exempt_neighbor_literal(tmp_path):
    f = write(tmp_path, "x.py", 'ALLOWED = "claude-opus-4-9"; BAD = "gpt-5.5"  # model-id-ok\n')
    rc, out = run("--enforce", "--baseline", empty_baseline(tmp_path), f)
    assert rc == 1
    assert "gpt-5.5" in out


def test_registry_reference_exempts(tmp_path):
    f = write(tmp_path, "x.py", 'm = registry_model("claude_primary", "claude-opus-4-9")\n')
    rc, _ = run("--enforce", "--baseline", empty_baseline(tmp_path), f)
    assert rc == 0


def test_latest_models_reference_does_not_exempt_code_literal(tmp_path):
    f = write(tmp_path, "x.py", 'MODEL = "gpt-5.5"  # latest_models someday\n')
    rc, out = run("--enforce", "--baseline", empty_baseline(tmp_path), f)
    assert rc == 1
    assert "gpt-5.5" in out


def test_registry_reference_does_not_exempt_neighbor_literal(tmp_path):
    f = write(tmp_path, "x.py", 'm = registry_model("claude_primary", "claude-opus-4-9"); BAD = "gpt-5.5"\n')
    rc, out = run("--enforce", "--baseline", empty_baseline(tmp_path), f)
    assert rc == 1
    assert "gpt-5.5" in out


def test_self_and_registry_exclusions_require_exact_paths(tmp_path):
    baseline_like = tmp_path / "scripts" / "enforcement" / "model-id-baseline.txt.py"
    registry_like = tmp_path / "config" / "agents" / "model-registry.yaml.extra.py"
    baseline_like.parent.mkdir(parents=True)
    registry_like.parent.mkdir(parents=True)
    baseline_like.write_text('MODEL = "gpt-5.5"\n')
    registry_like.write_text('MODEL = "claude-opus-4-9"\n')
    files = [str(baseline_like), str(registry_like)]

    rc, out = run("--enforce", "--baseline", empty_baseline(tmp_path), *files)

    assert rc == 1
    assert "model-id-baseline.txt.py" in out
    assert "model-registry.yaml.extra.py" in out
    assert "gpt-5.5" in out
    assert "claude-opus-4-9" in out


def test_baselined_pair_not_flagged(tmp_path):
    f = write(tmp_path, "x.py", 'MODEL = "claude-opus-4-9"\n')
    b = tmp_path / "baseline.txt"
    rc, out = run("--update-baseline", "--baseline", str(b), f)
    assert rc == 0, out
    rc, out = run("--enforce", "--baseline", str(b), f)
    assert rc == 0
    assert "0 NOT in baseline" in out


def test_new_same_file_occurrence_is_flagged(tmp_path):
    f = write(tmp_path, "x.py", 'MODEL = "claude-opus-4-9"\n')
    b = tmp_path / "baseline.txt"
    rc, out = run("--update-baseline", "--baseline", str(b), f)
    assert rc == 0, out
    with open(f, "a", encoding="utf-8") as handle:
        handle.write('FALLBACK = "claude-opus-4-9"\n')

    rc, out = run("--enforce", "--baseline", str(b), f)

    assert rc == 1
    assert "claude-opus-4-9" in out


def test_tier_alias_not_matched(tmp_path):
    # aliases / tier names must NOT trip the guard
    f = write(tmp_path, "x.py", 'model = "opus"\nprimary = "claude_primary"\n')
    rc, out = run("--enforce", "--baseline", empty_baseline(tmp_path), f)
    assert rc == 0
    assert "0 in-scope literal" in out


def test_provider_ids_matched(tmp_path):
    f = write(tmp_path, "x.sh", 'gemini --model gemini-2.5-pro\n')
    rc, out = run("--enforce", "--baseline", empty_baseline(tmp_path), f)
    assert rc == 1
    assert "gemini-2.5-pro" in out


def test_legacy_and_codex_model_ids_matched(tmp_path):
    f = write(
        tmp_path,
        "x.sh",
        "\n".join(
            [
                'claude --model claude-3-5-sonnet-20241022',
                'claude --model claude-3-haiku-20240307',
                'openai --model o4-mini',
                'codex --model codex-mini',
            ]
        ),
    )
    rc, out = run("--enforce", "--baseline", empty_baseline(tmp_path), f)
    assert rc == 1
    assert "claude-3-5-sonnet-20241022" in out
    assert "claude-3-haiku-20240307" in out
    assert "o4-mini" in out
    assert "codex-mini" in out


def test_model_registry_todo_does_not_exempt_literal(tmp_path):
    f = write(tmp_path, "x.py", 'MODEL = "claude-opus-4-9"  # TODO: move to model-registry someday\n')
    rc, out = run("--enforce", "--baseline", empty_baseline(tmp_path), f)
    assert rc == 1
    assert "claude-opus-4-9" in out


def test_default_scope_includes_skill_markdown(tmp_path):
    repo = tmp_path / "repo"
    skill = repo / ".claude" / "skills" / "demo" / "SKILL.md"
    agent = repo / ".claude" / "agent-library" / "demo.md"
    skill.parent.mkdir(parents=True)
    agent.parent.mkdir(parents=True)
    skill.write_text('Use "claude-opus-4-9" here.\n')
    agent.write_text('Use "gpt-5.5" here.\n')
    baseline = repo / "baseline.txt"

    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
    p = subprocess.run(
        ["bash", SCRIPT, "--enforce", "--baseline", str(baseline)],
        capture_output=True,
        text=True,
        cwd=repo,
    )

    assert p.returncode == 1
    assert ".claude/skills/demo/SKILL.md" in p.stdout + p.stderr
    assert "claude-opus-4-9" in p.stdout + p.stderr
    assert ".claude/agent-library/demo.md" in p.stdout + p.stderr
    assert "gpt-5.5" in p.stdout + p.stderr


def test_default_scope_includes_github_workflows(tmp_path):
    repo = tmp_path / "repo"
    workflow = repo / ".github" / "workflows" / "demo.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text('run: echo "gpt-5.5"\n')
    baseline = repo / "baseline.txt"

    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
    p = subprocess.run(
        ["bash", SCRIPT, "--enforce", "--baseline", str(baseline)],
        capture_output=True,
        text=True,
        cwd=repo,
    )

    assert p.returncode == 1
    assert ".github/workflows/demo.yml" in p.stdout + p.stderr
    assert "gpt-5.5" in p.stdout + p.stderr


def test_default_scope_enforce_flags_stale_baseline_entries(tmp_path):
    repo = tmp_path / "repo"
    cfg = repo / "config" / "demo.yaml"
    cfg.parent.mkdir(parents=True)
    cfg.write_text('model: "gpt-5.5"\n')
    baseline = repo / "baseline.txt"

    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "config/demo.yaml"], cwd=repo, check=True, capture_output=True, text=True)
    p = subprocess.run(
        ["bash", SCRIPT, "--update-baseline", "--baseline", str(baseline)],
        capture_output=True,
        text=True,
        cwd=repo,
    )
    assert p.returncode == 0, p.stdout + p.stderr
    with open(baseline, "a", encoding="utf-8") as handle:
        handle.write("config/missing.yaml\tgpt-5.5\t123:7\t1\n")

    p = subprocess.run(
        ["bash", SCRIPT, "--enforce", "--baseline", str(baseline)],
        capture_output=True,
        text=True,
        cwd=repo,
    )

    assert p.returncode == 1
    assert "STALE" in p.stdout + p.stderr
    assert "config/missing.yaml" in p.stdout + p.stderr


def test_review_results_are_out_of_model_sourcing_scope(tmp_path):
    repo = tmp_path / "repo"
    result = repo / "scripts" / "review" / "results" / "provider-review.md"
    result.parent.mkdir(parents=True)
    result.write_text('Historical review transcript mentions "gpt-5.5".\n')
    baseline = repo / "baseline.txt"

    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
    p = subprocess.run(
        ["bash", SCRIPT, "--enforce", "--baseline", str(baseline)],
        capture_output=True,
        text=True,
        cwd=repo,
    )

    assert p.returncode == 0
    assert "0 in-scope literal" in p.stdout + p.stderr


def test_workflow_preserves_model_guard_pipeline_exit_status():
    with open(WORKFLOW, encoding="utf-8") as handle:
        workflow = handle.read()

    start = workflow.index("  model-id-sourcing:")
    end = workflow.index("  compliance-dashboard:", start)
    section = workflow[start:end]

    assert "set -o pipefail" in section or "PIPESTATUS[0]" in section


def test_precommit_registry_exclusion_is_exact():
    with open(PRECOMMIT, encoding="utf-8") as handle:
        config = handle.read()

    hook = re.search(r"id: check-model-id-sourcing.*?exclude: '([^']+)'", config, re.S)
    assert hook is not None
    exclude = re.compile(hook.group(1))

    assert exclude.search("config/agents/model-registry.yaml")
    assert not exclude.search("config/agents/model-registry.yaml.extra.py")
    assert exclude.search("scripts/review/results/provider-review.md")
