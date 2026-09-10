<p align="center">
  <img src="../assets/logo.png" width="300" alt="TS4RLS — The Sims 4 Random Loading Screen">
</p>

# Contributing to TS4RLS

Personal tool for generating a randomized Sims 4 loading screen mod.

## Getting set up

1. Python 3.6+
2. `pip install -r requirements.txt` (installs `pytest`, `Pillow`, and
   `sv_ttk`; all three plus `PyInstaller` are also installed automatically
   on first run of `gui.py`/the exe builder if missing)
3. Run `python gui.py` once — the Build tab writes `config.json` for
   you. (See the [README](../README.md) for the full option list if you'd
   rather edit it by hand, or copy `config.example.json`.)

## Project layout

```
gui.py    single entry point at the repo root — the tkinter GUI (Home,
          Build, About tabs), and (--generate) a headless one-shot run.
          This is what gets compiled into the distributed executable.
src/
  common/   config_format.py (JSONC parse/dump), paths.py (config/asset
            location resolution), app_state.py (disclaimer flag + recent
            build history, kept separate from user-editable config.json)
  core/     generator.py (the actual mod generation logic), renamer.py
  cli/      cli_colors.py, config_editor.py (config.json read/write
            helpers used by the GUI and the build script)
  build/    executable_builder.py
dist/       built executables land here (gitignored) — not the repo root
```

There is no text-menu CLI — the GUI is the only interactive interface.
Run `python gui.py` from source to launch it directly; end users instead
download the executable built by `src/build/executable_builder.py`.

## Making a change

Run the automated test suite before opening a PR:

```
pytest -v
```

`tests/` covers the pure logic across `src/` — image discovery,
resizing/centre-crop, ARGB packing, `.package` template splicing, config
parsing/path resolution, and file renaming — using temporary directories
(`SIMS4_RLS_CONFIG_DIR` is redirected to a throwaway temp dir for the
whole test session; see `tests/conftest.py`). No test touches your real
`config.json`, images, Mods folder, or the game itself. CI
(`.github/workflows/ci.yml`) runs the same suite on every push and pull
request.

For anything the test suite doesn't cover (the actual `.package` output
loading correctly in-game, the executable build), verify manually:

- Run `python gui.py --generate` against a real
  `images_folder`/`mods_folder` and confirm the loading
  screen changes in-game. `python gui.py` with no args opens the GUI.
- If you touched `src/build/executable_builder.py`, rebuild the
  executable locally (`python src/build/executable_builder.py`) and
  confirm the built app in `dist/` still launches (GUI by default,
  `--generate` from a terminal) and produces the same result as running
  `gui.py` directly.

## Versioning

Every user-facing change should bump [`VERSION.md`](../VERSION.md) and add
a matching entry to [`CHANGELOG.md`](../CHANGELOG.md) in the same PR,
following [Semantic Versioning](https://semver.org/): MAJOR for breaking
config-format/behavior changes, MINOR for backward-compatible feature
additions, PATCH for fixes. Small non-user-facing changes (typo fixes,
comments) don't need a bump.

## Release flow

1. Update `CHANGELOG.md`.
2. Bump `VERSION.md`.
3. Update `README.md` if behavior changed.
4. Run `commit.bat "message"` (or `commit.sh` on POSIX) — it commits and
   tags `vX.Y.Z` from `VERSION.md`.

## Reporting a bug

Open an issue with your OS, Python version (if not using the executable),
the path shown in the app's About tab for your config file (with values
redacted if needed), and what you expected vs. what happened.

## License

TS4RLS is licensed under the [GPL-3.0-or-later](../LICENSE.md). By
contributing, you agree your contribution is licensed under the same terms.
