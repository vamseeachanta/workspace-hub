#!/usr/bin/env bash
# analyze-conversations.sh - Extract patterns from full Claude conversation logs
# Part of RAGS loop: Enhanced ABSTRACT phase with conversation analysis
#
# Input: Claude Code conversation logs from ~/.claude/projects/
# Output: JSON patterns for skill enhancement and learning
#
# Analyzes:
# - User prompt patterns (common questions, requests)
# - Correction patterns ("no, I meant...", "actually...")
# - Confusion indicators (repeated questions, clarifications)
# - Topic frequency and skill gaps
# - Response quality indicators

set -uo pipefail

# Auto-detect workspace root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
# Path: .claude/skills/coordination/workspace/claude-reflect/scripts - go up 6 levels
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(dirname "$(dirname "$(dirname "$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")")")")}"
# Fallback detection
if [[ ! -d "${WORKSPACE_ROOT}/.claude" ]]; then
    [[ -d "/mnt/github/workspace-hub" ]] && WORKSPACE_ROOT="/mnt/github/workspace-hub"
    [[ -d "/d/workspace-hub" ]] && WORKSPACE_ROOT="/d/workspace-hub"
fi

STATE_DIR="${WORKSPACE_STATE_DIR:-${WORKSPACE_ROOT}/.claude/state}"
OUTPUT_DIR="${STATE_DIR}/patterns"
DAYS=${1:-7}

# Claude projects directory
CLAUDE_PROJECTS_DIR="${HOME}/.claude/projects"

mkdir -p "$OUTPUT_DIR"

# Get project directory name for this workspace
PROJECT_DIR_NAME=$(echo "$WORKSPACE_ROOT" | sed 's|/|-|g' | sed 's|^-||')

# Find conversation log files from last N days
find_conversation_logs() {
    local project_path="$CLAUDE_PROJECTS_DIR/$PROJECT_DIR_NAME"

    if [[ ! -d "$project_path" ]]; then
        # Try alternate naming conventions
        project_path="$CLAUDE_PROJECTS_DIR/-mnt-github-workspace-hub"
        [[ ! -d "$project_path" ]] && project_path="$CLAUDE_PROJECTS_DIR/-d-workspace-hub"
    fi

    if [[ -d "$project_path" ]]; then
        find "$project_path" -name "*.jsonl" -mtime -"$DAYS" -type f 2>/dev/null | sort
    fi
}

LOG_FILES=$(find_conversation_logs)

if [[ -z "$LOG_FILES" ]]; then
    echo '{"conversations_analyzed": 0, "error": "No conversation logs found", "search_path": "'"$CLAUDE_PROJECTS_DIR"'"}'
    exit 0
fi

# Create temp file for combined logs
TEMP_FILE=$(mktemp)
trap "rm -f $TEMP_FILE" EXIT

# Combine all conversation logs
for f in $LOG_FILES; do
    cat "$f" >> "$TEMP_FILE"
done

if [[ ! -s "$TEMP_FILE" ]]; then
    echo '{"conversations_analyzed": 0, "error": "Empty conversation logs"}'
    exit 0
fi

# Create Python script in temp file
PYTHON_SCRIPT=$(mktemp)
trap "rm -f $TEMP_FILE $PYTHON_SCRIPT" EXIT

cat > "$PYTHON_SCRIPT" << 'PYTHON_EOF'
import sys
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta

temp_file = sys.argv[1]
days = int(sys.argv[2])

# Patterns to detect
CORRECTION_PATTERNS = [
    r'\b(no,?\s*(i|actually|that\'s not|wrong))',
    r'\b(actually,?\s*(i meant|i want|let me))',
    r'\b(wait,?\s*(no|that\'s))',
    r'\b(sorry,?\s*(i meant|that should))',
    r'\b(not\s+that|wrong\s+(file|one|thing))',
    r'\b(i\s+meant\s+to)',
    r'\b(oops|typo)',
]

QUESTION_PATTERNS = [
    r'\b(how\s+(do|can|to|should)\s+i)',
    r'\b(what\s+(is|are|does|should))',
    r'\b(why\s+(is|does|do|did))',
    r'\b(can\s+you\s+(help|show|explain))',
    r'\b(where\s+(is|are|do|can))',
    r'\b(is\s+there\s+a\s+way)',
]

CONFUSION_INDICATORS = [
    r'\b(i\s+don\'t\s+understand)',
    r'\b(what\s+do\s+you\s+mean)',
    r'\b(can\s+you\s+explain)',
    r'\b(i\'m\s+confused)',
    r'\b(that\s+doesn\'t\s+(work|make sense))',
    r'\b(still\s+not\s+working)',
]

SKILL_REQUEST_PATTERNS = [
    r'\/(\w+[-\w]*)',  # Slash commands
    r'\b(run|use|invoke)\s+(\w+)\s+skill',
    r'\b(is\s+there\s+a\s+skill\s+for)',
]

# Results containers
results = {
    "extraction_date": datetime.utcnow().isoformat() + "Z",
    "days_analyzed": days,
    "conversations_analyzed": 0,
    "total_user_messages": 0,
    "total_assistant_messages": 0,
    "user_prompt_patterns": [],
    "correction_events": [],
    "confusion_indicators": [],
    "skill_requests": [],
    "topic_frequency": {},
    "common_questions": [],
    "thinking_patterns": [],
    "response_lengths": {"short": 0, "medium": 0, "long": 0},
    "session_stats": {},
    "skill_gaps": [],
    "insights": []
}

sessions = defaultdict(list)
user_prompts = []
corrections = []
confusions = []
skill_requests = []
questions = []
thinking_samples = []
topics = Counter()

