# extract-script-ideas.jq - jq filter for script idea extraction
# Used by extract-script-ideas.sh

# Extract Bash commands only
def bash_commands:
    [.[] | select(.tool == "Bash" and .phase == "pre" and .command and (.command | length) > 0)];

# Normalize command for pattern matching
def normalize_cmd:
    . | gsub("\\s+"; " ") | gsub("^\\s+|\\s+$"; "") |
    gsub("/[a-zA-Z0-9/_.-]+"; "/<PATH>") |
    gsub("[0-9a-f]{7,}"; "<HASH>") |
    gsub("[0-9]{4}-[0-9]{2}-[0-9]{2}"; "<DATE>") |
    gsub("\"[^\"]+\""; "\"<STRING>\"");

# Find repeated command patterns (candidates for scripts)
def command_patterns:
    bash_commands |
    map({
        original: .command,
        normalized: (.command | normalize_cmd),
        repo: .repo
    }) |
    group_by(.normalized) |
    map({
        pattern: .[0].normalized,
        examples: [.[].original] | unique | .[0:3],
        count: length,
        repos: [.[].repo] | unique,
        cross_repo: (([.[].repo] | unique | length) >= 2)
    }) |
    sort_by(-.count) | .[0:20];

# Find git workflow patterns (common sequences)
def git_workflows:
    bash_commands |
    [.[] | select(.command | test("^git "))] |
    map(.command | split(" ")[0:2] | join(" ")) |
    group_by(.) |
    map({command: .[0], count: length}) |
    sort_by(-.count) | .[0:10];

# Find script creation/modification activity
def script_activity:
    [.[] | select(
        (.tool == "Write" or .tool == "Edit") and
        .file != null and
        (.file | test("\\.sh$"))
    )] |
    group_by(.file) |
    map({
        file: .[0].file,
        edits: length,
        sessions: ([.[].session_id] | unique | length)
    }) |
    sort_by(-.edits) | .[0:10];

# Find complex command chains (piped commands that could be scripts)
def complex_commands:
    bash_commands |
    [.[] | select(.command | test("\\|.*\\|"))] |
    map({
        command: .command,
        pipe_count: ((.command | split("|") | length) - 1),
        repo: .repo
    }) |
    sort_by(-.pipe_count) | .[0:10];

# Score patterns for script creation potential
def score_pattern:
    . as $p |
    (if $p.count >= 5 then 0.4 elif $p.count >= 3 then 0.3 else 0.2 end) +
    (if $p.cross_repo then 0.3 else 0.1 end) +
    (if ($p.pattern | length) > 30 then 0.2 else 0.1 end) +
    (if (($p.repos | length) >= 3) then 0.1 else 0 end);

# Generate script ideas with scores
def script_ideas:
    command_patterns |
    map(. + {
        score: (. | score_pattern),
        suggestion: (
            if .cross_repo then "Cross-repo utility script"
            elif (.pattern | test("^git ")) then "Git workflow automation"
            elif (.pattern | test("\\|")) then "Pipeline automation script"
            else "Utility script"
            end
        )
    }) |
    sort_by(-.score);

# Find enhancement opportunities for existing scripts
def enhancement_suggestions:
    script_activity |
    map(select(.edits >= 2)) |
    map({
        script: .file,
        edits: .edits,
        sessions: .sessions,
        suggestion: (
            if .edits >= 5 then "Frequently modified - consider stabilization"
            elif .sessions >= 2 then "Cross-session usage - document and test"
            else "Active development - monitor for patterns"
            end
        )
    });

# Identify skill candidates (high-value patterns)
def skill_candidates:
    script_ideas |
    map(select(.score >= 0.6)) |
    map({
        pattern: .pattern,
        examples: .examples,
        score: .score,
        repos: .repos,
        skill_type: (
            if (.pattern | test("^git ")) then "git-workflow"
            elif (.pattern | test("test|pytest|jest")) then "testing"
            elif (.pattern | test("docker|container")) then "containerization"
            elif (.pattern | test("npm|yarn|pip|uv")) then "dependency-management"
            else "automation"
            end
        ),
        suggested_name: (
            .pattern |
            gsub("<[A-Z]+>"; "") |
            gsub("[^a-zA-Z0-9]+"; "-") |
            gsub("^-+|-+$"; "") |
            .[0:30]
        )
    });

# Build output
{
    extraction_date: (now | strftime("%Y-%m-%dT%H:%M:%SZ")),
    days_analyzed: $days,
    total_bash_commands: (bash_commands | length),
    unique_patterns: (command_patterns | length),
    script_ideas: script_ideas,
    git_workflows: git_workflows,
    complex_commands: complex_commands,
    script_activity: script_activity,
    enhancement_suggestions: enhancement_suggestions,
    skill_candidates: skill_candidates,
    existing_scripts: $existing,
    insights: [
        (if ((script_ideas | map(select(.cross_repo)) | length) >= 3) then
            "Multiple cross-repo patterns detected - consider workspace-level automation"
        else null end),
        (if ((complex_commands | length) >= 5) then
            "Many complex pipelines - good candidates for script extraction"
        else null end),
        (if ((enhancement_suggestions | length) >= 2) then
            "Several scripts under active development - review for patterns"
        else null end),
        (if ((skill_candidates | length) >= 1) then
            "High-value patterns identified - ready for skill creation"
        else null end)
    ] | map(select(. != null))
}
