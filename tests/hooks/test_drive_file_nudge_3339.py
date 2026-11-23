"""Tests for #3339: drive-file nudge UserPromptSubmit hook (epic #3333).

Mirrors the #801 hook harness (tests/data_sources/test_ecosystem_data_sources_801.py):
subprocess invocation of the bash hook + WORKSPACE_HUB / DRIVE_NUDGE_STATE_DIR
tmp-dir isolation, session ids derived from tmp_path so /tmp state never collides.

Run: python3 -m pytest tests/hooks/test_drive_file_nudge_3339.py -v
"""
import json
import os
import re
import shutil
import statistics
import subprocess
import time

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
IMPL = os.path.dirname(os.path.dirname(HERE))
HOOK = os.path.join(IMPL, ".claude", "hooks", "drive-file-nudge.sh")
MAP = os.path.join(IMPL, ".claude", "hooks", "drive-file-map.json")
ECO_HOOK = os.path.join(IMPL, ".claude", "hooks", "ecosystem-data-nudge.sh")
SETTINGS = os.path.join(IMPL, ".claude", "settings.json")
SKILL_MD = os.path.join(
    IMPL, ".claude", "skills", "data", "drive-file-search", "SKILL.md"
)

# Small fixture eco-map (shape matches the generated ecosystem-domain-map.json;
# repo_home/has_ace_share_precedent kept so the #801 hook can run against it in
# the dual-emission test). "pipeline" and "anchor" are real eco-map keywords —
# kept here to exercise the software-compound discount and the documented
# Tier-2 collision class.
FAKE_ECO = {
    "_note": "test fixture",
    "domains": {
        "mooring": {
            "keywords": ["mooring", "anchor", "catenary"],
            "repo_home": "digitalmodel",
            "has_ace_share_precedent": True,
        },
        "metocean": {
            "keywords": ["metocean"],
            "repo_home": "worldenergydata",
            "has_ace_share_precedent": False,
        },
        "pipeline-subsea": {
            "keywords": ["pipeline", "flowline"],
            "repo_home": "digitalmodel",
            "has_ace_share_precedent": False,
        },
    },
}

TIER1_PROMPT = "set up a fatigue analysis like we did before"  # issue acceptance prompt
TIER2_PROMPT = "pull together the mooring analysis report"


def _run_hook(prompt, session_id, ws, hook=None):
    env = dict(os.environ)
    env["WORKSPACE_HUB"] = ws
    # Isolate once-per-session state inside this test's unique tmp dir.
    env["DRIVE_NUDGE_STATE_DIR"] = ws
    env["ECOSYSTEM_NUDGE_STATE_DIR"] = ws  # for the dual-emission #801 run
    payload = json.dumps({"prompt": prompt, "session_id": session_id})
    return subprocess.run(
        ["bash", hook or HOOK],
        input=payload,
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
    )


@pytest.fixture()
def ws(tmp_path):
    """A fake workspace-hub root with hook + real map + fixture eco-map."""
    hooks = tmp_path / ".claude" / "hooks"
    hooks.mkdir(parents=True)
    shutil.copy(HOOK, hooks / "drive-file-nudge.sh")
    shutil.copy(MAP, hooks / "drive-file-map.json")
    (hooks / "ecosystem-domain-map.json").write_text(json.dumps(FAKE_ECO))
    return str(tmp_path)


def _sid(ws, suffix=""):
    # Unique per test invocation (tmp_path basename), same trick as the #801 suite.
    return "test-" + os.path.basename(str(ws).rstrip("/")) + suffix


# ── Positive firing ──────────────────────────────────────────────────────


def test_fires_on_intent_phrase(ws):
    """Tier 1: the issue's acceptance prompt fires alone."""
    p = _run_hook(TIER1_PROMPT, _sid(ws), ws)
    assert p.returncode == 0
    assert "[drive-file]" in p.stdout
    assert "drive-file-search" in p.stdout
    assert p.stdout.strip().count("\n") == 0  # exactly ONE line


def test_fires_on_domain_plus_artifact(ws):
    """Tier 2: eco-domain keyword + artifact noun co-occurrence fires."""
    p = _run_hook(TIER2_PROMPT, _sid(ws), ws)
    assert p.returncode == 0
    assert "[drive-file]" in p.stdout


# ── Negative / silent paths ──────────────────────────────────────────────


