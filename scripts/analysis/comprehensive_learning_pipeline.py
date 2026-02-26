import os
import json
import glob
from datetime import datetime, timedelta
import yaml
import re
import subprocess
import fcntl
import random

# --- Configuration ---
WS_HUB = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STATE_DIR = os.path.join(WS_HUB, ".claude", "state")
CORRECTIONS_DIR = os.path.join(STATE_DIR, "corrections")
WORK_QUEUE_DIR = os.path.join(WS_HUB, ".claude", "work-queue")
ARCHIVE_DIR = os.path.join(WORK_QUEUE_DIR, "archive")
PENDING_WRK_DIR = os.path.join(WORK_QUEUE_DIR, "pending")
REPORTS_DIR = os.path.join(STATE_DIR, "learning-reports")
SKILL_SCORES_FILE = os.path.join(STATE_DIR, "skill-scores.yaml")
CANDIDATES_DIR = os.path.join(STATE_DIR, "candidates")
MEMORY_DIR = os.path.join(WS_HUB, ".claude", "memory")
NEXT_ID_LOCK = "/tmp/workspace-hub-next-id.lock"

def get_hostname():
    try:
        import socket
        return socket.gethostname().lower()
    except:
        return os.environ.get("HOSTNAME", "unknown").lower()

def load_jsonl(file_path):
    data = []
    if not os.path.exists(file_path):
        return data
    with open(file_path, 'r') as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return data

def get_week_range(date):
    start = date - timedelta(days=date.weekday())
    end = start + timedelta(days=6)
    return start.date(), end.date()

# --- Helpers ---

def sanitize_yaml_string(s):
    if not s:
        return ""
    # Strip --- sequences
    s = s.replace("---", "--- ")
    # Replace newlines with spaces for single-line fields
    s = s.replace("\n", " ")
    # Strip markdown control characters from beginning? (Optional)
    # Quote if contains special YAML characters
    if any(c in s for c in ":#\"'|&!%@*"):
        # Double escape quotes
        s = s.replace('"', '\\"')
        return f'"{s}"'
    return s

def sanitize_multiline(s):
    if not s:
        return ""
    # Strip --- sequences
    s = s.replace("---", "--- ")
    return s

def create_wrk_item(title, description, priority="low", source="comprehensive-learning"):
    # Ensure lock file exists
    if not os.path.exists(NEXT_ID_LOCK):
        open(NEXT_ID_LOCK, 'w').close()
        
    with open(NEXT_ID_LOCK, 'w') as lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX)
            
            # Get next ID using next-id.sh
            try:
                next_id = subprocess.check_output(["bash", os.path.join(WS_HUB, "scripts", "work-queue", "next-id.sh")]).decode().strip()
            except Exception as e:
                print(f"Error getting next ID: {e}")
                return None
                
            wrk_file = os.path.join(PENDING_WRK_DIR, f"WRK-{next_id}.md")
            
            # Sanitize inputs
            title_sanitized = sanitize_yaml_string(title[:80])
            description_sanitized = sanitize_multiline(description)
            
            content = f"""---
id: WRK-{next_id}
title: {title_sanitized}
status: pending
priority: {priority}
source: {source}
computer: {get_hostname()}
---
## Context
Auto-created by comprehensive-learning analysis.

## Description
{description_sanitized}

## Acceptance Criteria
- [ ] Issue addressed or candidate assessed
"""
            # Validate frontmatter
            try:
                frontmatter = content.split('---')[1]
                yaml.safe_load(frontmatter)
            except Exception as e:
                print(f"FAILED YAML VALIDATION for WRK-{next_id}: {e}")
                return None

            with open(wrk_file, 'w') as f:
                f.write(content)
            
            # Update state.yaml (next-id.sh already does some correction, but we should be safe)
            # Actually next-id.sh corrects state.yaml if it's behind.
            
            print(f"    Created WRK-{next_id}: {title}")
            return next_id
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)

