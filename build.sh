#!/usr/bin/env bash
# TS4RLS - build the executable
# Thin wrapper so `./build.sh` matches the sibling `commit.sh`, rather than
# needing to remember the full module path. Dependencies (Pillow, sv_ttk,
# PyInstaller) are installed automatically by executable_builder.py itself.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$DIR/src/build/executable_builder.py" "$@"
