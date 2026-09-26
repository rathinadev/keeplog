---
description: How to record terminal sessions, search command history, and browse past output with keeplog.
---

# Usage

## Record a Session

```bash
keeplog record
```

This spawns your shell inside a pseudo-terminal and records everything. Type commands normally, then `exit` when done.

## Search

Search matches the command, the directory it ran in, and everything it printed (in `full` mode).

```bash
# Interactive fzf search
keeplog search docker

# Matches output too: finds the `docker ps` whose output listed a postgres container
keeplog search postgres

# Without fzf, it falls back to a list
keeplog search "npm install"
```

## Browse

```bash
# Recent commands
keeplog recent

# Full details of a specific command
keeplog get 1
```

## Stats

```bash
keeplog status
```

## Auto-start

```bash
keeplog setup
```

Adds a hook to your `.zshrc`/`.bashrc`/`config.fish` so every terminal starts recording automatically.
