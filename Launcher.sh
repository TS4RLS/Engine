#!/bin/bash
# Dev launcher for running this project from source (contributors).
# End users should use the built TS4RLS/TS4_x64 executable instead
# (see src/build/executable_builder.py, dist/ once built). Pass
# --generate here to skip straight to generating a loading screen, e.g.:
#   ./Launcher.sh --generate

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="$(tr -d '[:space:]' < "$ROOT/VERSION.md")"

# ── Colors (ANSI; no-ops when not attached to a terminal) ───────────────
if [ -t 1 ]; then
    C_RESET='\033[0m'
    C_RED='\033[0;91m'
    C_GREEN='\033[0;92m'
    C_YELLOW='\033[0;93m'
    C_CYAN='\033[0;96m'
    C_BOLD='\033[1m'
else
    C_RESET=''; C_RED=''; C_GREEN=''; C_YELLOW=''; C_CYAN=''; C_BOLD=''
fi

# ── Locate Python ────────────────────────────────────────────────────────
PYTHON=""
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    printf "%b[ERROR] Python is not installed or not on your PATH.%b\n" "$C_RED" "$C_RESET"
    echo "Download Python from: https://www.python.org/downloads/"
    exit 1
fi

if ! "$PYTHON" --version >/dev/null 2>&1; then
    printf "%b[ERROR] Found a \"%s\" command, but it failed to run.%b\n" "$C_RED" "$PYTHON" "$C_RESET"
    exit 1
fi

# ── Ensure pip is available, bootstrapping it if needed ──────────────────
if ! "$PYTHON" -m pip --version >/dev/null 2>&1; then
    printf "%bpip not found — bootstrapping it...%b\n" "$C_YELLOW" "$C_RESET"
    if ! "$PYTHON" -m ensurepip --upgrade >/dev/null 2>&1; then
        printf "%b[ERROR] Could not install pip automatically.%b\n" "$C_RED" "$C_RESET"
        echo "Reinstall Python from https://www.python.org/downloads/ with pip included."
        exit 1
    fi
    printf "%bpip installed.%b\n\n" "$C_GREEN" "$C_RESET"
fi

# ── Ensure Pillow is available ────────────────────────────────────────────
if ! "$PYTHON" -c "import PIL" >/dev/null 2>&1; then
    printf "%bPillow not found — installing...%b\n" "$C_YELLOW" "$C_RESET"
    if ! "$PYTHON" -m pip install Pillow --quiet; then
        printf "%b[ERROR] Failed to install Pillow. Check your internet connection and try:%b\n" "$C_RED" "$C_RESET"
        echo "  $PYTHON -m pip install Pillow"
        exit 1
    fi
    printf "%bPillow installed.%b\n\n" "$C_GREEN" "$C_RESET"
fi

# ── Ensure sv_ttk is available ─────────────────────────────────────────────
if ! "$PYTHON" -c "import sv_ttk" >/dev/null 2>&1; then
    printf "%bsv_ttk not found — installing...%b\n" "$C_YELLOW" "$C_RESET"
    if ! "$PYTHON" -m pip install sv_ttk --quiet; then
        printf "%b[ERROR] Failed to install sv_ttk. Check your internet connection and try:%b\n" "$C_RED" "$C_RESET"
        echo "  $PYTHON -m pip install sv_ttk"
        exit 1
    fi
    printf "%bsv_ttk installed.%b\n\n" "$C_GREEN" "$C_RESET"
fi

if [ "$1" = "--generate" ]; then
    "$PYTHON" "$ROOT/gui.py" "$@"
    status=$?
    if [ $status -ne 0 ]; then
        printf "\n%b[ERROR] Something went wrong. See message above.%b\n" "$C_RED" "$C_RESET"
    fi
    exit $status
fi

pause() {
    read -rp "Press Enter to continue..." _
}

menu() {
    echo
    printf "%b---------------------------------------------------------------------%b\n" "$C_CYAN" "$C_RESET"
    printf "%b          TS4RLS - The Sims 4 Random Loading Screen - Dev Launcher%b\n" "$C_BOLD" "$C_RESET"
    echo "                               v$VERSION"
    echo "                     Built & Maintained by StuxieDev"
    printf "%b---------------------------------------------------------------------%b\n" "$C_CYAN" "$C_RESET"
    echo
    printf "      %b1)%b Launch the GUI\n" "$C_GREEN" "$C_RESET"
    printf "      %b2)%b Build launcher executable(s)\n" "$C_GREEN" "$C_RESET"
    printf "      %b3)%b Run test suite\n" "$C_GREEN" "$C_RESET"
    printf "      %b4)%b Exit\n" "$C_GREEN" "$C_RESET"
    echo
    read -rp "    Select an option [1-4]: " choice

    case "$choice" in
        1)
            "$PYTHON" "$ROOT/gui.py"
            [ $? -ne 0 ] && printf "%b[ERROR] Something went wrong — see message above.%b\n" "$C_RED" "$C_RESET"
            menu
            ;;
        2)
            "$PYTHON" "$ROOT/src/build/executable_builder.py"
            [ $? -ne 0 ] && printf "%b[ERROR] Build failed — see message above.%b\n" "$C_RED" "$C_RESET"
            echo
            pause
            menu
            ;;
        3)
            if ! "$PYTHON" -c "import pytest" >/dev/null 2>&1; then
                printf "%bpytest not found — installing...%b\n" "$C_YELLOW" "$C_RESET"
                if ! "$PYTHON" -m pip install -r "$ROOT/requirements.txt" --quiet; then
                    printf "%b[ERROR] Failed to install test dependencies.%b\n" "$C_RED" "$C_RESET"
                    echo
                    pause
                    menu
                    return
                fi
            fi
            (cd "$ROOT" && "$PYTHON" -m pytest -v)
            [ $? -ne 0 ] && printf "%b[ERROR] Some tests failed — see output above.%b\n" "$C_RED" "$C_RESET"
            echo
            pause
            menu
            ;;
        4)
            exit 0
            ;;
        *)
            echo
            printf "%bInvalid option. Please choose 1-4.%b\n" "$C_RED" "$C_RESET"
            menu
            ;;
    esac
}

menu
