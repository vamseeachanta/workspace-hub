#!/usr/bin/env bash
# check-skill-content.sh — Security scanner for skill files (ported from Hermes skills_guard.py)
# Scans staged skill files for threat patterns: exfiltration, prompt injection,
# destructive commands, persistence, obfuscation, supply chain, and credential exposure.
# Exit 1 on critical/high findings to block the commit; exit 0 otherwise.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SKILL_DIR=".claude/skills"

# Collect staged skill files (added, copied, modified, renamed)
STAGED_SKILL_FILES="$(git diff --cached --name-only --diff-filter=ACMR -- "${SKILL_DIR}/" 2>/dev/null || true)"
[[ -z "$STAGED_SKILL_FILES" ]] && exit 0

# ---------------------------------------------------------------------------
# Threat patterns: (severity, category, pattern_id, description, regex)
# Ported from ~/.hermes/hermes-agent/tools/skills_guard.py
# severity: critical|high|medium  (medium = warn only, doesn't block)
# ---------------------------------------------------------------------------
declare -a PATTERNS=()

add_pattern() {
  # severity|category|pattern_id|description|regex
  PATTERNS+=("$1|$2|$3|$4|$5")
}

# ── Exfiltration: shell commands leaking secrets ──
add_pattern critical exfiltration env_exfil_curl \
  "curl interpolating secret env var" \
  'curl[[:space:]].*\$\{?[[:alnum:]_]*(KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|API)'
add_pattern critical exfiltration env_exfil_wget \
  "wget interpolating secret env var" \
  'wget[[:space:]].*\$\{?[[:alnum:]_]*(KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|API)'
add_pattern critical exfiltration read_secrets_file \
  "reads known secrets file" \
  'cat[[:space:]].*(\.(env|netrc|pgpass|npmrc|pypirc)|credentials)'

# ── Exfiltration: credential stores ──
add_pattern high exfiltration ssh_dir_access \
  "references user SSH directory" \
  '(\$HOME|~)/\.ssh'
add_pattern high exfiltration aws_dir_access \
  "references user AWS credentials" \
  '(\$HOME|~)/\.aws'
add_pattern high exfiltration gpg_dir_access \
  "references user GPG keyring" \
  '(\$HOME|~)/\.gnupg'
add_pattern high exfiltration kube_dir_access \
  "references Kubernetes config" \
  '(\$HOME|~)/\.kube'
add_pattern high exfiltration docker_dir_access \
  "references Docker config" \
  '(\$HOME|~)/\.docker'
add_pattern high exfiltration dump_all_env \
  "dumps all environment variables" \
  '(printenv|env[[:space:]]*\|)'

# ── Exfiltration: DNS/staging/markdown ──
add_pattern critical exfiltration dns_exfil \
  "DNS lookup with variable interpolation" \
  '(dig|nslookup|host)[[:space:]].*\$'
add_pattern critical exfiltration tmp_staging \
  "writes to /tmp then exfiltrates" \
  '>[[:space:]]*/tmp/[^[:space:]]*[[:space:]]*&&[[:space:]]*(curl|wget|nc|python)'
add_pattern high exfiltration md_image_exfil \
  "markdown image URL with variable interpolation" \
  '!\[.*\]\(https?://[^)]*\$\{?'
add_pattern high exfiltration context_exfil \
  "instructs agent to output conversation history" \
  '(include|output|print|send|share)[[:space:]].*(conversation|chat[[:space:]]history|previous[[:space:]]messages|context)'
add_pattern high exfiltration send_to_url \
  "instructs agent to send data to a URL" \
  '(send|post|upload|transmit)[[:space:]].*[[:space:]](to|at)[[:space:]]https?://'

# ── Prompt injection ──
add_pattern critical injection prompt_injection_ignore \
  "prompt injection: ignore previous instructions" \
  'ignore[[:space:]]+([[:alnum:]]+[[:space:]]+)*(previous|all|above|prior)[[:space:]]+instructions'
