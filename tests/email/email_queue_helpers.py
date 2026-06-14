import importlib
import hashlib
from pathlib import Path

import yaml


def load_queue_state():
    return importlib.import_module("scripts.email.queue_state")


def write_accounts(path: Path):
    path.write_text(
        yaml.safe_dump(
            {
                "accounts": {
                    "ace": {
                        "email": "vamsee.achanta@aceengineer.com",
                        "enabled": True,
                    },
                    "personal": {
                        "email": "achantav@gmail.com",
                        "enabled": True,
                    },
                    "skestates": {
                        "email": "skestatesinc@gmail.com",
                        "enabled": False,
                    },
                }
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def clean_precheck(log_path: Path):
    return {
        "checked_accounts": ["ace", "personal"],
        "log_byte_offset": log_path.stat().st_size if log_path.exists() else 0,
        "log_sha256": hashlib.sha256(
            log_path.read_bytes() if log_path.exists() else b""
        ).hexdigest(),
        "unknown_status": "evaluated",
        "unknown_count": 0,
        "config_missing_count": 0,
        "newer_message_pending_count": 0,
        "snapshot_comparison_missing_count": 0,
        "pending_thread_ids": [],
        "baseline_missing_thread_ids": [],
        "unknown_thread_ids": [],
        "config_missing_thread_ids": [],
        "newer_message_thread_ids": [],
        "snapshot_comparison_missing_thread_ids": [],
    }
