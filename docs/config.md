# Configuration

```bash
# Set mode to light (metadata only, no output)
keeplog config mode light

# Set retention to 7 days
keeplog config retention_days 7

# View current config
keeplog config
```

## Config File Location

- **macOS:** `~/Library/Application Support/keeplog/config.json`
- **Linux:** `~/.config/keeplog/config.json`

## Options

| Key | Default | Description |
|-----|---------|-------------|
| `mode` | `full` | Capture mode (`full` or `light`) |
| `retention_days` | `30` | Auto-delete data older than this |
