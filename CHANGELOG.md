# Changelog

All notable changes to this project are documented here. Versioning follows
[Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`): MAJOR bumps
mark breaking config-format/behavior changes, MINOR marks backward-compatible
feature additions, PATCH marks fixes.

## [4.1.2] - 2026-09-10

### Fixed
- `assets/logo.png` subtitle text ("The Sims 4 Random Loading Screen") is
  now the same medium green as the title instead of a lighter tint — the
  lighter tint was too washed out to read on light backgrounds, and a
  darker tint tried in between disappeared entirely on dark backgrounds
  (the website hero). This one color is the one already proven to read on
  both.

## [4.1.1] - 2026-09-10

### Changed
- README/CONTRIBUTING header logo shrunk from `width="500"` to `width="300"`.

## [4.1.0] - 2026-09-10

### Added
- **First-launch disclaimer**: a one-time modal (unofficial/independent
  tool, backs up nothing itself, "as is" — no warranty) shown before the
  main window on first run, gated by a flag in the new `app_state.json`
  (kept separate from `config.json`, which the Build tab fully overwrites
  on every save).
- **Recent build history**: every successful `src/build/executable_builder.py`
  run records the built exe's path and timestamp; the Build tab shows the
  full list (each with a **Copy path** button) and the Home tab shows the
  latest one at a glance.
- **Changelog viewer** on the About tab: renders `CHANGELOG.md` (headings,
  bullets, bold, code spans) with a **Reload** button, plus **Website**,
  **Author** (linking to stuxie.dev), and **A StuxieDev Project** (linking
  to projects.stuxie.dev) links.
- `VERSION.md`/`CHANGELOG.md`/`assets/author.png` are now bundled into the
  built executable (previously only used from source, so a shipped exe
  couldn't actually read its own version or changelog).

### Changed
- **GUI restructured into Home / Build / About tabs** (was Settings /
  Actions / About): **Home** is daily use — read-only current-settings
  display, Generate/Rename/Build buttons, the legacy-folder warning, and
  the latest-build card; **Build** is where you edit settings and build
  the executable (settings editing always available, build/test tooling
  only when running from source).

## [4.0.0] - 2026-09-10

### Changed
- **No more automatic game launching.** TS4RLS now only ever generates the
  `.package` mod and drops it into your Mods folder — it no longer offers
  to launch Sims 4 for you afterwards. The `launch_game`,
  `launch_via_steam`, and `game_exe` config keys, and the `--force-launch`
  flag, are all removed.
- **No more separate CurseForge build.** The `TS4_x64` disguise executable,
  `create_curseforge_version` config key, and `assets/icon_curseforge.*`
  are all gone — `src/build/executable_builder.py` now only builds the one
  `TS4RLS` executable.
- **Output renamed**: the generated mod is now `TS4RLS.package` in
  `Mods/TS4RLS/` (was `RandomLoadingScreen.package` in
  `Mods/RandomLoadingScreen/`). The GUI detects a leftover
  `Mods/RandomLoadingScreen` folder from a previous version and blocks
  **Generate** until you delete it (one click, from a banner in the
  Actions tab) — having both installed at once means two loading screen
  packages are active, and only one can be.
- **`mods_folder` is now guessed automatically** on Windows/macOS (it's
  always your Sims 4 data folder with `Mods` appended, e.g.
  `Documents/Electronic Arts/The Sims 4/Mods`) and pre-filled in the
  Settings tab if found.
- **Icon/logo redesigned**: the dice pips are now clearly little framed
  photos (a dark frame border around a white photo, not just a plain
  diamond), and the brand green is deeper/more muted (`#2e7d32` face,
  was `#3fae52`).
- **Steam artwork consolidated to one set per slot** (`cover.png`,
  `wide_cover.png`, `background.png`, `logo.png`) — the `_dark`/`_light`
  pairs and the separate `assets/icon_dark.png`/`icon_light.png` source
  icons are gone. Colors now match the brand icon/logo exactly, on a
  light green background chosen to give the deeper icon room to stand out.
- **License changed to GPL-3.0-or-later** — TS4RLS is now public/open
  source (was closed-source/all-rights-reserved).
- Releases now also publish **`TS4RLS_Steam_Assets.zip`**, both as a
  release asset and to a permanent link on the `steam_assets` branch
  (`.github/workflows/release.yml`), so the Steam artwork can be grabbed
  without downloading a whole release or cloning the repo.

### Removed
- `launch_game`, `launch_via_steam`, `game_exe`, `create_curseforge_version`
  config keys; the `--force-launch` flag; `assets/icon_curseforge.*`;
  `assets/icon_dark.png`/`icon_light.png`;
  `assets/steam/*_dark.png`/`*_light.png`.

