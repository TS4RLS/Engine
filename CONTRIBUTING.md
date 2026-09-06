<p align="center">
  <img src="assets/logo.png" width="500" alt="Sims 4 Random Loading Screen">
</p>

# Contributing to Sims 4 Random Loading Screen

Personal tool for generating a randomized Sims 4 loading screen mod.

## Getting set up

1. Python 3.6+
2. `pip install -r requirements-dev.txt` (installs `pytest` and `Pillow`;
   `Pillow` and `PyInstaller` are also installed automatically on first
   run of the launcher/exe builder if missing)
3. Copy `config.example.json` to `config.json` and fill in
   `images_folder`/`mods_folder` — see the [README](README.md) for the
   full option list.

## Making a change

Run the automated test suite before opening a PR:

```
pytest -v
```

`tests/` covers the pure logic in all three scripts — image discovery,
resizing/centre-crop, ARGB packing, `.package` template splicing, config
parsing, and file renaming — using temporary directories. No test touches
your real `config.json`, images, Mods folder, or the game itself. CI
(`.github/workflows/ci.yml`) runs the same suite on every push and pull
request.

For anything the test suite doesn't cover (the actual `.package` output
loading correctly in-game, the `.exe` build, launch-via-Steam behavior),
verify manually:

- Run `Sims4_RLS_Creator.py` (or the launcher) against a real
  `images_folder`/`mods_folder` and confirm the loading screen changes
  in-game.
- If you touched `Sims4_RLS_ExeBuilder.py`, rebuild the executable
  locally (`python Sims4_RLS_ExeBuilder.py`) and confirm
  `Sims4_RLS_Launcher.exe` still launches and produces the same result
  as running the `.bat`/`.py` directly.
- If you touched launch behavior (`launch_game`, `launch_via_steam`,
  `game_exe`, CurseForge/`.curseclient` handling), confirm both the
  Steam and direct-exe launch paths still behave as configured.

## Versioning

Every user-facing change should bump [`VERSION.md`](VERSION.md) and add a
matching entry to [`CHANGELOG.md`](CHANGELOG.md) in the same PR, following
[Semantic Versioning](https://semver.org/): MAJOR for breaking
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

Open an issue with your OS, Python version (if not using the `.exe`), your
`config.json` (with paths redacted if needed), and what you expected vs.
what happened.

## License

This project is closed-source; see [LICENSE.md](LICENSE.md). No license is
granted to third parties by default, and pull requests are accepted at the
author's discretion — by submitting one, you agree your contribution may
be used under the same terms as the rest of the project.
