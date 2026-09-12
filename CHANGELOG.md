# Changelog

All notable changes to this project are documented here. Versioning follows
[Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`): MAJOR bumps
mark breaking config-format/behavior changes, MINOR marks backward-compatible
feature additions, PATCH marks fixes.

## [5.3.0] - 2026-09-13

### Added
- `src/build/create_project_assets.py` now also writes `favicon.ico` at
  the Website repo's root, not just under `assets/` — browsers request
  `/favicon.ico` directly as a fallback regardless of the `<link
  rel="icon">` tag in `<head>`, so the site-root copy needs to stay in
  sync with the app's branding too.

## [5.2.0] - 2026-09-12

### Added
- `src/build/create_steam_assets.py` now also syncs its output into the
  sibling Website repo's `assets/steam/` (which publishes its own copy for
  ts4rls.stuxie.dev/steam), the same way `create_project_assets.py` already
  syncs `icon.png`/`logo.png`/`favicon.ico` — so the published Steam art
  can no longer silently drift out of sync with the Engine's copy.

### Fixed
- **`create_steam_assets.py` clipped/overlapped the wordmark** when
  building `assets/steam/*` from the current `logo.png` — it cropped the
  wordmark out at a hardcoded x/y split tuned for an older layout, which
  cut a few pixels off the left of the tagline and clipped the bottom of
  the acronym in the stacked variant (`assets/steam/logo.png`), making it
  crowd into the tagline below. Both splits are now found dynamically
  from the image's own alpha channel, so they stay correct regardless of
  the wordmark's exact layout.

## [5.1.4] - 2026-09-12

### Fixed
- **`logo.png`'s wordmark text sat noticeably higher than the icon, and
  the canvas had a large dead gap on the right** (`src/build/create_project_assets.py`'s
  `draw_wordmark()`) — the acronym+tagline block is now measured up front
  and vertically centered against the icon's own center, and the canvas
  width is sized to fit the actual rendered content plus a small
  symmetric margin, instead of a hardcoded, wider-than-necessary value.
- **`icon.png`'s diagonal tile pattern was too large/off-center**, sitting
  much closer to two of the icon's four corners than the other two
  (`draw_glyph()`'s tile placement constants) — shrunk and re-centered so
  the pattern's bounding box has the same margin on all four sides.
- **`src/build/create_steam_assets.py` clipped/overlapped the wordmark**
  when regenerating `assets/steam/*` from the fixed `logo.png` above —
  it cropped the wordmark out of the logo at a hardcoded x/y split tuned
  for the old layout, which cut a few pixels off the left of the tagline
  and clipped the bottom of the acronym in the stacked variant
  (`assets/steam/logo.png`), making it crowd into the tagline. Both
  splits are now found dynamically from the image's own alpha channel,
  so they stay correct regardless of the wordmark's exact layout.

## [5.1.3] - 2026-09-12

### Changed
- Merged `src/scripts/` into `src/build/` and renamed all three dev/CI
  scripts: `build_release_files.py` → `create_release_files.py`,
  `generate_icon.py` → `create_project_assets.py`, `steam_asset_builder.py`
  → `create_steam_assets.py` — matching the sibling TWRAR project's layout
  and naming.
- `create_project_assets.py` now also writes the sibling Website repo's
  `icon.png`/`logo.png` directly (previously only `favicon.ico`) — reuses
  the 1024x1024 hi-res render already generated for `icon.icns` so the
  website's icon isn't downgraded to the app's smaller 256x256 one.

## [5.1.2] - 2026-09-12

### Fixed
- README's config table was missing 3 real settings (`launch_via_steam`,
  `game_folder`, `curseforge_mode`) and never documented the standalone
  runner executable feature at all — added a "Standalone runner" section
  and the missing table rows.
- README's "Do not rename or remove" list was missing
  `assets/checkbox_check.png` (the Qt theme's checked-checkbox icon).
- CONTRIBUTING.md's project layout tree omitted `src/build/` (the Steam
  asset generator) and `src/common/update_checker.py`.

## [5.1.1] - 2026-09-12

### Fixed
- `.gitignore` was missing `.venv/`/`venv/` (present in the sibling
  TWRAR/Engine's `.gitignore` but not here) — a local virtualenv could
  get committed by accident.

## [5.1.0] - 2026-09-12

### Added
- **`assets/steam/icon.png`** (256x256, transparent) — the app's own icon,
  for Steam's separate "Icon" custom-artwork slot (the non-Steam-game
  shortcut icon, not the library grid art). Included in
  `TS4RLS_Steam_Assets.zip` and the About tab's Steam artwork export like
  every other file in `assets/steam/`.

## [5.0.1] - 2026-09-12

### Fixed
- `cover.png`'s icon+wordmark block is now centered both horizontally
  *and* vertically in the 600x900 canvas (`src/build/steam_asset_builder.py`'s
  `build_cover()`) — it previously pinned the icon at a fixed `y=300`,
  leaving a lot of empty patterned space below the text.

### Changed
- Moved `scripts/` into `src/scripts/` (`build_release_files.py`,
  `generate_icon.py`) so all first-party source lives under `src/`.

## [5.0.0] - 2026-09-12

### Changed
- **The GUI is rewritten from Tkinter to PySide6/Qt** (`src/gui/`:
  `theme.py`, `disclaimer.py`, `workers.py`, `main_window.py`,
  `runner_builder.py`) — a MAJOR bump since this touches how the app
  looks and runs top to bottom, even though config.json's own format is
  unchanged. Motivated by a run of Tk-specific bugs this session turned
  up (the first-launch disclaimer silently never appearing at all on a
  fresh install, a family of white/gray border bugs in dark mode from
  clam theme bevel colors) that simply don't exist as a category in Qt.
  Worker threads now emit Qt signals straight to the UI instead of a
  manual `queue.Queue` + polling loop; the About tab's scrollable body
  is a native `QScrollArea` instead of a hand-rolled canvas+scrollbar;
  the changelog viewer renders real HTML instead of manually walking
  text with per-run tag_configure() calls. `requirements.txt` gains
  `PySide6>=6.7`.
- Default window size bumped to 960×760 (was 780×640) — the Build tab
  needed more room once `curseforge_mode`/`game_folder` were added.
- `.github/workflows/release.yml`'s Linux job now installs Qt's runtime
  libraries (`libegl1`/`libopengl0`) instead of `python3-tk`.
- `scripts/build_release_files.py` rewritten in the sibling TWRAR
  project's own style (`pathlib`, installs its own dependencies,
  `PyInstaller.__main__.run()` instead of a subprocess call) — still
  builds the release exe by default, or `TS4RLS_Steam_Assets.zip` with
  `--steam-zip`.

### Added
- **A standalone "runner" executable** (`runner.py`, built via
  `src/gui/runner_builder.py`) — a separate, GUI-less exe meant to
  replace the game's own launch target in Steam (a non-Steam-game
  shortcut) or CurseForge: running it regenerates the loading screen
  from the current config and launches the game, no window of its own.
  The Home/Build tabs' "Build executable" button now builds *this*
  (works from a shipped exe too — it only needs a system Python capable
  of running PyInstaller, not a source checkout), not the main app,
  which is still `python scripts/build_release_files.py` — a GUI button
  for that was removed along with the old Tk build, since rebuilding the
  app itself from source isn't something a shipped-exe user can do
  anyway. New **`curseforge_mode`** setting names the built runner the
  same as The Sims 4's own executable (`TS4_x64`) instead of the default
  `RLSRunner`, for launchers that expect a specific filename. The built
  runner's location (not dist/ — a source-checkout concept that isn't
  guaranteed to exist or be writable next to a shipped exe; the same
  per-user directory config.json itself uses) is shown on both tabs with
  "Copy path"/"Copy folder" buttons — the tool never places it into
  Steam/CurseForge's config itself, only points at where it landed.
- `src/common/launcher.py`: the Steam-URI/direct-exe game-launch logic,
  extracted out of the GUI so `runner.py` can share it without any Qt
  dependency.
- `paths.user_data_dir()`: public wrapper around the existing per-user
  data directory logic, for callers (the runner builder) outside
  `src/common` that need it.

### Fixed
- `runner_builder.py` checked for PyInstaller *after* already importing
  it — on a machine without PyInstaller installed, this crashed before
  ever reaching the auto-install step meant to handle exactly that case.

## [4.7.0] - 2026-09-12
### Added
- **`scripts/generate_icon.py`**, matching the sibling TWRAR project's
  convention: reproduces the icon/logo (three diamond "photo frame" tiles
  - a sun/moon dot and a tree, on a green rounded square) in code instead
  of only existing as hand-made PNGs, so it can be regenerated/tweaked
  going forward. `assets/icon.png`/`icon.ico`/`icon.icns`/`logo.png`
  regenerated from it (visually unchanged).

## [4.6.0] - 2026-09-12
### Changed
- **`build.bat`/`build.sh` are gone.** `src/build/executable_builder.py` is
  moved to `scripts/build_release_files.py` and run directly
  (`python scripts/build_release_files.py`) instead of through an
  OS-specific wrapper. `.github/workflows/release.yml` calls it the same
  way, matching the sibling TWRAR project's convention.

## [4.5.0] - 2026-09-12

### Added
- **"Launch The Sims 4"** button on the Home tab. Launches via Steam
  (`steam://rungameid/1222670`) by default; uncheck the new "Launch via
  Steam" setting in the Build tab and set a **game folder** instead for
  a direct `TS4_x64.exe`/`TS4.exe` launch (EA App/Origin installs, or
  anyone who'd rather not go through Steam).

### Fixed
- **Link/hint/error label colors weren't rendering the theme's accent
  color** — `Link.TLabel`/`Hint.TLabel`/`Error.TLabel` were only ever
  defined inside `theme_create()`'s `settings` dict; `style.lookup()`
  correctly reported their configured colors, but ttk didn't reliably
  apply a compound style's own foreground override when it's set that
  way, so links rendered in the base text color instead. Fixed by
  configuring them via plain `style.configure(...)` calls issued after
  `style.theme_use()` activates the theme, instead.
- **Window icon still showed Tk's stock feather icon in the Windows
  taskbar/Alt-Tab switcher** — `iconphoto()` alone sets the title-bar
  icon but doesn't reliably replace the cached taskbar icon on Windows.
  Now also calls `iconbitmap(default=...)` with `assets/icon.ico` on
  Windows — and specifically *before* `iconphoto()`, since calling it
  afterwards resets the taskbar icon back to the interpreter's own icon
  (confirmed by direct A/B testing).
- **Launching the built Windows executable popped a console window
  before the GUI appeared** — the exe was built with PyInstaller's
  `--console` (so `--generate` could still print output when launched
  from a terminal/shortcut), which allocates a console for every launch
  including a plain GUI one; hiding it from within gui.py only happened
  after Python/Tk had already finished starting up, so the console
  still visibly flashed open first. Now built `--windowed` instead (no
  console at all, ever), and `--generate` attaches to the *launching*
  terminal's own console at runtime (`AttachConsole`) when one exists,
  instead of allocating a new one of its own.
- **The app never actually opened on a fresh install (or after clearing
  app state)** — the first-launch disclaimer dialog is a `Toplevel`
  created while the main window is still `withdraw()`n, and on Windows,
  a `Toplevel` made `.transient()` for a still-withdrawn owner never
  gets mapped at all (confirmed by direct testing, isolated from the
  rest of the app). The dialog silently never appeared, `wait_window()`
  blocked forever, and the app looked hung with no window whatsoever.
  Dropping `.transient(self)` for this dialog fixes it — `grab_set()`
  already made it modal without needing that.
- **Dark mode showed stark white/gray borders** on the notebook's edge,
  every `Entry` field, checkbox indicators, and scrollbars — the custom
  ttk theme is built on "clam", which draws each of those as a 3D bevel
  using `lightcolor`/`darkcolor` (and, for checkbuttons, their own
  upper/lower border options) that default to a fixed system gray
  regardless of the theme's `bordercolor`. All now pinned to the
  theme's own colors so every edge renders as one flat, correctly
  dark (or light) line instead.

### Changed
- Window title reformatted to `TS4RLS (The Sims 4 Random Loading
  Screen) — vX.Y.Z`.
- Checkbox indicators now use the theme's accent/panel colors instead
  of clam's default light-gray look.
- The theme toggle button moved from a persistent bar above the tabs
  into the Home tab.
- About tab now shows the full logo banner (`assets/logo.png`) instead
  of a small icon plus a separate text header.
- The Home/Build action logs and the changelog viewer now use a themed
  `ttk.Scrollbar` instead of `scrolledtext.ScrolledText`'s built-in one —
  Tk delegates that widget's rendering to Windows' native Visual Styles
  engine, so it always rendered as a stark white scrollbar regardless of
  the active theme.
- Regenerated every Steam library asset (`assets/steam/`) from the
  current `icon.png`/`logo.png` — they'd drifted out of sync with the
  app's own branding since v4.0.0. Background patterns also switched to
  smaller, denser icon tiles instead of a few oversized, sparse ones,
  and `cover.png`/`logo.png` now center the title and subtitle text
  independently instead of as one left-aligned block (which left the
  narrower "TS4RLS" title looking off-center under the icon). Added a
  second logo style, `logo_horizontal.png` (icon beside the wordmark,
  rather than stacked above it), as an alternative for the same Library
  logo slot. Added `src/build/steam_asset_builder.py` so none of this
  has to be redone by hand again.
- `CONTRIBUTING.md` moved back to the repo root (out of `docs/`, which
  no longer exists), matching every other repo doc.
- `STEAM_GUIDE.md` removed — the Steam artwork download and setup info
  it held now lives on the website (`ts4rls.stuxie.dev/steam`) instead.

## [4.4.0] - 2026-09-10

### Added
- **Update checker**: the About tab checks GitHub Releases for a newer
  version in the background on load, shows "You're on the latest
  version." or "Update available: vX.Y.Z" with a download link straight
  to the release, and a "Check again" button for a manual re-check. Pure
  stdlib (`urllib`), no new dependency — new `src/common/update_checker.py`
  (11 unit tests, mocked network).

### Changed
- **GUI theming replaced with a real custom ttk theme, built directly
  from the website's own color tokens** (`gui.py`'s new `COLORS` dict —
  one-to-one with `style.css`'s `:root`/`[data-theme]` blocks), covering
  every widget class this GUI uses (frames, labelframes, notebook tabs,
  buttons, entries, checkbuttons, scrollbars) — not just link labels
  layered on top of a generic third-party palette. The previous approach
  (`sv_ttk`, added in 4.2.0) only recolored a handful of labels; everything
  else stayed `sv_ttk`'s own unrelated blue-accented palette, which read as
  "not actually colored like the website." Built on the stock `clam` ttk
  theme via `ttk.Style().theme_create()` — the only bundled theme that
  honors these options everywhere (`vista`/`aqua` draw natively and ignore
  most of them). **`sv_ttk` is no longer a dependency.**

## [4.3.1] - 2026-09-10

### Fixed
- **v4.3.0's release build failed on Linux and macOS** ("Permission
  denied" running `./build.sh`) because the new `build.sh`/`commit.sh`
  were committed without the executable bit — git tracked them as `100644`
  instead of `100755`. Windows silently worked anyway (no v4.3.0 GitHub
  Release was ever published, just a tag with no build artifacts).

### Added
- Every GitHub Release now carries a standing notice that the text-menu
  CLI is discontinued and unsupported (removed in v3.0.0) — added as a
  static `body` alongside `generate_release_notes` in
  `.github/workflows/release.yml`.

## [4.3.0] - 2026-09-10

### Added
- **`build.sh`/`build.bat`**: thin wrappers for
  `src/build/executable_builder.py`, matching the sibling `commit.sh`/
  `commit.bat` pair. `.github/workflows/release.yml` now calls `./build.sh`
  too, so CI and a local build go through the exact same entry point.

### Fixed
- **The main window no longer flashes visible before the first-launch
  disclaimer.** It now stays withdrawn (`self.withdraw()`) until the
  disclaimer is confirmed (or the whole app exits, if declined), instead
  of appearing and building all its tabs before the modal dialog covered it.
- **Disclaimer dialog relaid out to match TWRAR's own**: centered logo
  (the full wordmark, not just the icon), title, and body text; title
  changed from "Before you start" to "Before you continue" (also now the
  window title, replacing "Welcome to TS4RLS"); tighter, more consistent
  spacing; the dialog now centers on the screen instead of over the main
  window, since the main window has no real position yet while withdrawn.
  It already inherited the sv_ttk dark/light theme correctly (added in
  4.2.0) but is now given an explicit background too, matching the
  theme's panel color, since the previous flash-of-mismatched-background
  read as "not colored like the website".

## [4.2.1] - 2026-09-10

### Removed
- `Launcher.bat`/`Launcher.sh`. They were a thin dev-menu wrapper around
  commands (`python gui.py`, `python src/build/executable_builder.py`,
  `pytest -v`) that are just as easy to run directly, and every dependency
  they bootstrapped (Pillow, sv_ttk, PyInstaller) is now auto-installed by
  `gui.py`/`executable_builder.py` themselves.

## [4.2.0] - 2026-09-10

### Added
- **GUI light/dark theme toggle**, matching ts4rls.stuxie.dev's own
  palette: a bright green accent (`#4fc264`) in dark mode, the deeper
  icon-face green (`#2e7d32`) in light mode. Reskins every ttk widget via
  `sv_ttk` (new dependency, auto-installed like Pillow), and re-themes the
  changelog viewer, action logs, and every link label on toggle. Dark by
  default.

## [4.1.4] - 2026-09-10

### Fixed
- `assets/logo.png` subtitle text is now bold (matching the title's
  weight, just at a smaller size) instead of regular weight, which still
  read as too faint — the color was already correct (same medium green
  as the icon face) from 4.1.2.

## [4.1.3] - 2026-09-10

### Fixed
- `assets/logo.png` subtitle was still too faint even at the matching
  color from 4.1.2 — the light font weight itself was the remaining
  problem. Switched to the regular weight (from the light one) and bumped
  the size slightly.

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
