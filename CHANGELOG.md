# Changelog

All notable changes to this project are documented here. Versioning follows
[Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`): MAJOR bumps
mark breaking config-format/behavior changes, MINOR marks backward-compatible
feature additions, PATCH marks fixes.

## [1.3.3] - 2026-09-10

### Added
- **Cross-platform CurseForge build** — `src/executable_builder.py` now
  also builds the `TS4_x64` CurseForge pre-launch executable on macOS/Linux
  (using `assets/alt_icon.icns` on macOS), instead of skipping it outside
  Windows. The name mirrors Sims 4's own game executable on each platform.
- **Fully unattended generation** — `src/package_generator.py` no longer
  blocks on the final "press any key to close" prompt when invoked via
  `--generate` (as `Launcher.bat`/`Launcher.sh --generate` and the built
  executables all do) and `launch_game` is off, so it can run with zero
  input from scripts, other launchers, or CI.

### Changed
- **`assets/logo.png`** — regenerated from the same higher-resolution icon
  source as the Steam artwork, for a crisper README header logo.

## [1.3.2] - 2026-09-10

### Changed
- **`assets/steam/background*.png`** — the library hero is now a text-free
  background made of a scattered pattern of the app icon (or `alt_icon` for
  the `_alt` variant), since Steam draws the logo/title over the hero
  separately; it no longer duplicates the "SIMS 4 / RANDOM LOADING SCREENS"
  wordmark itself.
- **`assets/steam/cover*.png`, `wide_cover*.png`** — now use the same
  scattered icon pattern as their background, behind the existing
  icon/title/subtitle artwork, instead of a plain gradient.

## [1.3.1] - 2026-09-10

### Removed
- **`assets/steam/small_capsule.png`** — dropped from the Steam artwork set
  (unused Steam library slot).

## [1.3.0] - 2026-09-10

### Added
- **`STEAM_GUIDE.md`** — explains the `assets/steam/` artwork set and how to
  apply it to a non-Steam-game shortcut, linking to a community walkthrough.
- **`assets/steam/*_alt.png`** — CurseForge-branded (`alt_icon`) counterpart
  of every Steam artwork asset (`cover_alt.png`, `wide_cover_alt.png`,
  `background_alt.png`, `logo_alt.png`), for the `TS4_x64.exe` shortcut.

### Changed
- **`assets/steam/`** — the Steam artwork set now lives in its own
  subfolder instead of loose `steam_*.png` files at the top of `assets/`,
  and is generated at Steam's actual current library grid resolutions
  instead of half-size placeholders: `cover.png` (600×900, was
  `steam_cover.png` at the same size), `wide_cover.png` (920×430, was
  `steam_header.png` at 460×215), `background.png` (3840×1240, was
  `steam_hero.png` at 1920×620), `logo.png` (1280×720, was `steam_logo.png`
  at 640×360). `steam_small.png` moved to `small_capsule.png` unchanged.

### Fixed
- **`assets/alt_icon.ico`** had an opaque white background instead of a
  transparent one (inconsistent with `icon.ico` and with `alt_icon.png`/
  `alt_icon.icns`, which were already transparent) — regenerated from
  `alt_icon.icns` with alpha preserved.

## [1.2.0] - 2026-09-10

### Added
- **`Launcher.bat` / `Launcher.sh`** — a new interactive CLI at the project
  root (generate a loading screen, rename images, build the executable(s),
  or run the test suite) that also displays the current version from
  `VERSION.md`. Replaces the old single-purpose `Sims4_RLS_Launcher.bat`.
  Pass `--generate [--force-launch]` to skip the menu and generate
  directly — this is how `Launcher.exe`/`TS4_x64.exe` invoke it.
- **Cross-platform builds** — `src/executable_builder.py` now also builds a
  native `Launcher` executable on macOS/Linux (calling `Launcher.sh`), using
  `assets/icon.icns` on macOS. PyInstaller can't cross-compile, so build on
  each platform you want a native executable for. The `TS4_x64.exe`
  CurseForge variant stays Windows-only and is skipped elsewhere.
- **Console banners** — `src/package_generator.py`, `src/images_renamer.py`,
  and `src/executable_builder.py` each print a titled banner (script name,
  current version, "Built & Maintained by StuxieDev") on run, matching the
  `Launcher.bat`/`Launcher.sh` CLI header style.
- **`assets/icon.icns`, `assets/alt_icon.icns`** — macOS icon equivalents of
  the existing `.ico` files.
- **`assets/steam_hero.png`, `steam_logo.png`, `steam_header.png`,
  `steam_small.png`** — the rest of the standard Steam artwork set (hero
  banner, transparent logo overlay, header capsule, small capsule) to go
  with `steam_cover.png`.

### Changed
- **`src/` layout** — `Sims4_RLS_Creator.py`, `Sims4_RLS_ExeBuilder.py`, and
  `Sims4_RLS_ImagesRenamer.py` moved into `src/` and renamed to
  `package_generator.py`, `executable_builder.py`, and `images_renamer.py`.
- **`Sims4_RLS_Launcher.exe` renamed to `Launcher.exe`** (the CurseForge
  variant stays `TS4_x64.exe`).
- **`requirements-dev.txt` renamed to `requirements.txt`.**

### Fixed
- `.gitignore` now also ignores `.pytest_cache/`, and `__pycache__/` is
  anchored with a trailing slash.

## [1.1.0] - 2026-09-10

### Added
- **`assets/steam_cover.png`** — a 600×900 vertical cover image for use as
  the Steam library capsule artwork on the non-Steam-game shortcut.

### Changed
- **`TS4_x64.exe` now uses a distinct icon** (`assets/alt_icon.ico`) from
  `Sims4_RLS_Launcher.exe` (`assets/icon.ico`), instead of both exes
  sharing the same icon.
- Retired the `.DONOTRENAME_DONOTREMOVE/` folder — the build-time icons
  and the loading-screen `.package` template it held now live in
  `assets/` (`icon.ico`, `alt_icon.ico`, `alt_icon.png`,
  `template.package`) alongside the rest of the project's artwork.

## [1.0.1] - 2026-09-08

### Changed
- Footer's attribution line reformatted from "Written by" to "Built & Maintained by", matching Automater's standard StuxieDev footer wording

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
