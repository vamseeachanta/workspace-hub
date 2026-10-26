"""Narrow documentation contract; no exporters, providers, or audits are run.

Expected artifacts and ordering come from the Structure / Provider session
ecosystem audit sections of logs/orchestrator/README.md and the Canonical
operator sequence / Provider-specific notes in the portability topic. The short
rule and topic-file convention come from KNOWLEDGE.md, Session Log Ecosystem /
Topic Files. Counts, capture dates, and operational output are outside scope.
"""
from pathlib import Path
import re
import shutil

import pytest


REPO = Path(__file__).resolve().parents[2]
ORCHESTRATOR = Path("logs/orchestrator/README.md")
KNOWLEDGE = Path(".claude/memory/KNOWLEDGE.md")
TOPIC = KNOWLEDGE.parent / "topics/session-log-portability.md"
SURFACES = (ORCHESTRATOR, KNOWLEDGE, TOPIC)
# Artifact suffixes are specified by both documents' provider artifact lists.
ARTIFACTS = ("corrections/session_*.jsonl", "skill-patches.jsonl")


def _read(root, relative):
    path = root / relative
    assert path.is_file(), f"guidance file missing: {relative}"
    return path.read_text(encoding="utf-8")


def _section(text, heading):
    match = re.search(
        rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)",
        text, re.MULTILINE | re.DOTALL,
    )
    assert match, f"guidance section missing: {heading}"
    return match.group(1)


def _assert_artifacts(root):
    for relative in (ORCHESTRATOR, TOPIC):
        text = _read(root, relative).replace("session_YYYYMMDD.jsonl", "session_*.jsonl")
        for artifact in ARTIFACTS:
            assert artifact in text, f"required export artifact missing: {artifact} in {relative}"


def _assert_export_precedes_audit(root):
    guidance = _section(_read(root, ORCHESTRATOR), "Provider session ecosystem audit")
    sequence = re.search(r"sequence(?:\s+is)?\s*:\s*([^\n]+)", guidance, re.IGNORECASE)
    assert sequence, "orchestrator export/audit sequence missing"
    steps = sequence.group(1).split("→")
    _assert_step_order(steps, ORCHESTRATOR)

    workflow = _section(_read(root, TOPIC), "Canonical operator sequence")
    steps = re.findall(r"^\d+\.\s+(.+)$", workflow, re.MULTILINE)
    _assert_step_order(steps, TOPIC)


def _assert_step_order(steps, source):
    exports = [index for index, step in enumerate(steps)
               if re.search(r"\b(?:run\s+provider\s+exports|export\s+all\s+providers)\b", step, re.I)]
    audits = [index for index, step in enumerate(steps)
              if re.search(r"\brun\s+(?:the\s+)?audit\b", step, re.I)]
    assert exports and audits, f"export/audit steps missing: {source}"
    assert max(exports) < min(audits), f"export must precede audit: {source}"


def _assert_knowledge_topic(root):
    text = _read(root, KNOWLEDGE)
    rule = _section(text, "Session Log Ecosystem")
    raw_rule = next((line for line in rule.splitlines()
                     if "logs/orchestrator/<provider>/session_*.jsonl" in line), "")
    for concept in ("machine-local", "gitignored", "audit artifacts", "repo-tracked", "instead of committing raw logs"):
        assert concept in raw_rule, f"short portability rule missing concept: {concept}"
    references = _section(text, "Topic Files")
    # KNOWLEDGE uses code-span filenames, relative to its sibling topics folder.
    reference = re.search(r"`([^`]*session-log-portability\.md)`", references)
    assert reference, "portability topic reference missing"
    target = KNOWLEDGE.parent / "topics" / reference.group(1)
    assert (root / target).resolve() == (root / TOPIC).resolve(), "portability topic reference has wrong target"
    assert (root / target).is_file(), "portability topic link is broken"
    assert "# Session Log Portability" in _read(root, target), "portability topic heading missing"


def test_export_precedes_audit():
    _assert_export_precedes_audit(REPO)


def test_required_export_artifacts_documented():
    _assert_artifacts(REPO)


def test_knowledge_links_portability_topic():
    _assert_knowledge_topic(REPO)


@pytest.fixture
def guidance_copy(tmp_path):
    for relative in SURFACES:
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / relative, destination)
    return tmp_path


@pytest.mark.parametrize("relative", (ORCHESTRATOR, TOPIC))
@pytest.mark.parametrize("artifact", ARTIFACTS)
def test_missing_artifact_control(guidance_copy, relative, artifact):
    _assert_artifacts(guidance_copy)
    path = guidance_copy / relative
    path.write_text(path.read_text(encoding="utf-8").replace("session_YYYYMMDD.jsonl", "session_*.jsonl").replace(artifact, "removed-artifact"), encoding="utf-8")
    with pytest.raises(AssertionError, match="required export artifact missing: " + re.escape(artifact)):
        _assert_artifacts(guidance_copy)


@pytest.mark.parametrize("relative", (ORCHESTRATOR, TOPIC))
def test_inverted_order_control(guidance_copy, relative):
    _assert_export_precedes_audit(guidance_copy)
    path = guidance_copy / relative
    text = path.read_text(encoding="utf-8")
    if relative == ORCHESTRATOR:
        text = text.replace("export all providers → run audit", "run audit → export all providers")
    else:
        text = text.replace("Run provider exports first", "Run the audit first")
        text = text.replace("Then run the audit", "Then run provider exports")
    path.write_text(text, encoding="utf-8")
    with pytest.raises(AssertionError, match="export must precede audit: " + re.escape(str(relative))):
        _assert_export_precedes_audit(guidance_copy)


def test_broken_topic_link_control(guidance_copy):
    _assert_knowledge_topic(guidance_copy)
    path = guidance_copy / KNOWLEDGE
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("`session-log-portability.md`", "`missing/session-log-portability.md`"), encoding="utf-8")
    with pytest.raises(AssertionError, match="portability topic reference has wrong target"):
        _assert_knowledge_topic(guidance_copy)


def test_missing_topic_control(guidance_copy):
    _assert_knowledge_topic(guidance_copy)
    # Move only the disposable fixture; the repository guidance stays untouched.
    path = guidance_copy / TOPIC
    path.rename(path.with_suffix(".unavailable"))
    with pytest.raises(AssertionError, match="portability topic link is broken"):
        _assert_knowledge_topic(guidance_copy)