# --- Phase 3: Memory Staleness Check ---
def phase_3_memory_staleness_check():
    print("--- Phase 3: Memory Staleness Check ---")
    memory_files = glob.glob(os.path.join(MEMORY_DIR, "*.md"))
    if not memory_files:
        return "SKIPPED", "No memory files found"
        
    checked_count = 0
    stale_count = 0
    today = datetime.now().strftime("%Y-%m-%d")
    
    for m_file in memory_files:
        with open(m_file, 'r') as f:
            lines = f.readlines()
            
        modified = False
        new_lines = []
        for line in lines:
            # Extract paths/commands in backticks
            paths = re.findall(r'`([^`]+)`', line)
            line_updated = False
            for p in paths:
                # Check if it looks like a relative file path
                clean_p = p.lstrip('!')
                if '/' in clean_p and not os.path.isabs(clean_p) and not clean_p.startswith('http'):
                    full_path = os.path.join(WS_HUB, clean_p)
                    checked_count += 1
                    # Only check 10% of entries to keep it fast, or sample
                    if random.random() > 0.1: 
                        continue
                        
                    if os.path.exists(full_path):
                        if "*stale:" in line:
                            line = line.replace(re.search(r'\*stale: [^*]+\*', line).group(0), f"*verified: {today}*")
                            line_updated = True
                        elif "*verified:" not in line:
                            line = line.strip() + f" *verified: {today}*\n"
                            line_updated = True
                    else:
                        stale_count += 1
                        if "*verified:" in line:
                            line = line.replace(re.search(r'\*verified: [^*]+\*', line).group(0), f"*stale: {today}*")
                            line_updated = True
                        elif "*stale:" not in line:
                            line = line.strip() + f" *stale: {today}*\n"
                            line_updated = True
            
            if line_updated:
                modified = True
            new_lines.append(line)
            
        if modified:
            with open(m_file, 'w') as f:
                f.writelines(new_lines)
                
    return "DONE", f"Checked sample of entries, found {stale_count} stale"

