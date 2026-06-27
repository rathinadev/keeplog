# Usage

## Record a Session

```bash
keeplog record
```

This spawns your shell inside a pseudo-terminal and records everything. Type commands normally, then `exit` when done.

## Search

```bash
# Interactive fzf search
keeplog search docker

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

Adds a hook to your `.zshrc`/`.bashrc` so every terminal starts recording automatically.
