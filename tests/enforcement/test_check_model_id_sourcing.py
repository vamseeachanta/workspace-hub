"""Tests for the model-ID sourcing ratchet guard (#3060, epic #3058)."""
import os
import subprocess

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCRIPT = os.path.join(REPO, "scripts", "enforcement", "check-model-id-sourcing.sh")


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


def test_registry_reference_exempts(tmp_path):
    f = write(tmp_path, "x.py", 'm = registry_model("claude_primary", "claude-opus-4-9")\n')
    rc, _ = run("--enforce", "--baseline", empty_baseline(tmp_path), f)
    assert rc == 0


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