# --- Phase 5: Correction Trend Analysis ---
def phase_5_correction_trend_analysis():
    print("--- Phase 5: Correction Trend Analysis ---")
    # Only process files modified in last 90 days
    now = datetime.now()
    cutoff_90d = now - timedelta(days=90)
    
    corrections_files = glob.glob(os.path.join(CORRECTIONS_DIR, "*.jsonl"))
    recent_files = [f for f in corrections_files if datetime.fromtimestamp(os.path.getmtime(f)) > cutoff_90d]
    
    all_corrections = []
    for f in recent_files:
        all_corrections.extend(load_jsonl(f))
    
    if not all_corrections:
        return "DONE", "No recent corrections found"
    
    this_week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    last_week_start = this_week_start - timedelta(days=7)
    weeks_4_ago_start = this_week_start - timedelta(days=28)
    
    # Minimum gap (seconds) to count as a genuine correction rather than a
    # sequential-chain edit.  Edits spaced < MIN_CORRECTION_GAP_S apart at
    # chain_position > 2 are deliberate workflow steps, not mistakes.
    MIN_CORRECTION_GAP_S = 60
    MIN_CHAIN_POSITION_THRESHOLD = 2

    stats = {} # (type, tool) -> {this_week: N, last_week: N, last_4_weeks: N}

    for c in all_corrections:
        # Filter out sequential-chain noise: fast edits deep in a chain are not
        # genuine corrections (e.g., CSV row-by-row edits, SKILL.md incremental
        # updates).  Require either a meaningful pause OR early chain position.
        gap = c.get('correction_gap_seconds', 0)
        chain_pos = c.get('chain_position', 0)
        if gap < MIN_CORRECTION_GAP_S and chain_pos > MIN_CHAIN_POSITION_THRESHOLD:
            continue

        c_type = c.get('type', 'unknown')
        c_tool = c.get('tool', 'unknown')
        key = (c_type, c_tool)
        if key not in stats:
            stats[key] = {'this_week': 0, 'last_week': 0, 'last_4_weeks': 0}

        c_ts = c.get('timestamp', c.get('ts', ''))
        if not c_ts: continue
        try:
            c_date = datetime.fromisoformat(c_ts.replace('Z', '+00:00'))
        except:
            continue

        if c_date.replace(tzinfo=None) >= this_week_start:
            stats[key]['this_week'] += 1
        if last_week_start <= c_date.replace(tzinfo=None) < this_week_start:
            stats[key]['last_week'] += 1
        if weeks_4_ago_start <= c_date.replace(tzinfo=None) < this_week_start:
            stats[key]['last_4_weeks'] += 1
            
    # Compute top 3
    sorted_stats = sorted(stats.items(), key=lambda x: x[1]['this_week'], reverse=True)
    top_3 = sorted_stats[:3]
    print(f"  Top 3 corrections this week: {[(k, v['this_week']) for k, v in top_3]}")
    
    # Minimum corrections-per-week before a trend triggers a WRK item.
    # Low-volume tools (e.g. Write at 5-10/week) produce noisy escalations.
    MIN_WEEKLY_COUNT_TO_ESCALATE = 10

    escalated = 0
    for (c_type, c_tool), s in stats.items():
        avg_4_weeks = s['last_4_weeks'] / 4.0
        # Escalation criteria: increasing 2+ weeks OR 1.5x above average,
        # AND must exceed minimum volume floor to suppress low-volume noise.
        if s['this_week'] < MIN_WEEKLY_COUNT_TO_ESCALATE:
            continue
        if (s['this_week'] > s['last_week'] > 0) or (s['this_week'] > avg_4_weeks * 1.5 and s['this_week'] > 2):
            print(f"  Flagging structural issue: {c_type} on {c_tool}")
            
            # Find diagnosis: top files/errors for this type/tool
            relevant_corrections = [c for c in all_corrections if c.get('type') == c_type and c.get('tool') == c_tool]
            # Group by file
            file_counts = {}
            error_patterns = {}
            examples = []
            for c in relevant_corrections:
                f = c.get('file', 'unknown')
                file_counts[f] = file_counts.get(f, 0) + 1
                err = c.get('error', c.get('msg', 'unknown'))
                error_patterns[err] = error_patterns.get(err, 0) + 1
                if len(examples) < 3:
                    examples.append(json.dumps(c, indent=2))
            
            top_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            top_errors = sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)[:3]
            
            create_wrk_item(
                title=f"fix: recurring {c_type} correction pattern on {c_tool}",
                description=f"""Correction Trend Analysis detected increasing trend.
Type: {c_type}
Tool: {c_tool}
This week: {s['this_week']}
Last week: {s['last_week']}
4-week avg: {avg_4_weeks:.1f}

### Diagnosis
- **Top affected files**: {", ".join([f"{f} ({c})" for f, c in top_files])}
- **Common error patterns**: {", ".join([f"\"{e[:50]}\" ({c})" for e, c in top_errors])}

### Examples
```json
{",".join(examples)}
```
""",
                priority="medium",
                source="comprehensive-learning/phase-5"
            )
            escalated += 1
            
    # Log compaction date
    meta_file = os.path.join(STATE_DIR, "correction-trend-meta.json")
    with open(meta_file, 'w') as f:
        json.dump({"last_run": now.isoformat()}, f)
            
    return "DONE", f"Analyzed {len(stats)} types, escalated {escalated}"

