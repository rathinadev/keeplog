# keeplog

**Terminal session logger with full-text search.**

Records every command + output in your terminal, saves to SQLite, and lets you search instantly.

## Quick Install

```bash
pip install keeplog
keeplog setup
```

## Features

- **PTY capture** — records full output, not just commands
- **SQLite + FTS5** — instant full-text search
- **fzf integration** — interactive fuzzy search with preview
- **Zero config** — install and forget
- **Two modes** — full (capture output) or light (metadata only)
- **Cross-platform** — macOS + Linux, zsh + bash
