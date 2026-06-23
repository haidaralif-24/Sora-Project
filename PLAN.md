# Sora Project — Architecture & Plan

This document captures the system design for Sora before implementation goes further. It records the reasoning behind each tech choice, the build order, and the questions we haven't locked in yet — so we don't re-litigate decisions later.

## 1. Vision

Sora is a desktop AI companion that goes beyond a static avatar overlay. It should be able to:

- Sit on screen as a floating, personality-driven VRM avatar
- Hold real conversations — by typed chat and by voice, with spoken responses
- Manage files on the user's machine safely (organize, search, move)
- Act as a coding agent by driving CLI agent tools (Claude Code, aider, etc.)

## 2. Scope for v1

**In scope:**
- Floating transparent, always-on-top avatar window with idle motion and expression presets
- Text chat with streaming responses
- Voice in/out using cloud STT/TTS (provider-agnostic, swappable)
- Sandboxed file operations (list/search/move/rename) with human-in-the-loop confirmation for anything destructive
- One CLI coding agent integration, driven via subprocess

**Explicitly out of scope for v1, revisit later:**
- Local/offline LLM, STT, or TTS models — cloud-only to start, to avoid bundling multi-GB model weights
- A dedicated Go/Rust performance service — add only once Python is a measured bottleneck
- Multi-agent or multi-CLI-tool orchestration

## 3. High-Level Architecture

Three components, three languages, each picked for what it's actually good at:

- **Tauri shell (Rust)** — owns the window: transparency, always-on-top, click-through, tray icon, global hotkeys, autostart. Also launches and supervises the Python backend as a sidecar process.
- **Frontend (React + TypeScript + Three.js + @pixiv/three-vrm)** — renders the avatar and chat UI inside the Tauri webview. Talks to the Rust shell via Tauri's `invoke` IPC for OS-level actions (window control, dialogs, tray), and to the Python backend via WebSocket for everything AI- and voice-related.
- **Python backend** — the "brain." Runs the LLM tool-calling loop, holds persona and memory state, runs the voice pipeline, and executes file/agent tools.

Communication summary:
- Frontend ↔ Python: WebSocket (needed for bidirectional streaming — LLM tokens, audio chunks, interrupt signals)
- Frontend ↔ Rust shell: Tauri IPC (`invoke`)
- Python ↔ future Go/Rust service: gRPC or local HTTP, only if/when that service exists

## 4. Why these choices

| Decision | Why | Alternative considered |
|---|---|---|
| Tauri over Electron | Native transparent / click-through / always-on-top windows, smaller binary, lighter idle RAM | Electron — larger ecosystem for OS edge cases, heavier footprint |
| @pixiv/three-vrm for the avatar | The mature, actively maintained standard for VRM-in-web; no equivalent VRM ecosystem exists elsewhere | Native Rust avatar renderer — no VRM tooling maturity in Rust |
| Python for the AI orchestrator | The entire mature LLM/audio ecosystem (SDKs, STT, TTS, RAG) lives here first | Go/Rust orchestrator — would mean reimplementing AI tooling that doesn't natively exist there |
| Cloud APIs for LLM/STT/TTS in v1 | Keeps the Python sidecar thin, avoids bundling multi-GB model weights — the #1 distribution risk for this stack | Local models (Whisper, Kokoro, Piper, etc.) — revisit as an opt-in "offline mode" later |
| WebSocket for frontend ↔ Python | Bidirectional streaming for LLM tokens, audio chunks, interrupt signals | REST polling — too slow for real-time voice |
| File ops live in Python for v1, no separate service | Fewer moving parts; Python stdlib + `watchdog` is enough until proven otherwise | Dedicated Rust/Go file service — add only if profiling shows Python is the bottleneck |

## 5. Voice Pipeline

Flow: mic → voice activity detection → STT (streaming) → LLM (streaming) → TTS (streaming) → playback + lip-sync.

- **STT**: cloud-first for v1. Local fallback candidates if we go offline later: Whisper Large V3 Turbo (multilingual), Parakeet TDT (fastest streaming, English-strong).
- **TTS**: cloud-first for v1. Local fallback candidates: Kokoro, Chatterbox-Turbo, Piper.
- **VAD**: `silero-vad` to detect when the user starts/stops talking.
- **Lip-sync v1**: raw audio amplitude (RMS) driving the VRM mouth blendshape directly in the frontend — no extra dependency needed.
- **Lip-sync v2**: phoneme/viseme timing from the TTS provider, if it exposes timestamps.

## 6. Personality & Expression System

- LLM responses carry a structured side-channel indicating emotional state, e.g. `{ "expression": "happy", "text": "..." }`.
- Frontend maps `expression` to VRM's built-in expression presets (happy, angry, sad, surprised, relaxed), blended with an idle motion loop.
- Persona/system prompt and short-term conversation history live in Python; long-term memory backed by SQLite (structured state) plus a lightweight vector store (Chroma or LanceDB) for semantic recall.

## 7. File Management & Coding Agent Tools

Implemented as standard agentic tools the LLM can call: `list_files`, `search_files`, `move_file`, `run_coding_agent`, and similar.

Guardrails, built in from the start rather than retrofitted:
- Sandbox all file ops to a configurable root directory — never whole-filesystem access by default
- Trash instead of permanent delete; keep an undo log
- Human-in-the-loop confirmation before any destructive op or shell command the LLM wants to run
- Allowlist of binaries the agent may spawn — never let the LLM exec arbitrary processes

Coding agent integration: Python spawns the CLI tool (Claude Code, aider, etc.) via `asyncio.subprocess`, streams stdout/stderr back through the LLM loop and into the chat UI.

## 8. Data Storage

- **SQLite** — conversation history, persona/settings, file-op audit log
- **Chroma or LanceDB** — embeddings for memory/RAG and "chat with your files"
- **Local app data directory** — VRM model files and motion clips

## 9. Packaging & Distribution Risk

The Python sidecar needs to be frozen (PyInstaller or Nuitka) to ship inside the Tauri bundle. This is the single biggest distribution risk in this stack, and it gets worse if local model weights are ever bundled. Mitigation: stay cloud-API-first as long as possible, and treat a local-model "offline mode" as a deliberately separate, larger download — not the default install.

## 10. Phased Roadmap

- **Phase 0 — Scaffold** (done): Tauri + React + TS shell, core frontend dependencies installed
- **Phase 1 — Avatar alive**: load a VRM model, render in a transparent floating window, idle motion and blink loop
- **Phase 2 — Chat loop**: Python backend running, WebSocket connected, basic LLM chat with no voice yet
- **Phase 3 — Voice**: STT/TTS pipeline wired in, lip-sync v1
- **Phase 4 — File tools**: sandboxed file management tools with confirmation UI
- **Phase 5 — Coding agent**: CLI agent subprocess integration
- **Phase 6 — Performance pass**: only if needed — a Go or Rust service for heavy indexing or hardened sandboxing

## 11. Open Decisions

- [ ] Final LLM / STT / TTS provider choices for v1 — cost vs. latency vs. quality
- [ ] Go vs. Rust for the eventual performance service — both fit, team preference decides
- [ ] Which CLI coding agent to integrate first
- [ ] License for the repo