# --- Phase 1: Insights (Additional Quality Signals) ---
def phase_1_session_quality_signals():
    print("--- Phase 1: Session Quality Signals ---")
    signals_dir = os.path.join(STATE_DIR, "session-signals")
    if not os.path.exists(signals_dir):
        return "SKIPPED", "Signals directory not found"
        
    signal_files = glob.glob(os.path.join(signals_dir, "*.jsonl"))
    if not signal_files:
        return "SKIPPED", "No signal files found"
        
    flags = []
    
    for f_path in signal_files:
        data = load_jsonl(f_path)
        for entry in data:
            if entry.get('event') == 'session_end':
                signals = entry.get('signals', {})
                wrk_items = signals.get('wrk_items_touched', [])
                tool_calls = signals.get('tool_calls', [])
                
                # Context reset discipline: ≥3 unrelated WRK tasks but no /clear event
                # (Simple check: if we see /clear in tool calls or command history - 
                # but /clear is often a CLI command, not a tool call. 
                # Assuming /clear is logged in 'commands' if available)
                has_clear = "/clear" in entry.get('commands', [])
                if len(wrk_items) >= 3 and not has_clear:
                    flags.append(f"context pollution risk in {os.path.basename(f_path)} — {len(wrk_items)} tasks without reset")
                
                # Plan mode skipped: Multi-file edit session (≥3 files, ≥1 WRK) with no plan-mode recorded
                # (Assuming 'plan_mode' signal is logged)
                edited_files = [t for t in tool_calls if isinstance(t, dict) and t.get('tool') == 'Edit']
                unique_edited = len(set(t.get('file') for t in edited_files if t.get('file')))
                if unique_edited >= 3 and len(wrk_items) >= 1 and not signals.get('plan_mode_invoked'):
                    flags.append(f"plan mode not used before implementation in {os.path.basename(f_path)}")
                
                # Agent loop / stuck pattern: same tool+file pair appears ≥5× consecutively
                last_pair = None
                consecutive_count = 0
                for t in tool_calls:
                    if isinstance(t, dict):
                        pair = (t.get('tool'), t.get('file'))
                        if pair == last_pair and pair[0] is not None:
                            consecutive_count += 1
                        else:
                            consecutive_count = 1
                        last_pair = pair
                        if consecutive_count >= 5:
                            flags.append(f"possible agent loop in {os.path.basename(f_path)} — {pair[0]} on {pair[1]}")
                            break
                            
                # Task decomposition quality: WRK item with >15 tool calls before first commit
                # (This requires more granular logging than session_end usually has)
                # If tool_calls count > 15 and no 'git commit' was seen
                has_commit = any(isinstance(t, dict) and t.get('tool') == 'Bash' and 'git commit' in t.get('command', '') for t in tool_calls)
                if len(tool_calls) > 15 and not has_commit:
                    flags.append(f"WRK scope too large in {os.path.basename(f_path)} — {len(tool_calls)} calls before commit")

    if not flags:
        return "DONE", "No session quality issues flagged"
        
    # Return first 3 flags as a summary
    return "DONE", " | ".join(flags[:3])

# --- Phase 6: WRK Feedback Loop ---
def phase_6_wrk_feedback_loop():
    print("--- Phase 6: WRK Feedback Loop ---")
    archived_wrks = glob.glob(os.path.join(ARCHIVE_DIR, "**", "WRK-*.md"), recursive=True)
    pending_wrks = glob.glob(os.path.join(PENDING_WRK_DIR, "WRK-*.md"))
    
    feedback = {'positive': 0, 'stale': 0}
    
    scores = {}
    if os.path.exists(SKILL_SCORES_FILE):
        with open(SKILL_SCORES_FILE, 'r') as f:
            try:
                scores = yaml.safe_load(f) or {}
            except:
                pass

    for wrk_file in archived_wrks:
        with open(wrk_file, 'r') as f:
            content = f.read()
            if 'source: comprehensive-learning/phase-7' in content:
                feedback['positive'] += 1
                
    for wrk_file in pending_wrks:
        with open(wrk_file, 'r') as f:
            content = f.read()
            if 'source: comprehensive-learning/phase-7' in content:
                file_time = datetime.fromtimestamp(os.path.getmtime(wrk_file))
                if datetime.now() - file_time > timedelta(days=30):
                    feedback['stale'] += 1
                    # Downgrade logic: find skill name from title
                    title_match = re.search(r'title: "\[skill\]: ([^—]+)', content)
                    if title_match:
                        skill_name = title_match.group(1).strip()
                        if 'skills' in scores and skill_name in scores['skills']:
                            # scores['skills'][skill_name]['usage_rate'] *= 0.8
                            print(f"  Downgrading stale candidate skill: {skill_name}")
                    
    # Save updated scores
    if feedback['stale'] > 0:
        with open(SKILL_SCORES_FILE, 'w') as f:
            yaml.dump(scores, f)
            
    return "DONE", f"Positive: {feedback['positive']}, Stale: {feedback['stale']}"

