#!/bin/bash
# Sims 4 Random Loading Screen - Interactive CLI for this project.
#
# Double-click/run to open the menu, or pass --generate (mirroring
# Launcher.bat, used by the Windows .exe builds) to skip straight to
# generating a loading screen, e.g.:
#   ./Launcher.sh --generate [--force-launch]

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="$(tr -d '[:space:]' < "$ROOT/VERSION.md")"

PYTHON=""
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "[ERROR] Python is not installed or not on your PATH."
    echo "Download Python from: https://www.python.org/downloads/"
    exit 1
fi

if ! "$PYTHON" -c "import PIL" >/dev/null 2>&1; then
    echo "Pillow not found — installing..."
    "$PYTHON" -m pip install Pillow --quiet
    echo "Pillow installed."
    echo
fi

if [ "$1" = "--generate" ]; then
    "$PYTHON" "$ROOT/src/package_generator.py" "$@"
    exit $?
fi

pause() {
    read -rp "Press Enter to continue..." _
}

menu() {
    echo
    echo "---------------------------------------------------------------------"
    echo "          Sims 4 Random Loading Screen - Interactive Launcher"
    echo "                               v$VERSION"
    echo "                     Built & Maintained by StuxieDev"
    echo "---------------------------------------------------------------------"
    echo
    echo "      1) Generate loading screen (and launch game if configured)"
    echo "      2) Rename images only"
    echo "      3) Build launcher .exe(s)"
    echo "      4) Run test suite"
    echo "      5) Exit"
    echo
    read -rp "    Select an option [1-5]: " choice

    case "$choice" in
        1)
            "$PYTHON" "$ROOT/src/package_generator.py"
            echo
            pause
            menu
            ;;
        2)
            "$PYTHON" "$ROOT/src/images_renamer.py"
            echo
            pause
            menu
            ;;
        3)
            "$PYTHON" "$ROOT/src/executable_builder.py"
            echo
            pause
            menu
            ;;
        4)
            (cd "$ROOT" && "$PYTHON" -m pytest -v)
            echo
            pause
            menu
            ;;
        5)
            exit 0
            ;;
        *)
            echo
            echo "Invalid option. Please choose 1-5."
            menu
            ;;
    esac
}

menu