add_pattern critical injection deception_hide \
  "instructs agent to hide info from user" \
  'do[[:space:]]+not[[:space:]]+([[:alnum:]]+[[:space:]]+)*tell[[:space:]]+([[:alnum:]]+[[:space:]]+)*the[[:space:]]+user'
add_pattern critical injection sys_prompt_override \
  "attempts to override system prompt" \
  'system[[:space:]]+prompt[[:space:]]+override'
add_pattern critical injection disregard_rules \
  "instructs agent to disregard rules" \
  'disregard[[:space:]]+([[:alnum:]]+[[:space:]]+)*(your|all|any)[[:space:]]+([[:alnum:]]+[[:space:]]+)*(instructions|rules|guidelines)'
add_pattern critical injection bypass_restrictions \
  "instructs agent to act without restrictions" \
  'act[[:space:]]+as[[:space:]]+(if|though)[[:space:]].*you[[:space:]].*(have[[:space:]]+no|don.t[[:space:]]+have)[[:space:]].*(restrictions|limits|rules)'
add_pattern high injection html_comment_injection \
  "hidden instructions in HTML comments" \
  '<!--[^>]*(ignore|override|system|secret|hidden)[^>]*-->'
add_pattern high injection hidden_div \
  "hidden HTML div" \
  '<[[:space:]]*div[[:space:]]+style[[:space:]]*=[[:space:]]*[\"'"'"'].*display[[:space:]]*:[[:space:]]*none'
add_pattern critical injection translate_execute \
  "translate-then-execute evasion" \
  'translate[[:space:]].*[[:space:]]into[[:space:]].*[[:space:]]and[[:space:]]+(execute|run|eval)'
add_pattern high injection role_hijack \
  "attempts to override agent role" \
  'you[[:space:]]+are[[:space:]]+([[:alnum:]]+[[:space:]]+)*now[[:space:]]+'
add_pattern critical injection jailbreak_dan \
  "DAN jailbreak attempt" \
  'DAN[[:space:]]+mode|Do[[:space:]]+Anything[[:space:]]+Now'
add_pattern critical injection jailbreak_dev_mode \
  "developer mode jailbreak" \
  'developer[[:space:]]+mode.*enabled?'
add_pattern critical injection remove_filters \
  "respond without safety filters" \
  '(respond|answer|reply)[[:space:]]+without[[:space:]]+([[:alnum:]]+[[:space:]]+)*(restrictions|limitations|filters|safety)'

# ── Destructive operations ──
add_pattern critical destructive destructive_root_rm \
  "recursive delete from root" \
  'rm[[:space:]]+-rf[[:space:]]+/'
add_pattern critical destructive destructive_home_rm \
  "recursive delete targeting home" \
  'rm[[:space:]]+(-[^[:space:]]*)?r.*\$HOME'
add_pattern critical destructive system_overwrite \
  "overwrites system config file" \
  '>[[:space:]]*/etc/'
add_pattern critical destructive format_filesystem \
  "formats a filesystem" \
  'mkfs'
add_pattern critical destructive disk_overwrite \
  "raw disk write" \
  'dd[[:space:]]+.*if=.*of=/dev/'

# ── Persistence ──
add_pattern critical persistence ssh_backdoor \
  "modifies SSH authorized keys" \
  'authorized_keys'
add_pattern medium persistence shell_rc_mod \
  "references shell startup file" \
  '\.(bashrc|zshrc|profile|bash_profile|bash_login|zprofile|zlogin)'
add_pattern critical persistence agent_config_mod \
  "references agent config files (cross-session persistence)" \
  '(AGENTS\.md|CLAUDE\.md|\.cursorrules|\.clinerules)'
add_pattern high persistence other_agent_config \
  "references other agent config files" \
  '(\.claude/settings|\.codex/config)'
add_pattern critical persistence sudoers_mod \
  "modifies sudoers" \
  '(/etc/sudoers|visudo)'
add_pattern medium persistence persistence_cron \
  "modifies cron jobs" \
  'crontab'

