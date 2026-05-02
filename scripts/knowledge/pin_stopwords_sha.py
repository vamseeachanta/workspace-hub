from __future__ import annotations

import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts/knowledge/run_batch_pack_2.py"
STOPWORDS = ROOT / "scripts/knowledge/data/stopwords_en_v1.txt"


def main() -> int:
    digest = hashlib.sha256(STOPWORDS.read_bytes()).hexdigest()
    content = RUNNER.read_text(encoding="utf-8")
    content, count = re.subn(
        r'STOPWORDS_SHA = "[^"]+"',
        f'STOPWORDS_SHA = "{digest}"',
        content,
        count=1,
    )
    if count != 1:
        raise RuntimeError("could not update STOPWORDS_SHA")
    RUNNER.write_text(content, encoding="utf-8")
    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