def test_silent_on_domain_only(ws):
    """Tier 2 needs BOTH halves — a bare domain mention stays silent."""
    p = _run_hook("run a mooring analysis", _sid(ws), ws)
    assert p.returncode == 0
    assert p.stdout.strip() == ""


def test_silent_on_artifact_only(ws):
    """Bare artifact nouns never fire alone (false-positive guard)."""
    p = _run_hook("write a report on the meeting", _sid(ws), ws)
    assert p.returncode == 0
    assert p.stdout.strip() == ""


def test_silent_on_irrelevant_prompt(ws):
    for i, prompt in enumerate(["what time is it", "refactor this python function please"]):
        p = _run_hook(prompt, _sid(ws, f"-s{i}"), ws)
        assert p.returncode == 0
        assert p.stdout.strip() == ""


def test_silent_on_demoted_intent_phrases(ws):
    """REQUIRED negatives (review F2): the three demonstrated false-positive
    prompts stay silent under the revised tiers (demoted intent phrases need
    domain co-occurrence; 'ci pipeline' is discounted as a software compound)."""
    prompts = [
        "do we have unit tests for this module",
        "reuse this helper function in the CI pipeline",
        "this sets a bad precedent for the API design",
    ]
    for i, prompt in enumerate(prompts):
        p = _run_hook(prompt, _sid(ws, f"-d{i}"), ws)
        assert p.returncode == 0
        assert p.stdout.strip() == "", f"false positive on: {prompt!r}"


def test_data_ask_routes_to_801_only(ws):
    """D7 carve-out: DATA-shaped asks never fire this hook — #801's DATA-level
    nudge owns them (would otherwise be Tier 2: 'do we have' + 'metocean')."""
    p = _run_hook("do we have data for metocean", _sid(ws), ws)
    assert p.returncode == 0
    assert p.stdout.strip() == ""


def test_word_boundary_no_false_fire(ws):
    """(^|[^a-z0-9])…([^a-z0-9]|$) boundaries: substrings only — 'reporting'
    is not 'report', 'precedented' is not 'precedent' (domain kw 'pipeline'
    matches but neither Tier-2 half does)."""
    p = _run_hook("the reporting pipeline is precedented", _sid(ws), ws)
    assert p.returncode == 0
    assert p.stdout.strip() == ""


# ── Coexistence with #801 (plan D7) ──────────────────────────────────────


def test_dual_emission_with_801_accepted(ws):
    """Dual emission is the ACCEPTED, asserted design: the mooring-report
    prompt fires this hook (FILE level) AND #801 (DATA level), one line each."""
    eco_hook_copy = os.path.join(ws, ".claude", "hooks", "ecosystem-data-nudge.sh")
    shutil.copy(ECO_HOOK, eco_hook_copy)
    sid = _sid(ws)
    p_drive = _run_hook(TIER2_PROMPT, sid, ws)
    p_eco = _run_hook(TIER2_PROMPT, sid, ws, hook=eco_hook_copy)
    assert "[drive-file]" in p_drive.stdout
    assert p_drive.stdout.strip().count("\n") == 0
    assert "[ecosystem-data]" in p_eco.stdout
    assert p_eco.stdout.strip().count("\n") == 0


def test_known_limitation_collision_probe(ws):
    """Documents the ACCEPTED Tier-2 collision class (review F7): eco-map
    keyword 'anchor' x artifact noun 'template' — a software prompt that DOES
    fire. Accepted: once-per-session bounds the cost at one line; tuning the
    exclusion lists is a config-only change."""
    p = _run_hook("fix the anchor tag in the template", _sid(ws), ws)
    assert p.returncode == 0
    assert "[drive-file]" in p.stdout  # expected (accepted) false positive


# ── Once-per-session state ───────────────────────────────────────────────


def test_once_per_session(ws):
    sid = _sid(ws)
    a = _run_hook(TIER1_PROMPT, sid, ws)
    assert "[drive-file]" in a.stdout
    # second prompt is itself a Tier-1 phrase — still suppressed
    b = _run_hook("search the drives for mooring examples", sid, ws)
    assert b.returncode == 0
    assert b.stdout.strip() == ""
    assert os.path.exists(os.path.join(ws, f"claude-{sid}-drivefile"))


def test_new_session_fires_again(ws):
    a = _run_hook(TIER1_PROMPT, _sid(ws, "-a"), ws)
    b = _run_hook(TIER1_PROMPT, _sid(ws, "-b"), ws)
    assert "[drive-file]" in a.stdout
    assert "[drive-file]" in b.stdout