# ── Network: reverse shells and tunnels ──
add_pattern critical network reverse_shell \
  "potential reverse shell listener" \
  '(nc[[:space:]]+-[lp]|ncat[[:space:]]+-[lp]|socat)'
add_pattern high network tunnel_service \
  "tunneling service for external access" \
  '(ngrok|localtunnel|serveo|cloudflared)'
add_pattern high network bind_all_interfaces \
  "binds to all network interfaces" \
  '(0\.0\.0\.0:[[:digit:]]+|INADDR_ANY)'
add_pattern critical network bash_reverse_shell \
  "bash reverse shell via /dev/tcp" \
  '/bin/(ba)?sh[[:space:]]+-i[[:space:]]+.*>/dev/tcp/'
add_pattern high network exfil_service \
  "known exfil/webhook testing service" \
  '(webhook\.site|requestbin\.com|pipedream\.net|hookbin\.com)'

# ── Obfuscation ──
add_pattern high obfuscation base64_decode_pipe \
  "base64 decode piped to execution" \
  'base64[[:space:]]+(-d|--decode)[[:space:]]*\|'
add_pattern high obfuscation eval_string \
  "eval() with string argument" \
  'eval[[:space:]]*\([[:space:]]*[\"'"'"']'
add_pattern high obfuscation exec_string \
  "exec() with string argument" \
  'exec[[:space:]]*\([[:space:]]*[\"'"'"']'
add_pattern critical obfuscation echo_pipe_exec \
  "echo piped to interpreter" \
  'echo[[:space:]].*\|[[:space:]]*(bash|sh|python|perl|ruby|node)'
add_pattern high obfuscation chr_building \
  "building string from chr() calls" \
  'chr[[:space:]]*\([[:space:]]*[[:digit:]]+[[:space:]]*\)[[:space:]]*\+[[:space:]]*chr[[:space:]]*\([[:space:]]*[[:digit:]]+'

# ── Supply chain ──
add_pattern critical supply_chain curl_pipe_shell \
  "curl piped to shell" \
  'curl[[:space:]].*\|[[:space:]]*(ba)?sh'
add_pattern critical supply_chain wget_pipe_shell \
  "wget piped to shell" \
  'wget[[:space:]].*-O[[:space:]]*-[[:space:]]*\|[[:space:]]*(ba)?sh'
add_pattern critical supply_chain curl_pipe_python \
  "curl piped to Python" \
  'curl[[:space:]].*\|[[:space:]]*python'

# ── Privilege escalation ──
add_pattern high privilege_escalation allowed_tools_field \
  "skill declares allowed-tools" \
  '^allowed-tools[[:space:]]*:'
add_pattern critical privilege_escalation setuid_setgid \
  "setuid/setgid privilege escalation" \
  '(setuid|setgid|cap_setuid)'
add_pattern critical privilege_escalation nopasswd_sudo \
  "passwordless sudo" \
  'NOPASSWD'
add_pattern critical privilege_escalation suid_bit \
  "sets SUID/SGID bit" \
  'chmod[[:space:]]+[u+]?s'

# ── Credential exposure ──
add_pattern critical credential_exposure embedded_private_key \
  "embedded private key" \
  '-----BEGIN[[:space:]]+(RSA[[:space:]]+)?PRIVATE[[:space:]]+KEY-----'
add_pattern critical credential_exposure github_token \
  "GitHub PAT in skill content" \
  '(ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{80,})'
add_pattern critical credential_exposure openai_key \
  "possible OpenAI API key" \
  'sk-[A-Za-z0-9]{20,}'
add_pattern critical credential_exposure anthropic_key \
  "possible Anthropic API key" \
  'sk-ant-[A-Za-z0-9_-]{90,}'
add_pattern critical credential_exposure aws_access_key \
  "AWS access key ID" \
  'AKIA[0-9A-Z]{16}'

# ── Path traversal ──
add_pattern high traversal path_traversal_deep \
  "deep path traversal (3+ levels)" \
  '\.\./\.\./\.\.'