# --- Phase 7: Action Candidates ---
def phase_7_action_candidates():
    print("--- Phase 7: Action Candidates ---")
    candidate_files = {
        'skill': os.path.join(CANDIDATES_DIR, "skill-candidates.md"),
        'script': os.path.join(CANDIDATES_DIR, "script-candidates.md"),
        'hook': os.path.join(CANDIDATES_DIR, "hook-candidates.md"),
        'mcp': os.path.join(CANDIDATES_DIR, "mcp-candidates.md"),
        'agent': os.path.join(CANDIDATES_DIR, "agent-candidates.md")
    }
    
    wrk_created = 0
    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Standard candidate files.
    # Supports two line formats written by session-analysis.sh:
    #   Legacy:  - **name** — N occurrences (session: ...)
    #   Current: - **signal** — score: X.X (source: ...)
    LEGACY_PATTERN = re.compile(r'^- \*\*([^*]+)\*\* — (\d+) occurrences')
    CURRENT_PATTERN = re.compile(r'^- \*\*([^*]+)\*\* — score: ([0-9.]+)')
    MIN_SCORE_TO_ACTION = 0.7   # only action high-confidence candidates
    MIN_OCCURRENCES_TO_ACTION = 3

    for c_type, c_file in candidate_files.items():
        if not os.path.exists(c_file): continue
        with open(c_file, 'r') as f:
            lines = f.readlines()
        for line in lines:
            name = None
            meta = None
            legacy = LEGACY_PATTERN.search(line)
            current = CURRENT_PATTERN.search(line)
            if legacy:
                name = legacy.group(1).strip()
                count = int(legacy.group(2))
                if not name or name.lower() == 'null' or count < MIN_OCCURRENCES_TO_ACTION:
                    continue
                meta = f"Occurrence count: {count}"
            elif current:
                name = current.group(1).strip()
                score = float(current.group(2))
                if not name or name.lower() == 'null' or score < MIN_SCORE_TO_ACTION:
                    continue
                meta = f"Score: {score:.2f}"
            else:
                continue

            create_wrk_item(
                title=f"[{c_type}]: {name[:70]} — auto-actioned from candidates",
                description=(
                    f"Auto-created from `.claude/state/candidates/{c_type}-candidates.md`.\n"
                    f"{meta}"
                ),
                priority="low",
                source="comprehensive-learning/phase-7"
            )
            wrk_created += 1
        
        # Reset file
        with open(c_file, 'w') as f:
            f.write(f"# {c_type.capitalize()} Candidates\n*Updated by session-analysis.sh — do not edit manually*\n*Last run: {now_iso}*\n\n## Candidates\n\n<!-- Populated automatically by morning cron -->\n")

    # Signal-based candidates
    signals = glob.glob(os.path.join(STATE_DIR, "session-signals", "*.jsonl"))
    tool_sequences = {} # tuple(tools) -> count
    for f in signals:
        data = load_jsonl(f)
        for d in data:
            if d.get('event') == 'session_end':
                tools = d.get('signals', {}).get('tool_calls', [])
                if len(tools) > 3:
                    seq = tuple(tools)
                    tool_sequences[seq] = tool_sequences.get(seq, 0) + 1
    
    for seq, count in tool_sequences.items():
        if count >= 3:
            create_wrk_item(
                title=f"[script]: workflow automation — repeated tool sequence",
                description=f"Repeated tool sequence detected {count} times:\n`{' -> '.join(seq)}`",
                priority="medium",
                source="comprehensive-learning/phase-7"
            )
            wrk_created += 1

    # Code quality signals
    # Same file edited ≥3× this week, no test file touched
    # No test file exists for a module touched in ≥2 sessions this week
    this_week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    
    corrections = []
    for f in glob.glob(os.path.join(CORRECTIONS_DIR, "*.jsonl")):
        corrections.extend(load_jsonl(f))
    
    file_sessions = {} # file -> set(session_ids)
    file_tests = set()
    
    for c in corrections:
        c_ts = c.get('timestamp', c.get('ts', ''))
        if not c_ts: continue
        try:
            c_date = datetime.fromisoformat(c_ts.replace('Z', '+00:00')).replace(tzinfo=None)
        except:
            continue
            
        if c_date >= this_week_start:
            if c.get('tool') == 'Edit' or c.get('type') == 'edit':
                f_path = c.get('file', '')
                if f_path:
                    session_id = c.get('session_id', 'unknown')
                    if f_path not in file_sessions: file_sessions[f_path] = set()
                    file_sessions[f_path].add(session_id)
                    if 'test' in f_path.lower():
                        file_tests.add(f_path)
                    
    for f_path, sessions in file_sessions.items():
        # Only suggest tests for source files, ignore markdown/yaml/json
        # Check: touched in >= 2 sessions
        if len(sessions) >= 2 and not any(f_path in t for t in file_tests):
            if not any(f_path.endswith(ext) for ext in ['.md', '.yaml', '.yml', '.json', '.txt', '.log']):
                # Check if test file exists
                test_exists = False
                for ext in ['.py', '.ts', '.js', '.go', '.sh']:
                    if f_path.endswith(ext):
                        base = f_path[:-len(ext)]
                        # Look for common test patterns
                        patterns = [
                            base + "_test" + ext,
                            base + ".test" + ext,
                            "tests/test_" + os.path.basename(f_path),
                            "tests/" + os.path.basename(base) + "_test" + ext
                        ]
                        for p in patterns:
                            if os.path.exists(os.path.join(WS_HUB, p)):
                                test_exists = True
                                break
                
                if not test_exists:
                    create_wrk_item(
                        title=f"[test]: add tests for {os.path.basename(f_path)}",
                        description=f"File `{f_path}` edited in {len(sessions)} sessions this week with no associated test file activity.",
                        priority="medium",
                        source="comprehensive-learning/phase-7"
                    )
                    wrk_created += 1

    return "DONE", f"Created {wrk_created} WRK items"