## [3.0.0] - 2026-09-10

### Changed
- **CLI removed entirely.** The interactive text menu (`src/cli/menu.py`,
  `--cli`) is gone — the GUI's Settings tab is now the only config editor.
  `src/cli/info_guide.py` was removed too (it was only reachable from the
  menu).
- **Single entry point moved to the repo root**: `src/app.py` and
  `src/gui.py` were merged into a root-level `gui.py`. Run `python gui.py`
  for the GUI or `python gui.py --generate [--force-launch]` headless.
- **Main executable renamed** from `Sims4RandomLoadingScreen` to `TS4RLS`,
  and its OS app-data folder (where `config.json` lives when not running
  portably) renamed to match — existing installs need to re-enter their
  settings once, or move their old `config.json` over manually.
- **Built executables now land in `dist/`** instead of the repo root.
- **One unified brand icon/logo**: `assets/icon.png`/`logo.png` is now a
  single medium-green mark used everywhere (GUI window icon, main
  executable icon, About tab) — the `app_icon` config key and the
  `logo_dark.png`/`logo_light.png` split are gone. `icon_dark.png`/
  `icon_light.png` remain, but only as inputs to the Steam asset generator
  (Steam genuinely has a light/dark theme; the app itself doesn't need one).

### Removed
- `src/cli/menu.py`, `src/cli/info_guide.py`, `src/common/theme.py`
  (OS dark-mode detection, no longer needed without a dark/light app icon
  choice), `assets/logo_dark.png`, `assets/logo_light.png`, the `app_icon`
  config key.

## [2.0.4] - 2026-09-10

### Added
- **`app_icon` config key** (`"dark"` or `"light"`, default `"dark"`) —
  `src/build/executable_builder.py` now asks (or reads this default
  non-interactively) which brand icon the main app executable is built
  with, instead of always using the dark one.
- **`assets/icon_curseforge.ico`/`.icns`/`.png`** — restored the original
  green plumbob-style icon (which mimics Sims 4's own game icon) and the
  `TS4_x64` CurseForge build now uses it instead of the TS4RLS brand icon,
  so the disguised executable looks like the real game exe it replaces.

### Changed
- **Icon/text contrast rule, applied consistently everywhere**: anything
  on a dark background (`*_dark` steam assets, `logo_dark.png`) now uses
  the *light* icon and the light icon's own color for text; anything on a
  light background (`*_light` steam assets, `logo_light.png`) uses the
  *dark* icon and the dark icon's own color for text — previously the
  dark/light suffix matched its own same-tone icon (low contrast) and text
  colors were chosen ad hoc per asset.

## [2.0.3] - 2026-09-10

### Changed
- `logo_dark.png`/`logo_light.png` wordmark text now uses the same green
  as its paired icon (was a separately-chosen dark text/white text pair)
  and the canvas is auto-cropped to its content instead of shipping a
  fixed-width image with a large empty margin on the right.
- `assets/steam/logo_dark.png`/`logo_light.png` (the Steam "Library logo"
  slot) was missing the "TS4RLS" shortcode entirely (subtitle only) —
  added it back.
- All four `assets/steam/*_dark.png`/`*_light.png` assets (cover, wide
  cover, background, logo) now use the same green-tinted title/subtitle
  colors — `cover.png`/`wide_cover.png` previously used plain
  white/near-black text, inconsistent with the logo asset.
- `assets/logo_dark.png`/`logo_light.png` (the top-level wordmark) now use
  the exact same green-tint text colors as their `assets/steam/` counterparts.

## [2.0.2] - 2026-09-10

### Changed
- **Brand palette corrected to green** — the v2.0.1 mark used purple as
  the primary color; the actual TS4RLS theme is green throughout. Assets
  renamed to reflect what they now represent: `icon.ico`/`.icns`/`.png` →
  **`icon_dark.*`** (dark green, the app's default/dark-mode icon),
  `alt_icon.*` → **`icon_light.*`** (a brighter green, used for the
  `TS4_x64` build and the GUI's light-mode branding). Added
  `logo_dark.png`/`logo_light.png` (the previous single `logo.png` had
  dark text that was unreadable on a dark background) — the README now
  picks between them automatically via `<picture>`/`prefers-color-scheme`.
- **Icon redesign**: the "image" pips are now diamond-shaped (a die face
  made of small diamond photo-icons) instead of rounded squares.
- `assets/steam/*.png` renamed from `<name>`/`<name>_alt` to
  `<name>_dark`/`<name>_light` and regenerated with the corrected palette.

## [2.0.1] - 2026-09-10

### Changed
- **Project moved to the `TS4RLS` GitHub org** (`github.com/TS4RLS/Engine`,
  transferred from `StuxieDev/Sims-4-Random-Loading-Screen` — old links
  redirect, but every in-repo reference now points at the new URL), joined
  by new `TS4RLS/Website` (`ts4rls.stuxie.dev`) and `TS4RLS/.github` repos.
- **Brand mark redesigned** — `assets/icon.png`/`icon.ico`/`icon.icns`,
  `alt_icon.*`, and `assets/logo.png` are now a flat, minimal "photo dice"
  mark (three small image pictograms in a diagonal die-face arrangement)
  instead of the previous gradient ring/badge composition, in the same
  purple (main) and green (`alt_icon`, light-mode/CurseForge) palettes.
  `assets/steam/*.png` regenerated to match.
- README header now reads "TS4RLS — The Sims 4 Random Loading Screen" and
  adds a `Website:`/`License:` line alongside `Repository:`, matching the
  org's other repos.

## [2.0.0] - 2026-09-10

A restructuring release: the app now ships as a single self-contained
executable with a GUI and a CLI sharing the same logic, instead of a
collection of scripts glued together by Launcher.bat/Launcher.sh.

### Added
- **GUI** (`src/gui.py`, tkinter) — Settings, Actions, and About tabs
  covering everything the CLI does: generate, rename, configure, and (from
  source) build/test. Automatically uses the main purple/orange branding
  in dark mode and the green plumbob `alt_icon` branding in light mode
  (best-effort OS dark-mode detection).
- **CLI text menu** (`src/cli/menu.py`) — Generate / Rename / Configure /
  Info / Exit, reachable via `--cli` on the app or the dev launcher.
- **Single entry point** (`src/app.py`) — `python src/app.py` (GUI),
  `--cli` (text menu), `--generate [--force-launch]` (headless). The exact
  same build, renamed to `TS4_x64`/`TS4_x64.exe`, auto-detects its own
  filename and behaves as `--generate --force-launch` with no arguments,
  for the CurseForge pre-launch script use case.
- **Per-user config location** — `config.json` now lives in the OS
  user-data directory (`%APPDATA%`, `~/Library/Application Support`, or
  `~/.config`) by default, resolved by `src/common/paths.py`. A
  `config.json` already sitting next to the running app/script still takes
  priority ("portable mode"), so existing from-source checkouts keep
  working unchanged. `SIMS4_RLS_CONFIG_DIR` overrides the location
  entirely (used by the test suite).
- **Bundled assets** — the built executable bundles `template.package`,
  the icon PNGs, and `assets/steam/` directly (no source tree required
  alongside it). The About tab can save the Steam artwork set as a zip.
- **Quick-setup wizard** (`src/cli/config_editor.py`) runs automatically
  the first time no config is found, walking through every setting in
  order (Enter accepts the default, or type a custom value).
- **`config.json`/`config.example.json` are now JSONC** (JSON plus `//`
  line comments) — every setting is documented inline
  (`src/common/config_format.py`).
- **Colored CLI output** across every script (`src/cli/cli_colors.py`).
- **`non_interactive` config key** (default `true`) so unattended runs
  never block on the "press any key to close" prompt.
- Cross-platform CurseForge builds (macOS/Linux, not just Windows).

### Changed
- **`src/` reorganized** into `common/`, `core/`, `cli/`, and `build/`
  subfolders by role, plus top-level `gui.py`/`app.py`.
  `package_generator.py` → `core/generator.py`, `images_renamer.py` →
  `core/renamer.py`; both now expose callable `generate()`/
  `rename_images()` functions instead of running side effects at import
  time, so the GUI/CLI/headless modes call them in-process.
- **`STEAM_GUIDE.md`, `CONTRIBUTING.md`** moved to `docs/`.
- **Executable names**: the old `Launcher.exe`/`RandomLoadingScreen.exe`
  pair is replaced by a single `Sims4RandomLoadingScreen`(`.exe`).
  `TS4_x64`(`.exe`) is unchanged in purpose.
- `Launcher.bat`/`Launcher.sh` are now explicitly the from-source dev
  entry point (open the app, build executables, run tests) — end users
  should download the built executable instead.

### Fixed
- Non-ASCII arrow/multiplication-sign characters in generator log output
  could crash on consoles using a legacy codepage (e.g. `UnicodeEncodeError`
  on some Windows setups); replaced with ASCII equivalents.

## [1.3.4] - 2026-09-10

### Added
- **`non_interactive` config key** (default `true`) — controls whether
  `src/package_generator.py` blocks on the final "press any key to close"
  prompt when `launch_game` is `false`. Previously this only skipped when
  invoked with `--generate`; now it's off by default everywhere, and can be
  set to `false` in `config.json` to bring the prompt back for the
  interactive menu.

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
