#!/usr/bin/env bash
set -euo pipefail

REPO="rathinadev/keeplog"

echo "==> Installing keeplog..."

if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 is required. Install it first:"
    echo "  macOS: brew install python"
    echo "  Linux: apt install python3 python3-pip"
    exit 1
fi

if ! command -v pip3 &>/dev/null && ! python3 -m pip --version &>/dev/null; then
    echo "ERROR: pip is required."
    exit 1
fi

python3 -m pip install --quiet --upgrade keeplog 2>/dev/null || {
    echo "==> Installing from source..."
    TMPDIR=$(mktemp -d)
    cd "$TMPDIR"
    curl -fsSL "https://github.com/$REPO/archive/main.tar.gz" | tar xz --strip=1
    python3 -m pip install --quiet -e .
    cd /
    rm -rf "$TMPDIR"
}

echo "==> Initializing database..."
python3 -m keeplog init

echo "==> Adding to shell rc..."
python3 -m keeplog install

echo ""
echo "Done! Restart your terminal or run: source ~/.zshrc"
