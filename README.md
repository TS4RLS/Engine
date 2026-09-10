<p align="center">
  <img src="assets/logo.png" width="500" alt="TS4RLS — The Sims 4 Random Loading Screen">
</p>

# TS4RLS — The Sims 4 Random Loading Screen

Automatically picks a random image from a folder and installs it as your Sims 4 loading screen mod — run it, then launch the game yourself and get a fresh screen every time.

**Version 4.0.0** — see [CHANGELOG.md](CHANGELOG.md) for release history.

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

- **First run**: the Settings tab lets you set your images folder, Mods
  folder, and a handful of optional settings — no manual config file
  editing required.
- Settings are stored per-user (Windows: `%APPDATA%`, macOS:
  `~/Library/Application Support`, Linux: `~/.config`), so the app works
  the same no matter where you put the executable.

---

## Using it

**1. Add your images**

Drop PNG, JPG, BMP, WebP, or TIFF images into the images folder you set up. Sub-folders are scanned automatically. One image is enough; the more you have, the more variety you get.

**2. Run before launching the game**

- **GUI**: double-click the executable, go to the **Actions** tab, click
  **Generate loading screen**.
- **Unattended** (scripts, other launchers, a Steam shortcut): run it with
  `--generate`. It never blocks waiting for a keypress.

Either way, it picks a random image and builds the mod. Launch Sims 4 yourself afterwards to see it.

---

## Configuration

Use the **Settings** tab to change anything — it reads and writes
`config.json` directly. Only `images_folder` and `mods_folder` are
required; everything else has a default.

| Key | Required | Default | Description |
|---|---|---|---|
| `images_folder` | ✓ | — | Folder containing your source images |
| `mods_folder` | ✓ | — | Your Sims 4 Mods folder — this is your Sims 4 game data folder with `Mods` added (e.g. `Documents/Electronic Arts/The Sims 4/Mods`), not the game's installation directory. The Settings tab pre-fills this automatically if it finds it. |
| `is_vertical` | | `true` | When `true`, combines **2 portrait images** side-by-side into one landscape loading screen |
| `rename_files` | | `false` | When `true`, renames every image in `images_folder` to a random 32-character alphanumeric name and converts it to JPEG before picking a random image |
| `non_interactive` | | `true` | When `true`, never blocks on the "press any key to close" prompt |
| `target_width` / `target_height` | | `1920` / `1080` | Loading screen output size |

### Vertical mode

When `is_vertical` is `true`, the app randomly picks **two portrait-oriented images** and stitches them side-by-side into a single landscape loading screen. Use tall/portrait photos for best results. Set to `false` to use one image directly.

---

## Steam artwork

`assets/steam/` has a full set of custom Steam library artwork for adding
TS4RLS to your Steam library as a non-Steam game — see
**[docs/STEAM_GUIDE.md](docs/STEAM_GUIDE.md)** for the asset list and how to
apply it.

**[⬇ Download TS4RLS_Steam_Assets.zip](https://github.com/TS4RLS/Engine/raw/steam_assets/TS4RLS_Steam_Assets.zip)**
— always up to date with the latest release, no need to clone the repo.
(Also available from the About tab's **Save Steam artwork (.zip)...** button,
or as an asset on any [Release](https://github.com/TS4RLS/Engine/releases).)

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
| `config.json not found` | Run the app and fill in the Settings tab — it's created on first save |
| `config.json missing required key` | Use the Settings tab to fill it in |
| `Images folder not found` | Update `images_folder` in Settings |
| `Mods folder not found` | Update `mods_folder` in Settings |
| `No images found` | Check the folder path and that your files are PNG/JPG/BMP/WebP/TIFF |
| Loading screen unchanged in-game | Delete `localthumbcache.package` from your Mods folder, then relaunch |
| Still showing blue loading screen | Remove any other loading screen `.package` from your Mods folder |

---

## Development

This section is for contributors running from source — end users should
just download the executable above.

- **Requirements**: Python 3.6+, `pip install -r requirements.txt`
  (`Pillow`/`PyInstaller` are also installed automatically if missing).
- Run **`Launcher.bat`** (Windows) or **`./Launcher.sh`** (macOS/Linux) for
  a small dev menu: open the app, build the executable(s), or run the test
  suite.
- `python gui.py` (GUI) or `python gui.py --generate` (headless) run the
  app directly without building anything.
- `python src/build/executable_builder.py` builds `TS4RLS`(`.exe`) into
  `dist/`. PyInstaller can't cross-compile, so build on each platform you
  want a native executable for.
- `pytest -v` runs the test suite (`.github/workflows/ci.yml` runs the same
  on every push/PR).

See **[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)** for the full project
layout and release flow.

---

## Do not rename or remove

These files in `assets/` are required at runtime/build time, not just artwork:

- `template.package` — base mod template every generated loading screen is spliced into
- `icon.ico` / `icon.icns` / `icon.png` — the app's icon (window icon and the executable's icon)
- `logo.png` — the wordmark logo

---

*Built & Maintained by <img src="https://github.com/StuxieDev.png" height="14" alt="StuxieDev" valign="middle"> [StuxieDev](https://github.com/StuxieDev).*
