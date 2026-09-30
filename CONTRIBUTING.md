# Contributing to keeplog

Thanks for considering a contribution. keeplog is a small, dependency-free CLI tool — keep changes focused and in that spirit.

## Setup

```bash
git clone https://github.com/rathinadev/keeplog
cd keeplog
pip install -e ".[dev]"
python -m pytest tests/
```

## Guidelines

- **No new runtime dependencies** unless there's a strong reason — keeplog's "no dependencies" promise is a feature.
- **Cross-platform**: code must work on both macOS and Linux, and across zsh, bash, and fish. If you touch shell-hook logic (`src/keeplog/hooks/`), test it in the shell you changed.
- **Tests**: add or update tests under `tests/` for any behavior change. CI runs on macOS + Linux across Python 3.9–3.14, plus the upcoming 3.15 as an early-warning check that doesn't block merges.
- **Small commits**: one logical change per commit, with a clear message. Unrelated changes go in separate commits/PRs.
- **Lint**: `flake8` runs in CI with a relaxed `max-line-length=127`; keep it passing.

## Reporting issues

Open a GitHub issue with:
- Your OS, shell, and Python version
- Steps to reproduce
- What you expected vs. what happened

## Security issues

Please don't open a public issue for security-sensitive reports (e.g. anything related to secret capture or credential exposure). See `SECURITY.md` for how to report privately.

## Pull requests

1. Fork, branch off `main`
2. Make your change with tests
3. Ensure `python -m pytest tests/` and `flake8` pass locally
4. Open a PR describing the change and why

## License

By contributing, you agree your contributions are licensed under the project's [MIT License](LICENSE).
