#!/usr/bin/env python3
"""
Post-session skill extractor — Hermes-inspired self-improvement for Claude Code.

Fires on the Stop hook. Reads the session transcript, calls Haiku to decide
if a reusable skill was discovered, and writes SKILL.md to .claude/skills/
if one is found. Outputs a systemMessage so the user sees the result inline.

Called by: ~/.claude/settings.json Stop hook
Python: ~/.hermes/hermes-agent/.venv/bin/python (has anthropic + dotenv installed)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path("/mnt/local-analysis/workspace-hub")
PROJECTS_DIR = Path.home() / ".claude" / "projects" / "-mnt-local-analysis-workspace-hub"
SKILLS_LEARNED_DIR = REPO_ROOT / ".claude" / "skills" / "workspace-hub" / "learned"
HERMES_ENV = Path.home() / ".hermes" / ".env"
OPENROUTER_BASE = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "anthropic/claude-haiku-4-5"
MAX_CONVERSATION_CHARS = 8000


def load_hermes_env():
    if not HERMES_ENV.exists():
        return
    try:
        from dotenv import dotenv_values
        for k, v in dotenv_values(HERMES_ENV).items():
            if v:
                os.environ.setdefault(k, v)
        return
    except ImportError:
        pass
    # Fallback: manual parse
    for line in HERMES_ENV.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        v = v.strip().strip('"').strip("'")
        if v:
            os.environ.setdefault(k.strip(), v)


def read_transcript(session_id: str) -> list[dict]:
    transcript_path = PROJECTS_DIR / f"{session_id}.jsonl"
    if not transcript_path.exists():
        # Fallback: most recently modified transcript
        candidates = sorted(PROJECTS_DIR.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not candidates:
            return []
        transcript_path = candidates[0]

    entries = []
    for line in transcript_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return entries


def extract_conversation(entries: list[dict]) -> str:
    turns = []
    for entry in entries:
        etype = entry.get("type")
        if etype not in ("user", "assistant"):
            continue

        msg = entry.get("message", {})
        if not isinstance(msg, dict):
            continue

        role = msg.get("role", etype)
        content = msg.get("content", "")

        if isinstance(content, list):
            text_parts = [
                block.get("text", "")
                for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            ]
            content = " ".join(text_parts)

        content = str(content).strip()
        if not content or content.startswith("<command-message>"):
            continue

        label = "USER" if role == "user" else "ASSISTANT"
        turns.append(f"{label}: {content[:600]}")

    conversation = "\n\n".join(turns[-30:])  # Last 30 turns
    return conversation[:MAX_CONVERSATION_CHARS]


def analyze_for_skill(conversation: str) -> dict | None:
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return None

    try:
        from openai import OpenAI
    except ImportError:
        return None

    client = OpenAI(base_url=OPENROUTER_BASE, api_key=api_key)

    prompt = f"""You are analyzing a Claude Code session to find reusable skills worth saving.

Session transcript:
---
{conversation}
---

A skill is worth capturing ONLY if the session demonstrates:
1. A non-obvious workflow or process applicable to future sessions
2. A debugging pattern, architectural decision, or tool-usage sequence worth repeating
3. A project-specific procedure that isn't obvious from the code

Do NOT create a skill for:
- Simple Q&A, one-off tasks, or standard git/coding operations
- Sessions with no meaningful problem-solving (< 5 substantive exchanges)
- Topics already well-covered by existing documentation

If a skill IS worth capturing, respond with EXACTLY this JSON (no markdown, no explanation).
Keep "content" to 3-5 sentences max — it is a trigger/reminder, not a tutorial:
{{"create_skill": true, "name": "kebab-case-skill-name", "description": "One-line description for skill index", "tags": ["tag1", "tag2"], "content": "# Skill Title\\n\\nBrief 3-5 sentence description of when to use this and the key steps/commands."}}

If NO skill is worth capturing, respond with EXACTLY:
{{"create_skill": false}}

JSON only, no other text:"""

    try:
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        result_text = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
            result_text = result_text.strip()
        return json.loads(result_text)
    except Exception:
        return None


def write_skill(result: dict) -> Path:
    name = result.get("name", "learned-skill").lower().replace(" ", "-")
    description = result.get("description", "Auto-extracted skill")
    tags = result.get("tags", [])
    content = result.get("content", "")
    today = datetime.now().strftime("%Y-%m-%d")

    skill_dir = SKILLS_LEARNED_DIR / name
    skill_dir.mkdir(parents=True, exist_ok=True)

    if not content.startswith("---"):
        tags_yaml = ", ".join(f'"{t}"' for t in tags)
        frontmatter = f"""---
name: {name}
description: {description}
version: 1.0.0
source: auto-extracted
extracted: {today}
metadata:
  tags: [{tags_yaml}]
---

"""
        content = frontmatter + content

    skill_path = skill_dir / "SKILL.md"
    skill_path.write_text(content)
    return skill_path


def main():
    load_hermes_env()

    try:
        hook_input = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        hook_input = {}

    session_id = hook_input.get("session_id", "")

    entries = read_transcript(session_id)
    if not entries:
        return

    conversation = extract_conversation(entries)
    if len(conversation) < 200:
        return  # Too short to be worth analyzing

    result = analyze_for_skill(conversation)
    if not result or not result.get("create_skill"):
        return

    skill_path = write_skill(result)
    rel_path = skill_path.relative_to(REPO_ROOT)

    output = {
        "systemMessage": f"[skill-extractor] Learned: {rel_path} — \"{result.get('description', '')}\""
    }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
