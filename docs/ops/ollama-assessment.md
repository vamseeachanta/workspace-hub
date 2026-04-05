# Ollama Local LLM Runtime - Hardware Assessment

> Date: 2026-04-05
> Status: Assessment complete, installation pending
> Related: workspace-hub#1921, workspace-hub#1922

## Executive Summary

Ollama is installable across our 4-machine ecosystem, but model size is hardware-limited.
The RTX 3060 12GB machine (one of the licensed-win boxes) is the primary candidate for
serious local LLM work. This machine (ace-linux-1) is only viable for embeddings and
tiny models.

## Machine-by-Machine Assessment

| Machine | GPU | VRAM | CUDA | CPU | RAM | Free Disk | Max GPU Model | Status |
|---------|-----|------|------|-----|-----|-----------|---------------|--------|
| ace-linux-1 (dev-primary) | GTX 750 Ti | 2 GB | 5.0 | Xeon 32T | 32 GB | 123 GB | 1.2B | Assessed |
| ace-linux-2 (dev-secondary) | NVIDIA T400 | 4 GB | 7.5 | TBD | 32 GB | TBD | 4B | Assessed |
| licensed-win-1 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Audit needed |
| licensed-win-2 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Audit needed |

**Note:** Confirmed that one of the Windows machines has an RTX 3060 12GB. Which one
needs verification. RTX 3060 can run 8B-14B models on GPU.

## Use Cases by Capability

### ace-linux-1 (this machine)
- Embedding generation (nomic-embed-text, mxbai-embed-large)
- Fallback when subscriptions are throttled (tiny models only)
- Local document pre-processing

### ace-linux-2 (T400 4GB)
- 3B-4B models for summarization, light reasoning
- Concurrent embedding pipeline
- Local code review pre-screening

### RTX 3060 12GB (Windows machine)
- 8B-14B models for serious code review and reasoning
- Primary Ollama runner for the ecosystem
- Multiple models running simultaneously

## Model Compatibility Matrix

| VRAM Budget | Models That Fit (Q4 GGUF) | Expected Token/s |
|-------------|---------------------------|------------------|
| 2 GB (750 Ti) | qwen3.5:0.6b, lfm2.5:1.2b | 15-25 tok/s |
| 4 GB (T400) | qwen3.5:4b, llama3.2:3b | 10-15 tok/s |
| 12 GB (3060) | qwen3.5:8b, qwen3-coder:7b, devstral:small-2 | 30-50 tok/s |

## Installation Commands

### Linux (ace-linux-1, ace-linux-2)
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama --version
ollama pull <model>
```

### Windows (licensed-win machines)
```powershell
winget install Ollama.Ollama
ollama --version
ollama pull <model>
```

## Next Steps
1. Complete #1921: Install on ace-linux-1 for embeddings
2. Complete #1922: Identify RTX 3060 machine, roll out ecosystem-wide
3. Design integration workflow (fallback routing, shared embeddings)