# ── Fail-open ────────────────────────────────────────────────────────────


def test_failopen_without_map(tmp_path):
    hooks = tmp_path / ".claude" / "hooks"
    hooks.mkdir(parents=True)
    shutil.copy(HOOK, hooks / "drive-file-nudge.sh")
    (hooks / "ecosystem-domain-map.json").write_text(json.dumps(FAKE_ECO))
    # no drive-file-map.json present
    p = _run_hook(TIER1_PROMPT, "test-" + tmp_path.name, str(tmp_path))
    assert p.returncode == 0
    assert p.stdout.strip() == ""


def test_failopen_without_eco_map(tmp_path):
    """Tier 2 silently degrades to off without the eco map; Tier 1 survives."""
    hooks = tmp_path / ".claude" / "hooks"
    hooks.mkdir(parents=True)
    shutil.copy(HOOK, hooks / "drive-file-nudge.sh")
    shutil.copy(MAP, hooks / "drive-file-map.json")
    # no ecosystem-domain-map.json present
    ws_dir = str(tmp_path)
    p2 = _run_hook(TIER2_PROMPT, "test-" + tmp_path.name + "-t2", ws_dir)
    assert p2.returncode == 0
    assert p2.stdout.strip() == ""  # Tier 2 off
    p1 = _run_hook(TIER1_PROMPT, "test-" + tmp_path.name + "-t1", ws_dir)
    assert p1.returncode == 0
    assert "[drive-file]" in p1.stdout  # Tier 1 still works


