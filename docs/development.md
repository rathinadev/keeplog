# Development

```bash
git clone https://github.com/rathinadev/keeplog
cd keeplog
pip install -e .
python -m pytest tests/
```

## Project Structure

```
src/keeplog/
├── cli.py              # CLI dispatcher
├── db.py               # SQLite + FTS5 storage
├── capture.py          # PTY capture loop
├── install.py          # Auto-start setup
├── search.py           # fzf integration
├── config.py           # Config file
└── hooks/
    ├── bash.sh
    └── zsh.sh
```
