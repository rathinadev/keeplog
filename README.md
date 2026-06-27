# keeplog

**Terminal session logger with full-text search.**

Records every command + output in your terminal, saves to SQLite, and lets you search instantly.

```bash
pip install keeplog
keeplog setup   # auto-start on every terminal
# restart your terminal — it's already recording
```

## Features

- **PTY capture** — records full output, not just commands
- **SQLite + FTS5** — instant full-text search across everything
- **fzf integration** — interactive fuzzy search with preview
- **Zero config** — install and forget, always running in background
- **Two modes** — full (capture output) or light (metadata only)
- **Lightweight** — no servers, no cloud, no dependencies
- **Cross-platform** — macOS + Linux, zsh + bash

## Install

```bash
pip install keeplog
```

Or one-liner (installs pip package + sets up auto-start):

```bash
curl -fsSL https://raw.githubusercontent.com/rathinadev/keeplog/main/install.sh | sh
```

## Quick Start

```bash
# Initialize database
keeplog init

# Start recording manually
keeplog record
# (type commands, then exit)

# Set up auto-start (adds to .zshrc/.bashrc)
keeplog setup
# Restart your terminal — recording starts automatically

# Search recorded commands
keeplog search docker
keeplog search "npm install"

# Browse recent
keeplog recent
keeplog get 1    # show full output of command #1

# Stats
keeplog status
```

## Commands

| Command | Description |
|---------|-------------|
| `record` | Start recording session |
| `setup` | Add auto-start hook to shell rc |
| `remove` | Remove auto-start hook |
| `search <query>` | Interactive search (fzf if available) |
| `recent` | Show recent commands |
| `get <id>` | Show full command details + output |
| `status` | Show stats |
| `last` | Show last session |
| `export` | Export all data as JSON |
| `clear <days>` | Clear data older than N days |
| `config [key val]` | Get/set configuration |
| `init` | Initialize database |

## Configuration

```bash
# Set mode to light (metadata only, no output)
keeplog config mode light

# Set retention to 7 days
keeplog config retention_days 7

# View current config
keeplog config
```

Config file location:
- macOS: `~/Library/Application Support/keeplog/config.json`
- Linux: `~/.config/keeplog/config.json`

## How It Works

1. ``keeplog record`` spawns your shell inside a **pseudo-terminal (PTY)**
2. Every keystroke and output streams through keeplog
3. **Shell hooks** (preexec/precmd) mark command boundaries
4. Output is stripped of ANSI escape codes and saved to **SQLite with FTS5**
5. ``keeplog search`` queries the FTS index and pipes results into **fzf**

```
Terminal → keeplog record → PTY → your shell
                                ↓
                          SQLite DB → fzf search
```

## Storage

Data is stored locally — no cloud, no servers:

- macOS: `~/Library/Application Support/keeplog/logs.db`
- Linux: `~/.local/share/keeplog/logs.db`

## Uninstall

```bash
pip uninstall keeplog
keeplog remove
```

## Development

```bash
git clone https://github.com/rathinadev/keeplog
cd keeplog
pip install -e .
python -m pytest tests/
```

## License

MIT