# Parse conversation logs
with open(temp_file, 'r') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        msg_type = entry.get('type', '')
        session_id = entry.get('sessionId', 'unknown')

        # Track sessions
        sessions[session_id].append(entry)

        # Analyze user messages
        if msg_type == 'user':
            message = entry.get('message', {})
            content = message.get('content', '')

            # Handle content that's a list (tool results, etc.)
            if isinstance(content, list):
                content = ' '.join([
                    c.get('text', '') if isinstance(c, dict) else str(c)
                    for c in content
                ])

            if not content or len(content) < 3:
                continue

            results["total_user_messages"] += 1
            user_prompts.append({
                "content": content[:500],  # Truncate for storage
                "session": session_id,
                "timestamp": entry.get('timestamp', '')
            })

            # Check for corrections
            content_lower = content.lower()
            for pattern in CORRECTION_PATTERNS:
                if re.search(pattern, content_lower):
                    corrections.append({
                        "content": content[:200],
                        "session": session_id,
                        "pattern": pattern
                    })
                    break

            # Check for confusion
            for pattern in CONFUSION_INDICATORS:
                if re.search(pattern, content_lower):
                    confusions.append({
                        "content": content[:200],
                        "session": session_id
                    })
                    break

            # Check for questions
            for pattern in QUESTION_PATTERNS:
                if re.search(pattern, content_lower):
                    questions.append(content[:200])
                    break

            # Check for skill requests
            for pattern in SKILL_REQUEST_PATTERNS:
                matches = re.findall(pattern, content_lower)
                if matches:
                    skill_requests.extend(matches if isinstance(matches[0], str) else [m[0] for m in matches])

            # Extract topics (simple keyword extraction)
            words = re.findall(r'\b[a-z]{4,}\b', content_lower)
            # Filter common words
            stopwords = {'that', 'this', 'with', 'from', 'have', 'been', 'were', 'they',
                        'their', 'what', 'when', 'where', 'which', 'would', 'could',
                        'should', 'there', 'about', 'into', 'some', 'them', 'then',
                        'these', 'your', 'make', 'like', 'just', 'know', 'take'}
            for word in words:
                if word not in stopwords:
                    topics[word] += 1

        # Analyze assistant messages
        elif msg_type == 'assistant':
            results["total_assistant_messages"] += 1
            message = entry.get('message', {})
            content_list = message.get('content', [])

            if isinstance(content_list, list):
                for item in content_list:
                    if isinstance(item, dict):
                        # Extract thinking
                        if item.get('type') == 'thinking':
                            thinking = item.get('thinking', '')
                            if thinking and len(thinking) > 100:
                                thinking_samples.append(thinking[:500])

                        # Measure response length
                        if item.get('type') == 'text':
                            text = item.get('text', '')
                            text_len = len(text)
                            if text_len < 200:
                                results["response_lengths"]["short"] += 1
                            elif text_len < 1000:
                                results["response_lengths"]["medium"] += 1
                            else:
                                results["response_lengths"]["long"] += 1

# Compile results
results["conversations_analyzed"] = len(sessions)

# Top corrections
results["correction_events"] = corrections[:20]
results["correction_count"] = len(corrections)

# Confusion indicators
results["confusion_indicators"] = confusions[:20]
results["confusion_count"] = len(confusions)

# Skill requests
skill_counter = Counter(skill_requests)
results["skill_requests"] = [{"skill": k, "count": v} for k, v in skill_counter.most_common(20)]

# Topic frequency
results["topic_frequency"] = dict(topics.most_common(30))

# Common questions
question_counter = Counter(questions)
results["common_questions"] = [{"question": k, "count": v} for k, v in question_counter.most_common(15)]

# Thinking pattern samples (for learning)
results["thinking_patterns"] = thinking_samples[:10]

# Session stats
session_lengths = [len(msgs) for msgs in sessions.values()]
if session_lengths:
    results["session_stats"] = {
        "total_sessions": len(sessions),
        "avg_messages_per_session": sum(session_lengths) / len(session_lengths),
        "max_session_length": max(session_lengths),
        "min_session_length": min(session_lengths)
    }

# Identify skill gaps (topics with high frequency but no skill matches)
high_freq_topics = [t for t, c in topics.most_common(20) if c >= 3]
results["skill_gaps"] = high_freq_topics[:10]

# Generate insights
if results["correction_count"] > 5:
    results["insights"].append(f"High correction rate ({results['correction_count']} corrections) - consider improving initial understanding")

if results["confusion_count"] > 3:
    results["insights"].append(f"Multiple confusion indicators ({results['confusion_count']}) - review clarity of responses")

if results["response_lengths"]["long"] > results["response_lengths"]["short"] * 2:
    results["insights"].append("Responses tend to be long - consider more concise answers")

if skill_requests:
    top_skill = skill_counter.most_common(1)[0] if skill_counter else None
    if top_skill and top_skill[1] >= 3:
        results["insights"].append(f"Frequent skill request: '{top_skill[0]}' ({top_skill[1]} times)")

# User prompt patterns (common prefixes/intents)
prompt_starts = Counter()
for p in user_prompts:
    content = p["content"].lower().strip()
    # Get first 3-4 words as pattern
    words = content.split()[:4]
    if len(words) >= 2:
        prompt_starts[' '.join(words)] += 1

results["user_prompt_patterns"] = [
    {"pattern": k, "count": v}
    for k, v in prompt_starts.most_common(15)
    if v >= 2
]

print(json.dumps(results, indent=2))
PYTHON_EOF

# Execute Python script
python3 "$PYTHON_SCRIPT" "$TEMP_FILE" "$DAYS"
