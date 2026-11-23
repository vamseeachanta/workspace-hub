#!/usr/bin/env python3
"""Local faster-whisper transcription bridge for push-to-talk dictation."""
import os
import sys

try:
    from faster_whisper import WhisperModel
except ImportError:
    sys.stderr.write(
        "faster-whisper not installed. Run: "
        "uv pip install --python $(command -v python3) faster-whisper\n"
    )
    raise SystemExit(3)


def main() -> int:
    if len(sys.argv) < 2:
        sys.stderr.write("usage: transcribe.py <wavfile>\n")
        return 2

    model_name = os.environ.get("DICTATE_MODEL", "base.en")
    device = os.environ.get("DICTATE_DEVICE", "cpu")
    compute = os.environ.get("DICTATE_COMPUTE", "int8")
    language = os.environ.get("DICTATE_LANGUAGE", "en")
    model = WhisperModel(model_name, device=device, compute_type=compute)
    segments, _info = model.transcribe(sys.argv[1], language=language, vad_filter=True)
    text = " ".join(segment.text.strip() for segment in segments).strip()
    print(" ".join(text.split()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