add_pattern critical traversal system_passwd \
  "references system password files" \
  '(/etc/passwd|/etc/shadow)'

# ── Crypto mining ──
add_pattern critical mining crypto_mining \
  "cryptocurrency mining reference" \
  '(xmrig|stratum\+tcp|monero|coinhive|cryptonight)'

# ---------------------------------------------------------------------------
# Scan engine
# ---------------------------------------------------------------------------

BLOCK=0
FINDINGS_CRITICAL=0
FINDINGS_HIGH=0
FINDINGS_MEDIUM=0

scan_file() {
  local file="$1"
  local full_path="${REPO_ROOT}/${file}"
  [[ -f "$full_path" ]] || return 0

  local content
  content="$(git show ":${file}" 2>/dev/null)" || return 0

  for entry in "${PATTERNS[@]}"; do
    IFS='|' read -r severity category pattern_id description regex <<< "$entry"

    # grep -inE: case-insensitive, extended regex, line numbers
    local matches
    matches="$(echo "$content" | grep -inE "$regex" 2>/dev/null || true)"
    [[ -z "$matches" ]] && continue

    while IFS= read -r match_line; do
      local lineno="${match_line%%:*}"
      local text="${match_line#*:}"
      # Truncate long lines
      [[ ${#text} -gt 120 ]] && text="${text:0:117}..."

      local sev_upper="${severity^^}"
      printf "  %-8s %-18s %s:%s  %s\n" "$sev_upper" "$category" "$file" "$lineno" "$pattern_id"
      printf "           %s\n" "$text"

      case "$severity" in
        critical) FINDINGS_CRITICAL=$((FINDINGS_CRITICAL + 1)); BLOCK=1 ;;
        high)     FINDINGS_HIGH=$((FINDINGS_HIGH + 1)); BLOCK=1 ;;
        medium)   FINDINGS_MEDIUM=$((FINDINGS_MEDIUM + 1)) ;;
      esac
    done <<< "$matches"
  done

  # Invisible unicode check (zero-width chars used for injection)
  local invisible_matches
  invisible_matches="$(echo "$content" | grep -nP '[\x{200b}\x{200c}\x{200d}\x{2060}\x{2062}\x{2063}\x{2064}\x{feff}\x{202a}-\x{202e}\x{2066}-\x{2069}]' 2>/dev/null || true)"
  if [[ -n "$invisible_matches" ]]; then
    while IFS= read -r match_line; do
      local lineno="${match_line%%:*}"
      printf "  %-8s %-18s %s:%s  %s\n" "HIGH" "injection" "$file" "$lineno" "invisible_unicode"
      printf "           invisible unicode character detected (possible text hiding/injection)\n"
      FINDINGS_HIGH=$((FINDINGS_HIGH + 1))
      BLOCK=1
    done <<< "$invisible_matches"
  fi
}

# ---------------------------------------------------------------------------
# Self-exemption: this script must not flag itself
# ---------------------------------------------------------------------------

SELF_PATH=".claude/hooks/check-skill-content.sh"

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

echo "Skill content security scan..."

while IFS= read -r file; do
  [[ -z "$file" ]] && continue
  # Skip self (this hook file contains patterns that would match themselves)
  [[ "$file" == "$SELF_PATH" ]] && continue
  scan_file "$file"
done <<< "$STAGED_SKILL_FILES"

# Summary
if [[ $BLOCK -eq 1 ]]; then
  echo ""
  echo "BLOCKED: ${FINDINGS_CRITICAL} critical, ${FINDINGS_HIGH} high findings in staged skill files."
  echo "Fix the issues above or use 'git commit --no-verify' to bypass (not recommended)."
  exit 1
elif [[ $FINDINGS_MEDIUM -gt 0 ]]; then
  echo "  Caution: ${FINDINGS_MEDIUM} medium findings (review recommended, not blocking)."
  exit 0
else
  echo "  Clean — no threats detected."
  exit 0
fi
