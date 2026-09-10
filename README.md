<p align="center">
  <img src="assets/logo.png" width="500" alt="Sims 4 Random Loading Screen">
</p>

# Sims 4 Random Loading Screen

Automatically picks a random image from a folder and installs it as your Sims 4 loading screen mod — run it before launching the game and get a fresh screen every time.

---

## Requirements

- **Python 3.6+** — [python.org/downloads](https://www.python.org/downloads/) *(tick "Add Python to PATH" during install)*
- **Pillow** — installed automatically on first run, or manually: `pip install Pillow`

---

## Setup

**1. Configure your paths**

Copy `config.example.json` to `config.json` and fill in the two required fields:

```json
{
  "images_folder": "C:/Users/YourName/Pictures/The Sims 4 Loading Screens",
  "mods_folder":   "C:/Users/YourName/Documents/Electronic Arts/The Sims 4/Mods"
}
```

**2. Add your images**

Drop PNG, JPG, BMP, WebP, or TIFF images into your `images_folder`. Sub-folders are scanned automatically. One image is enough; the more you have, the more variety you get.

**3. Run before launching the game**

Run **`Launcher.bat`** (Windows) or **`./Launcher.sh`** (macOS/Linux) and
choose **1) Generate loading screen** from the menu — or, once built, just
double-click **`Launcher.exe`**, which skips the menu and generates directly.
Either way, it picks a random image, builds the mod, and optionally launches
Sims 4 for you.

By default (`non_interactive: true`) it never blocks on the final
"press any key to close" prompt, so it's safe to drive unattended from
scripts, other launchers, or CI. For fully unattended use, pass
`--generate` directly — `Launcher.bat --generate` / `./Launcher.sh
--generate` — which also skips the menu. Add `--force-launch` to also
launch the game regardless of `launch_game` in `config.json`. This is
exactly how `Launcher.exe`/`TS4_x64.exe` invoke it.

---

## Configuration

All settings live in `config.json`. Only `images_folder` and `mods_folder` are required — everything else has a default.

| Key | Required | Default | Description |
|---|---|---|---|
| `images_folder` | ✓ | — | Folder containing your source images |
| `mods_folder` | ✓ | — | Your Sims 4 Mods folder |
| `is_vertical` | | `true` | When `true`, combines **2 portrait images** side-by-side into one landscape loading screen |
| `rename_files` | | `false` | When `true`, renames every image in `images_folder` to a random 32-character alphanumeric name and converts it to JPEG before picking a random image. Can also be run standalone via `Launcher.bat`/`Launcher.sh` (option 2) or `python src/images_renamer.py` |
| `launch_game` | | `true` | Automatically launch Sims 4 after generating the mod |
| `non_interactive` | | `true` | When `true`, never blocks on the "press any key to close" prompt (only shown when `launch_game` is `false`) — set to `false` if you want that pause when running the interactive menu |
| `launch_via_steam` | | `true` | Launch via Steam (`steam://rungameid/...`) |
| `game_exe` | | `""` | Direct path to `TS4_x64.exe` — only used when `launch_via_steam` is `false` |

> **`config.json` is gitignored** — your personal paths are never committed.

### Vertical mode

When `is_vertical` is `true`, the script randomly picks **two portrait-oriented images** and stitches them side-by-side into a single landscape loading screen. Use tall/portrait photos for best results. Set to `false` to use one image directly.

---

## Steam launcher (.exe)

To add the tool to Steam as a non-Steam game, build a standalone executable
via `Launcher.bat`/`Launcher.sh` (option 3) or directly:

```
python src/executable_builder.py
```

This produces **`Launcher.exe`** (Windows) or plain **`Launcher`** (macOS/Linux)
in the project root, using `assets/icon.ico`/`icon.icns`. It just calls
`Launcher.bat`/`Launcher.sh` next to it in non-interactive mode — keep them
together. PyInstaller is installed automatically if needed. PyInstaller can't
cross-compile, so run the builder on each platform you want a native build
for.

If `create_curseforge_version` is `true` in `config.json`, a second
executable, **`TS4_x64`** (`TS4_x64.exe` on Windows), is also built using
`assets/alt_icon.ico`/`.icns` — the name mirrors Sims 4's own game
executable on each platform. It behaves identically but always launches the
game, for use as a CurseForge pre-launch script.

---

## Steam artwork

`assets/steam/` has a full set of custom Steam library artwork for the
non-Steam-game shortcut — see **[STEAM_GUIDE.md](STEAM_GUIDE.md)** for the
asset list and how to apply it.

---

## How it works

The Sims 4 loading screen is a `.package` file (DBPF 2.0 format) containing a single compressed image at a known resource key. Each run:

1. Scans `images_folder` and picks one image at random (or two, in vertical mode)
2. Resizes and centre-crops to match the template's resolution
3. Splices the new image into the template's GFX resource
4. Writes `RandomLoadingScreen.package` to `Mods/RandomLoadingScreen/`

The output won't conflict with other mods as long as no other loading screen `.package` exists in your Mods folder — only one can be active at a time.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `config.json not found` | Copy `config.example.json` → `config.json` and fill in your paths |
| `config.json missing required key` | Check `config.example.json` for required keys |
| `[ERROR] Images folder not found` | Update `images_folder` in `config.json` |
| `[ERROR] Mods folder not found` | Update `mods_folder` in `config.json` |
| `[ERROR] Template package not found` | Ensure `assets/template.package` is present |
| `[ERROR] No images found` | Check the folder path and that your files are PNG/JPG/BMP/WebP/TIFF |
| Loading screen unchanged in-game | Delete `localthumbcache.package` from your Mods folder, then relaunch |
| Still showing blue loading screen | Remove any other loading screen `.package` from your Mods folder |
| Python not found | Install Python and tick "Add to PATH" |

---

## Testing

Unit tests cover the pure logic in the Python scripts (image discovery,
resizing/cropping, ARGB packing, `.package` splicing, config parsing, and
file renaming) using temporary directories — no test touches your real
`config.json`, images, Mods folder, or the game itself.

```
pip install -r requirements.txt
pytest -v
```

A GitHub Actions workflow (`.github/workflows/ci.yml`) runs the same suite
on every push and pull request.

---

## Project layout

```
Launcher.bat / Launcher.sh  Interactive CLI entry point (root)
src/
  package_generator.py      Generates the loading screen mod
  images_renamer.py         Renames/converts images to JPEG
  executable_builder.py     Builds the standalone executable(s)
assets/                     Icons, logo, template.package
  steam/                    Steam library artwork (see STEAM_GUIDE.md)
config.json                 Your personal settings (gitignored)
```

## Do not rename or remove

These files in `assets/` are required at runtime/build time, not just artwork:

- `template.package` — base mod template every generated loading screen is spliced into
- `icon.ico` / `icon.icns` — icon embedded into `Launcher.exe`/`Launcher` at build time
- `alt_icon.ico` / `alt_icon.icns` — icon embedded into `TS4_x64`/`TS4_x64.exe` at build time

---

*Built & Maintained by <img src="https://github.com/StuxieDev.png" height="14" alt="StuxieDev" valign="middle"> [StuxieDev](https://github.com/StuxieDev).*
