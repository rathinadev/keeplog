# keeplog

[![CI](https://github.com/rathinadev/keeplog/actions/workflows/python-app.yml/badge.svg)](https://github.com/rathinadev/keeplog/actions/workflows/python-app.yml)
[![PyPI](https://img.shields.io/pypi/v/keeplog)](https://pypi.org/project/keeplog/)
[![Python](https://img.shields.io/pypi/pyversions/keeplog?cacheSeconds=0)](https://pypi.org/project/keeplog/)
[![License](https://img.shields.io/pypi/l/keeplog)](https://github.com/rathinadev/keeplog/blob/main/LICENSE)

**Search what your terminal printed, not just what you typed.**

Most shell-history tools (Atuin, hishtory) only save the *command*. keeplog records the full output too, via a PTY, and indexes it. So `keeplog search postgres` finds the `docker ps` you ran last week, because "postgres" appeared in what it printed.

![keeplog demo](https://github.com/rathinadev/keeplog/raw/main/docs/assets/demo.gif)

```bash
pip install keeplog
keeplog setup   # auto-start on every terminal
# restart your terminal — it's already recording
```

## Features

- **PTY capture** — records full output, not just commands
- **SQLite + FTS5** — instant full-text search across commands, directories, and output
- **fzf integration** — interactive fuzzy search with preview
- **Zero config** — install and forget, always running in background
- **Two modes** — full (capture output) or light (metadata only)
- **Lightweight** — no servers, no cloud, no dependencies
- **Cross-platform** — macOS + Linux, zsh + bash + fish

## Install

```bash
pip install keeplog
```

Or with Homebrew (macOS/Linux):

```bash
brew tap rathinadev/keeplog https://github.com/rathinadev/keeplog
brew trust rathinadev/keeplog   # Homebrew 7+ asks you to trust third-party taps once
brew install keeplog
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

# Set up auto-start (adds to .zshrc/.bashrc/config.fish)
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

## Shell Support

keeplog auto-detects your shell (`$SHELL`) and installs the matching hook:

- **zsh** — via `ZDOTDIR` + `preexec`/`precmd`
- **bash** — via `PROMPT_COMMAND` + the `DEBUG` trap
- **fish** — via `fish_preexec`/`fish_postexec` events

It works inside **tmux** and **screen**: each pane gets its own terminal, so each pane is recorded as its own session.

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
4. Output is stripped of ANSI escape codes and saved to **SQLite with FTS5**. Full-screen apps (vim, less, htop, tmux itself) are skipped, since what they draw isn't useful as text
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

The database and config file are created with `0600` permissions (owner read/write only).

## Privacy & Security

In **full mode** (the default), keeplog records everything that appears in your terminal — including anything you type or that gets printed back, unfiltered. That means:

- Passwords typed at interactive prompts, API keys, tokens, and secrets pasted or echoed to the terminal **will be saved in plaintext** in `logs.db`.
- `keeplog export` dumps this data as JSON with no redaction.
- Anyone with read access to your user account can read `logs.db` directly with `sqlite3`.

If this matters to you:

- Use `keeplog config mode light` to record only the command, directory, exit code, and timestamp — no output — for a safer default.
- Set a shorter `retention_days` so sensitive data doesn't linger (`keeplog config retention_days 7`).
- Avoid running secrets-handling commands while a `full`-mode session is active, or switch to `light` mode first.

keeplog does not send data anywhere — everything stays in your local SQLite file — but it does not currently redact secrets on your behalf.

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
