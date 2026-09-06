# Changelog

All notable changes to this project are documented here. Versioning follows
[Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`): MAJOR bumps
mark breaking config-format/behavior changes, MINOR marks backward-compatible
feature additions, PATCH marks fixes.

## [1.0.0] - 2026-09-06
### Added
- **`LICENSE.md`** — the project is now formally licensed (closed-source,
  all rights reserved; see [LICENSE.md](LICENSE.md)).
- **Automated test suite (`pytest`)** — `tests/` covers the pure-logic
  parts of the three scripts: image discovery, resizing/centre-crop, ARGB
  packing, `.package` template splicing, config parsing, and file
  renaming, all run against temporary directories. No test touches your
  real `config.json`, images, Mods folder, or the game itself. See
  [CONTRIBUTING.md](CONTRIBUTING.md).
- **`requirements-dev.txt`** (`pytest`, `Pillow`) for running the test
  suite locally.
- **GitHub Actions CI** (`.github/workflows/ci.yml`) runs the test suite
  on every push and pull request.
- **`assets/`** (`icon.ico`, `icon.png`, `logo.png`) for the project's
  icon/logo artwork.
- **README "Testing" section** documenting how to install dev
  dependencies and run the suite.

## [0.7.0] - 2026-06-07
### Added
- **CurseForge distribution support** — a `.curseclient` marker file
  identifies the CurseForge-distributed build, and the launcher now
  forces the game to launch for that build variant regardless of the
  `launch_game` setting.

## [0.6.0] - 2026-06-07
### Added
- **Command-line argument support** in the launcher, plus configurable
  game-launch behavior driven by `config.json` (`launch_game`,
  `launch_via_steam`, `game_exe`), so launching Sims 4 after generating
  the loading screen — and how — is now optional and configurable
  instead of hardcoded.

### Changed
- **Dependency auto-install checks** — the launcher now checks for
  Pillow and PyInstaller and installs them automatically if missing,
  instead of failing with an import error.
- Internal refactor of the launcher/creator code for readability and
  maintainability; no user-facing behavior change.

## [0.4.0] - 2026-06-06
### Added
- **Launch message** printed after generating the loading screen, for
  clearer user feedback on what happened.
- **Countdown before closing**, and a clearer exit message, in the
  launcher script.

### Fixed
- **Template package name** in error messages and path configuration
  (error text and path handling now correctly reference the template
  `.package` file).

## [0.3.0] - 2026-06-06
### Added
- **`Sims4_RLS_ImagesRenamer.py`** — renames every image in
  `images_folder` to a random 32-character alphanumeric name and
  converts it to JPEG, either as part of a normal run (`rename_files`
  in config) or standalone.

## [0.2.0] - 2026-06-06
### Added
- **Custom `.exe` icon support** in `Sims4_RLS_ExeBuilder.py` — PNG-to-ICO
  conversion, with the icon read from
  `.DONOTRENAME_DONOTREMOVE/ExeIcon_DONOTRENAME_DONOTREMOVE.ico` and
  embedded into the built executable.

## [0.1.0] - 2026-06-06
### Added
- Initial release: `Sims4_RLS_Creator.py` picks a random image (or two,
  in vertical mode) from `images_folder`, resizes/centre-crops it, and
  splices it into the DBPF `.package` loading-screen template, writing
  `RandomLoadingScreen.package` to the Sims 4 Mods folder.
- `Sims4_RLS_Launcher.bat` to run the generator with one double-click.
- `Sims4_RLS_ExeBuilder.py` to package the launcher as a standalone
  `.exe` via PyInstaller, for adding the tool to Steam as a non-Steam
  game.
- `config.example.json` template and `config.json` (gitignored) for
  `images_folder`/`mods_folder` and the `is_vertical` option.