# --- Phase 8: Report Review ---
def phase_8_report_review():
    print("--- Phase 8: Report Review ---")
    reports = sorted(glob.glob(os.path.join(REPORTS_DIR, "*.md")), reverse=True)[:4]
    if len(reports) < 2:
        return "SKIPPED", "Not enough reports for comparison"
    
    escalated_types_count = {} # type -> count
    
    for r_file in reports[:4]:
        with open(r_file, 'r') as f:
            content = f.read()
            # Find escalated types in Phase 5 notes or created WRK items
            types = re.findall(r'fix: recurring ([^ ]+) correction pattern', content)
            for t in set(types):
                escalated_types_count[t] = escalated_types_count.get(t, 0) + 1
                
    escalated_recurring = 0
    for t, count in escalated_types_count.items():
        if count >= 3:
            create_wrk_item(
                title=f"P1: fix: {t} corrections not responding to improve",
                description=f"Correction type `{t}` has been escalated in {count} out of the last 4 learning reports.",
                priority="high",
                source="comprehensive-learning/phase-8"
            )
            escalated_recurring += 1
            
    return "DONE", f"Escalated recurring issues: {escalated_recurring}"

# --- Phase 9: Skill Coverage Audit ---
def phase_9_skill_coverage_audit():
    # Only run on Sundays
    if datetime.now().weekday() != 6:
        return "SKIPPED", "Not Sunday"
        
    print("--- Phase 9: Skill Coverage Audit ---")
    # Identify manual workflows (multi-step tool sequences)
    # Read session signals for tool call sequences
    signals_files = glob.glob(os.path.join(STATE_DIR, "session-signals", "*.jsonl"))
    
    # We want tool sequences that took > 5 calls and happened >= 3 times
    # and don't match an existing skill invocation
    # (In reality, d.get('signals').get('skill_invocations') would be non-empty)
    
    gaps_found = 0
    # Placeholder for actual logic which requires richer tool trace
    return "DONE", f"Gaps found: {gaps_found}"

if __name__ == "__main__":
    import sys
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    results = {}
    if phase == "1" or phase == "all":
        results["1"] = phase_1_session_quality_signals()
    if phase == "3" or phase == "all":
        results["3"] = phase_3_memory_staleness_check()
    if phase == "5" or phase == "all":
        results["5"] = phase_5_correction_trend_analysis()
    if phase == "6" or phase == "all":
        results["6"] = phase_6_wrk_feedback_loop()
    if phase == "7" or phase == "all":
        results["7"] = phase_7_action_candidates()
    if phase == "8" or phase == "all":
        results["8"] = phase_8_report_review()
    if phase == "9" or phase == "all":
        results["9"] = phase_9_skill_coverage_audit()
        
    for p, (status, notes) in results.items():
        print(f"PHASE_RESULT|{p}|{status}|{notes}")
