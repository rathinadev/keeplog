# Changelog

All notable changes to this project are documented here.
This project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- `keeplog search` now matches command output, not just the command and directory
- Existing databases are indexed automatically the first time keeplog opens them (about 0.5s for a 140 MB database)
- Homebrew formula: `brew tap rathinadev/keeplog https://github.com/rathinadev/keeplog && brew install keeplog`

## [1.0.0] - 2026-08-08

### Added
- Fish shell support (`fish_preexec`/`fish_postexec` hooks)
- Per-page SEO metadata, `robots.txt`, and social card generation for the docs site
- Structured data (`SoftwareApplication`) on the docs homepage
- `CONTRIBUTING.md` and this changelog

### Changed
- CI now tests macOS + Linux across Python 3.9, 3.10, and 3.11 (previously Ubuntu/3.10 only)

### Fixed
- **`keeplog clear` crashed with `UnboundLocalError` every time it was run** — a redundant local import of `clear_old` inside the `record` branch shadowed the module-level import for the whole function
- `logs.db` and `config.json` are now created with `0600` permissions instead of default umask permissions
- Corrected a `keeplog` typo in the docs quick-start example
- Added the `favicon.png` referenced by the docs site (was missing)

### Security
- Documented that `full` capture mode records terminal output unfiltered, including secrets — see the README's "Privacy & Security" section

## [0.1.1] - 2026-06-27
- Added Python version classifiers, tests, and README badges

## [0.1.0] - 2026-06-27
- Initial release: PTY-based session capture, SQLite + FTS5 storage, fzf search, zsh/bash shell hooks, auto-start setup
