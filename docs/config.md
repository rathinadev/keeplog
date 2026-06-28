# Configuration

```bash
# Set mode to light (metadata only, no output)
keeplog config mode light

# Set retention to 7 days
keeplog config retention_days 7

# View current config
keeplog config
```

## Capture Modes

### Full mode (default)
Records the full terminal session via PTY — commands plus their complete output. This gives you the richest search experience since you can search not just what you typed, but what came back. Uses slightly more disk space.

### Light mode
Only records the command, directory, exit code, and timestamp — no output is captured. Lighter on disk and faster, but you lose the ability to search results. Useful if you only care about command history with context.

```bash
# Switch between modes
keeplog config mode light   # metadata only
keeplog config mode full    # full PTY capture (default)
```

## Config File Location

- **macOS:** `~/Library/Application Support/keeplog/config.json`
- **Linux:** `~/.config/keeplog/config.json`

## Options

| Key | Default | Description |
|-----|---------|-------------|
| `mode` | `full` | Capture mode (`full` or `light`) |
| `retention_days` | `30` | Auto-delete data older than this |
