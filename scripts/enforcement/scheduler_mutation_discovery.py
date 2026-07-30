"""Conservative scheduler-indirection and operation-shape derivation."""
from __future__ import annotations

import re


def derive_kanban_operations(records: dict[bytes, bytes]) -> set[str]:
    body = records.get(b"scripts/install/setup-kanban-loader-timer.sh", b"")
    code = b"\n".join(
        line for line in body.splitlines() if not line.lstrip().startswith(b"#")
    )
    checks = {
        "install:systemd-unit-write": rb"do_install\(\)[\s\S]+service_body \| write_unit",  # scheduler-mutation-forensic
        "install:systemd-enable": rb"do_install\(\)[\s\S]+run_systemctl enable --now",  # scheduler-mutation-forensic
        "install:crontab-replace": rb"do_install\(\)[\s\S]+run_crontab -",  # scheduler-mutation-forensic
        "uninstall:systemd-unit-remove": rb"do_uninstall\(\)[\s\S]+remove_unit \"\$SERVICE_PATH\"",  # scheduler-mutation-forensic
        "uninstall:systemd-disable": rb"do_uninstall\(\)[\s\S]+run_systemctl disable --now",  # scheduler-mutation-forensic
        "uninstall:crontab-replace": rb"do_uninstall\(\)[\s\S]+run_crontab -",  # scheduler-mutation-forensic
    }
    return {name for name, pattern in checks.items() if re.search(pattern, code)}


def has_primitive_alias_call(code: bytes) -> bool:
    cron_name = rb"cron" + rb"tab"
    task_name = rb"Scheduled" + rb"Task"
    shell = re.findall(
        rb"(?m)(?:^|;|&&|\|\|)\s*([A-Za-z_]\w*)\s*=\s*['\"]?(" + cron_name
        + rb")[" + rb"'\"]?\s*(?=;|&&|\|\||$)",
        code,
    )
    powershell = re.findall(
        rb"(?mi)(?:^|;)\s*\$([A-Za-z_]\w*)\s*=\s*['\"]"
        rb"((?:Register|Unregister|Set)-" + task_name + rb")[" + rb"'\"]\s*(?=;|$)",
        code,
    )
    for variable, _primitive in shell:
        prefix = rb"(?:(?:command|builtin)\s+|env(?:\s+[A-Za-z_]\w*=[^\s;|&]+)*\s+)?"
        call = (
            rb"(?m)(?:^|[|;&])\s*" + prefix + rb"[\"']?\$\{?" + variable
            + rb"\}?[\"']?(?=\s|$)"
        )
        if re.search(call, code):
            return True
    for variable, _primitive in powershell:
        reference = rb"\$" + variable + rb"\b"
        direct = rb"(?mi)(?:^|;)\s*[&.]\s*[\"']?" + reference
        expression = rb"(?mi)(?:^|;)\s*Invoke-Expression\b[^\n;]*" + reference
        if re.search(direct, code) or re.search(expression, code):
            return True
    return False


def _extract_block(code: bytes, pattern: bytes) -> tuple[bytes, bytes] | None:
    match = re.search(pattern, code, re.IGNORECASE)
    if not match:
        return None
    start = code.find(b"{", match.start())
    depth = 0
    for index in range(start, len(code)):
        if code[index:index + 1] == b"{":
            depth += 1
        elif code[index:index + 1] == b"}":
            depth -= 1
            if depth == 0:
                return code[start + 1:index], code[index + 1:]
    return None


def derive_windows_task_operations(records: dict[bytes, bytes]) -> set[str]:
    body = records.get(b"scripts/windows/setup-scheduler-tasks.ps1", b"")
    code = b"\n".join(
        line for line in body.splitlines() if not line.lstrip().startswith(b"#")
    )
    function = _extract_block(code, rb"function\s+Register-ClaudeTask\s*\{")
    if not function:
        return set()
    body, _after_function = function
    remove = _extract_block(body, rb"if\s*\(\$RemoveMode\)\s*\{")
    if not remove:
        return set()
    remove_body, replacement = remove
    task_name = rb"Scheduled" + rb"Task"
    operations = set()
    if re.search(rb"Unregister-" + task_name, remove_body) and re.search(rb"\breturn\b", remove_body):
        operations.add("remove:unregister-fixed-task")
    existing = _extract_block(replacement, rb"if\s*\(\$existing\)\s*\{")
    if existing:
        existing_body, after_existing = existing
        if re.search(rb"Unregister-" + task_name, existing_body) and re.search(
            rb"Register-" + task_name, after_existing
        ):
            operations.add("replace:unregister-register-fixed-task")
    return operations
