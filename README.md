# Sora Project

You code with an AI all day. But it doesn't see you, hear you, or even have a face.

**Sora** is trying to fix that — a desktop AI companion that actually shows up: a floating VRM avatar with personality, a real voice, hands that can organize your files, and the ability to drive coding agents for you. Less "chatbot in a browser tab," more "someone's actually in the room with you."

**Status:** still early — frontend's scaffolded, backend's not built yet. Full architecture + reasoning in [PLAN.md](./PLAN.md) if you want the deep dive.

## What Sora actually does (or will, soon)

- **Has a face** — floats on your screen, always-on-top, see-through background, reacts with actual expressions
- **Has a voice** — talk to it, it talks back. Real speech in, real speech out, not just text bubbles
- **Has hands** — can organize, search, and move files on your machine (safely, with guardrails)
- **Has skills** — plugs into CLI coding agents (Claude Code, aider, etc.) so it can actually write code *with* you, not just about you

## Tech Stack

| Layer | Choice |
|---|---|
| Desktop shell | Tauri 2 (Rust) |
| Frontend | React + TypeScript + Vite |
| Avatar rendering | Three.js + @pixiv/three-vrm |
| State management | Zustand |
| Styling | Tailwind CSS v4 |
| AI backend | Python — WebSocket orchestrator (planned, not yet built) |
| LLM / STT / TTS | Cloud APIs for v1, provider-agnostic |

Full rationale for each choice is in [PLAN.md](./PLAN.md).

## Project Structure

```
sora-project/
├── src/                  # React + TS frontend (avatar canvas, chat UI)
├── src-tauri/            # Rust shell — window/OS integration, Tauri commands
├── backend/              # Python orchestrator (planned) — LLM, voice, memory, tools
├── PLAN.md               # Architecture & roadmap
└── README.md
```

## Getting Started

Nothing fancy running yet — just the shell.

```bash
# install dependencies
npm install

# run in dev mode
npm run tauri dev

# build
npm run tauri build
```

Needs Rust + Tauri's CLI prerequisites for your OS — check Tauri's official setup guide if you're missing pieces.

## Roadmap

- [x] Get the shell running (Tauri + React + TS)
- [x] Pull in the core deps (three, @pixiv/three-vrm, zustand, Tailwind)
- [ ] Get a VRM model actually rendering on screen
- [ ] Python backend talking to the frontend over WebSocket
- [ ] Voice in, voice out, lip-sync
- [ ] File tools, with guardrails so it doesn't go rogue on your filesystem
- [ ] Hook up a CLI coding agent
- [ ] Figure out packaging without it becoming a nightmare

Full breakdown in [PLAN.md](./PLAN.md).

## Contributing

PRs welcome — see [CONTRIBUTING.md](./CONTRIBUTING.md) for setup and ground rules.

## Author

Initiated by [Haidar](https://github.com/haidaralif-24) as a portfolio project, as well as learning how to ship a real product
## License

MIT — see [LICENSE](./LICENSE)
