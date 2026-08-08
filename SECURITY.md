# Security Policy

## Supported Versions

Only the latest released version of keeplog receives security fixes.

## Known Behavior (not a vulnerability report)

keeplog's `full` capture mode records terminal output unfiltered, including any secrets typed or printed in your shell (passwords, API keys, tokens). This is documented, expected behavior — see the [README's Privacy & Security section](README.md#privacy--security) — not something to report as a bug. If you want to reduce this exposure, use `keeplog config mode light` or a shorter `retention_days`.

## Reporting a Vulnerability

If you find an actual security vulnerability (e.g. a way for another local user to read data they shouldn't, a bug that leaks data outside the local machine, or an injection issue in the shell hooks), please report it privately rather than opening a public issue:

- Use [GitHub's private vulnerability reporting](https://github.com/rathinadev/keeplog/security/advisories/new) for the repo, or
- Open a draft security advisory

Please include steps to reproduce, your OS/shell/Python version, and the potential impact. We'll acknowledge reports as soon as possible and credit reporters in the changelog unless you'd prefer to stay anonymous.