def test_failopen_without_jq(ws):
    """No-jq guard (review F8): the stub PATH dir explicitly provides symlinks
    to bash, cat, grep, sed, touch, mkdir — everything the hook spawns EXCEPT
    jq (grep/sed are not coreutils, so they are linked explicitly)."""
    stub = os.path.join(ws, "stubbin")
    os.mkdir(stub)
    for tool in ("bash", "cat", "grep", "sed", "touch", "mkdir"):
        real = shutil.which(tool)
        assert real, f"host is missing {tool}"
        os.symlink(real, os.path.join(stub, tool))
    assert shutil.which("jq", path=stub) is None  # stub really has no jq
    env = dict(os.environ)
    env["WORKSPACE_HUB"] = ws
    env["DRIVE_NUDGE_STATE_DIR"] = ws
    env["PATH"] = stub
    payload = json.dumps({"prompt": TIER1_PROMPT, "session_id": _sid(ws, "-nojq")})
    p = subprocess.run(
        [os.path.join(stub, "bash"), HOOK],
        input=payload,
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert p.returncode == 0
    assert p.stdout.strip() == ""


def test_malformed_stdin(ws):
    for i, bad in enumerate(["not json", "", "{"]):
        env = dict(os.environ)
        env["WORKSPACE_HUB"] = ws
        env["DRIVE_NUDGE_STATE_DIR"] = ws
        p = subprocess.run(
            ["bash", HOOK],
            input=bad,
            env=env,
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert p.returncode == 0, f"non-zero exit on stdin {bad!r}"
        assert p.stdout.strip() == ""
    # no state file was written for any malformed invocation
    leftovers = [f for f in os.listdir(ws) if f.endswith("-drivefile")]
    assert leftovers == []


# ── Content / config ─────────────────────────────────────────────────────


def test_coverage_fallback_dated(ws):
    """The coverage line comes ONLY from the dated map fallback (review F1) and
    MUST carry the as_of date + the dde staleness softener (review F6)."""
    with open(MAP) as f:
        cov = json.load(f)["coverage_fallback"]
    p = _run_hook(TIER1_PROMPT, _sid(ws), ws)
    out = p.stdout
    assert cov["ace"] in out
    assert cov["dde"] in out
    assert cov["as_of"] in out
    assert "stale" in out  # dde staleness softener ...
    assert "#3334" in out  # ... referencing the dde refresh issue


def test_map_precomputed_consistency():
    """The authoring-time precomputed alternation strings (plan D4/F3) must
    equal the ERE-escaped joins of their source lists — pins against drift."""
    specials = set(".[\\*^$()+?{|")

    def ere_escape(s):
        return "".join("\\" + c if c in specials else c for c in s)

    with open(MAP) as f:
        m = json.load(f)
    pre = m["precomputed"]
    pairs = [
        ("tier1_intent_phrases", "tier1_re"),
        ("tier2_intent_phrases", "tier2_re"),
        ("artifact_nouns", "artifact_re"),
        ("data_ask_exclusions", "data_ask_re"),
        ("software_context_exclusions", "software_context_exclusions_re"),
    ]
    for list_key, re_key in pairs:
        expected = "|".join(ere_escape(x) for x in m[list_key])
        assert pre[re_key] == expected, f"{re_key} drifted from {list_key}"


# ── Latency budget ───────────────────────────────────────────────────────


def test_latency_budget(ws):
    """<50 ms acceptance (review F3: enforce median-of-5 AND min-of-5; budget
    overridable via DRIVE_NUDGE_LATENCY_BUDGET_MS for slow CI). A host load
    spike can distort one batch (plan Risks: wall-clock flake under load), so
    up to 3 batches of 5 are attempted; the assertion holds if ANY batch has
    both min-of-5 and median-of-5 under budget."""
    budget_s = float(os.environ.get("DRIVE_NUDGE_LATENCY_BUDGET_MS", "50")) / 1000.0
    batches = []
    for attempt in range(3):
        times = []
        for i in range(5):
            t0 = time.perf_counter()
            p = _run_hook(TIER1_PROMPT, _sid(ws, f"-lat{attempt}{i}"), ws)
            times.append(time.perf_counter() - t0)
            assert p.returncode == 0
            assert "[drive-file]" in p.stdout  # fresh sid each run: match path
        lo, med = min(times), statistics.median(times)
        batches.append((lo, med))
        if lo < budget_s and med < budget_s:
            return
    detail = "; ".join(
        f"batch{i}: min {lo * 1000:.1f} ms / median {med * 1000:.1f} ms"
        for i, (lo, med) in enumerate(batches)
    )
    raise AssertionError(
        f"no batch met the {budget_s * 1000:.0f} ms budget on min-of-5 AND "
        f"median-of-5 ({detail})"
    )


# ── Wiring + cross-artifact alignment (skip-guarded) ─────────────────────


def _wiring_present():
    try:
        with open(SETTINGS) as f:
            settings = json.load(f)
    except (OSError, ValueError):
        return False
    for entry in settings.get("hooks", {}).get("UserPromptSubmit", []):
        for h in entry.get("hooks", []):
            if "drive-file-nudge.sh" in h.get("command", ""):
                return True
    return False


@pytest.mark.skipif(
    not _wiring_present(),
    reason="settings.json wiring is owner-merged (#3330 precedent); "
    "skip until the UserPromptSubmit entry lands",
)
def test_settings_wiring():
    """Wiring test (pattern: tests/hooks/test_state_size_settings_wiring.py):
    passes on the branch that carries the owner-merged settings.json entry."""
    assert _wiring_present()


def _skill_triggers():
    """Parse the `triggers:` list from #3338's SKILL.md frontmatter (tolerant)."""
    try:
        with open(SKILL_MD) as f:
            text = f.read()
    except OSError:
        return None
    m = re.search(r"^---\s*$(.*?)^---\s*$", text, re.S | re.M)
    block = m.group(1) if m else text
    tm = re.search(r"^triggers:\s*$((?:\n\s*-\s+.*)+)", block, re.M)
    if not tm:
        return None
    return [
        re.sub(r"^\s*-\s+", "", line).strip().strip("\"'")
        for line in tm.group(1).strip("\n").splitlines()
    ]


@pytest.mark.skipif(
    not os.path.exists(SKILL_MD),
    reason="cross-artifact alignment (review F5): skip until #3338's "
    ".claude/skills/data/drive-file-search/SKILL.md lands",
)
def test_hook_skill_trigger_alignment(ws):
    """Every canonical skill trigger fires this hook's Tier-1 matcher; the
    DATA-level phrasing routes to neither (it stays with #801)."""
    triggers = _skill_triggers()
    if not triggers:
        pytest.skip("SKILL.md present but no parseable triggers: list")
    for i, trig in enumerate(triggers):
        p = _run_hook(trig, _sid(ws, f"-al{i}"), ws)
        assert "[drive-file]" in p.stdout, f"skill trigger did not fire hook: {trig!r}"
    p = _run_hook("do we have data for metocean", _sid(ws, "-al-data"), ws)
    assert p.stdout.strip() == ""
