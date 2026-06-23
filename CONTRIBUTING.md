# Contributing to Sora

Found a bug? Got an idea? Want to help build a desktop companion that's more than just a chat window? PRs are welcome.

## Before you start

- Check open issues first — someone might already be on it
- For bigger changes, open an issue to discuss before diving into code, so nobody's wasting time

## Setup

```bash
npm install
npm run tauri dev
```

Needs Rust + Tauri's CLI prerequisites — see Tauri's official setup guide for your OS.

## Making a PR

1. Fork the repo, branch off `main`
2. Keep commits focused — one logical change per PR is easier to review
3. Open the PR with a short description of what and why

## Code style

- TypeScript/React: stay consistent with what's already there
- Rust: run `cargo fmt` before committing
- Python (once the backend lands): `black` + type hints where it matters

No CLA, no bureaucracy. Just be reasonable and respectful in issues and PRs.
