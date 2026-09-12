<p align="center">
  <img src="assets/logo.png" width="300" alt="TS4RLS — The Sims 4 Random Loading Screen">
</p>

# TS4RLS — The Sims 4 Random Loading Screen

Automatically picks a random image from a folder and installs it as your Sims 4 loading screen mod — run it, then launch the game yourself and get a fresh screen every time.

**Version 5.2.0** — see [CHANGELOG.md](CHANGELOG.md) for release history.

Website: https://ts4rls.stuxie.dev  
Repository: https://github.com/TS4RLS/Engine  
License: [GPL-3.0-or-later](LICENSE.md)

---

## Download

Grab the latest **`TS4RLS`** executable from the
[Releases page](https://github.com/TS4RLS/Engine/releases) —
it's a single self-contained file, nothing else to install. Double-click it
for the GUI, or run it from a terminal with `--generate` for a headless
one-shot run.

- **First run**: a one-time disclaimer, then the **Build** tab lets you set
  your images folder, Mods folder, and a handful of optional settings — no
  manual config file editing required.
- Settings are stored per-user (Windows: `%APPDATA%`, macOS:
  `~/Library/Application Support`, Linux: `~/.config`), so the app works
  the same no matter where you put the executable.
- The GUI has a light/dark theme toggle in the top-right, using the same
  green palette as [ts4rls.stuxie.dev](https://ts4rls.stuxie.dev) — dark
  by default.
- The About tab checks GitHub for a newer release on load and shows a
  download link if one's available.

---

## Using it

**1. Add your images**

Drop PNG, JPG, BMP, WebP, or TIFF images into the images folder you set up. Sub-folders are scanned automatically. One image is enough; the more you have, the more variety you get.

**2. Run before launching the game**

- **GUI**: double-click the executable, go to the **Home** tab, click
  **Generate loading screen**.
- **Unattended** (scripts, other launchers, a Steam shortcut): run it with
  `--generate`. It never blocks waiting for a keypress.

Either way, it picks a random image and builds the mod. Launch Sims 4 yourself afterwards to see it.

---

## Configuration

Use the **Build** tab to change anything — it reads and writes
`config.json` directly. Only `images_folder` and `mods_folder` are
required; everything else has a default. The Home tab shows your current
settings read-only and links to the Build tab to change them.

| Key | Required | Default | Description |
|---|---|---|---|
| `images_folder` | ✓ | — | Folder containing your source images |
| `mods_folder` | ✓ | — | Your Sims 4 Mods folder — this is your Sims 4 game data folder with `Mods` added (e.g. `Documents/Electronic Arts/The Sims 4/Mods`), not the game's installation directory. The Build tab pre-fills this automatically if it finds it. |
| `is_vertical` | | `true` | When `true`, combines **2 portrait images** side-by-side into one landscape loading screen |
| `rename_files` | | `false` | When `true`, renames every image in `images_folder` to a random 32-character alphanumeric name and converts it to JPEG before picking a random image |
| `non_interactive` | | `true` | When `true`, never blocks on the "press any key to close" prompt |
| `target_width` / `target_height` | | `1920` / `1080` | Loading screen output size |
| `launch_via_steam` | | `true` | When `true`, launches The Sims 4 via `steam://` instead of a direct executable |
| `game_folder` | | — | Sims 4 game install folder — only used when `launch_via_steam` is `false` |
| `curseforge_mode` | | `false` | When `true`, the runner executable (see [Standalone runner](#standalone-runner) below) is named `TS4_x64` instead of `RLSRunner`, for CurseForge/launcher integrations that expect that filename |

### Vertical mode

When `is_vertical` is `true`, the app randomly picks **two portrait-oriented images** and stitches them side-by-side into a single landscape loading screen. Use tall/portrait photos for best results. Set to `false` to use one image directly.

---

## Standalone runner

The Build tab's **Build executable** button compiles a second, separate,
GUI-less executable — `RLSRunner` by default, or `TS4_x64` if
`curseforge_mode` is on. Running it regenerates the loading screen from
your current `config.json` and launches the game, with no window or
console of its own. Point Steam (as a non-Steam game shortcut) or
CurseForge at it instead of — or renamed to replace — the game's own
executable, and every normal launch gets a fresh loading screen
automatically, no extra step.

The Home tab shows the most recent runner build with buttons to copy its
executable path or containing folder — it's never auto-placed into
Steam/CurseForge's own config, you point them at it yourself.

---

## Steam artwork

`assets/steam/` has a full set of custom Steam library artwork (grid
capsules, hero, logo) for adding TS4RLS to your Steam library as a
non-Steam game.

**[⬇ Download TS4RLS_Steam_Assets.zip](https://github.com/TS4RLS/Engine/raw/steam_assets/TS4RLS_Steam_Assets.zip)**
— always up to date with the latest release, no need to clone the repo.
Also available from **[ts4rls.stuxie.dev/steam](https://ts4rls.stuxie.dev/steam)**,
the About tab's **Save Steam artwork (.zip)...** button, or as an asset on
any [Release](https://github.com/TS4RLS/Engine/releases).

---

## How it works

The Sims 4 loading screen is a `.package` file (DBPF 2.0 format) containing a single compressed image at a known resource key. Each run:

1. Scans `images_folder` and picks one image at random (or two, in vertical mode)
2. Resizes and centre-crops to match the template's resolution
3. Splices the new image into the template's GFX resource
4. Writes `TS4RLS.package` to `Mods/TS4RLS/`

The output won't conflict with other mods as long as no other loading screen `.package` exists in your Mods folder — only one can be active at a time.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `config.json not found` | Run the app and fill in the Build tab — it's created on first save |
| `config.json missing required key` | Use the Build tab to fill it in |
| `Images folder not found` | Update `images_folder` in the Build tab |
| `Mods folder not found` | Update `mods_folder` in the Build tab |
| `No images found` | Check the folder path and that your files are PNG/JPG/BMP/WebP/TIFF |
| Loading screen unchanged in-game | Delete `localthumbcache.package` from your Mods folder, then relaunch |
| Still showing blue loading screen | Remove any other loading screen `.package` from your Mods folder |

---

## Development

This section is for contributors running from source — end users should
just download the executable above.

- **Requirements**: Python 3.6+, `pip install -r requirements.txt`
  (`Pillow`/`PySide6`/`PyInstaller` are also installed automatically if
  missing).
- `python gui.py` (GUI) or `python gui.py --generate` (headless) run the
  app directly without building anything.
- `python src/build/create_release_files.py` builds `TS4RLS`(`.exe`) into
  `dist/`. PyInstaller can't cross-compile, so build on each platform you
  want a native executable for.
- `pytest -v` runs the test suite (`.github/workflows/ci.yml` runs the same
  on every push/PR).

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for the full project
layout and release flow.

---

## Do not rename or remove

These files in `assets/` are required at runtime/build time, not just artwork:

- `template.package` — base mod template every generated loading screen is spliced into
- `icon.ico` / `icon.icns` / `icon.png` — the app's icon (window icon and the executable's icon)
- `logo.png` — the wordmark logo
- `author.png` — avatar shown next to the author link on the About tab
- `checkbox_check.png` — the checkbox indicator's checked-state icon in the Qt GUI's theme

`VERSION.md` and `CHANGELOG.md` at the repo root are also bundled into the
executable — the GUI reads its own version from the former and renders the
latter in the About tab's changelog viewer.

---

*Written & Maintained by <img src="https://github.com/StuxieDev.png" height="14" alt="StuxieDev" valign="middle"> [StuxieDev](https://stuxie.dev).*

*[A StuxieDev Project](https://projects.stuxie.dev)*
