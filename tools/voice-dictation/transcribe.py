#!/usr/bin/env python3
"""Local, free, offline speech-to-text for the push-to-talk dictation tool.

Reads a 16 kHz mono WAV path on argv[1], prints the transcript to stdout.
Uses faster-whisper (CTranslate2) — no cloud, no API key, no per-token cost.

Config via env (so one script fits a thin laptop or a CUDA workstation):
    DICTATE_MODEL    whisper model size   (default: base.en)
    DICTATE_DEVICE   cpu | cuda           (default: cpu)
    DICTATE_COMPUTE  int8 | float16 | ... (default: int8 — fast on CPU)
The model downloads once to ~/.cache/huggingface, then runs offline.
"""
import os
import sys

try:
    from faster_whisper import WhisperModel
except ImportError:
    sys.stderr.write(
        "faster-whisper not installed. Run: "
        "uv pip install faster-whisper  (or pip install --user faster-whisper)\n"
    )
    raise SystemExit(3)

MODEL = os.environ.get("DICTATE_MODEL", "base.en")
DEVICE = os.environ.get("DICTATE_DEVICE", "cpu")
COMPUTE = os.environ.get("DICTATE_COMPUTE", "int8")


def main() -> int:
    if len(sys.argv) < 2:
        sys.stderr.write("usage: transcribe.py <wavfile>\n")
        return 2
    wav = sys.argv[1]
    model = WhisperModel(MODEL, device=DEVICE, compute_type=COMPUTE)
    # vad_filter suppresses the phantom-text hallucinations Whisper emits on
    # silence/noise between sentences — critical for a dictation tool.
    segments, _info = model.transcribe(wav, language="en", vad_filter=True)
    text = " ".join(seg.text.strip() for seg in segments).strip()
    print(" ".join(text.split()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
