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

Double-click **`Sims4_RLS_Launcher.bat`** (or `Sims4_RLS_Launcher.exe`).
The script picks a random image, builds the mod, and optionally launches Sims 4 for you.

---

## Configuration

All settings live in `config.json`. Only `images_folder` and `mods_folder` are required — everything else has a default.

| Key | Required | Default | Description |
|---|---|---|---|
| `images_folder` | ✓ | — | Folder containing your source images |
| `mods_folder` | ✓ | — | Your Sims 4 Mods folder |
| `is_vertical` | | `true` | When `true`, combines **2 portrait images** side-by-side into one landscape loading screen |
| `rename_files` | | `false` | When `true`, renames every image in `images_folder` to a random 32-character alphanumeric name and converts it to JPEG before picking a random image. Can also be run standalone: `python Sims4_RLS_ImagesRenamer.py` |
| `launch_game` | | `true` | Automatically launch Sims 4 after generating the mod |
| `launch_via_steam` | | `true` | Launch via Steam (`steam://rungameid/...`) |
| `game_exe` | | `""` | Direct path to `TS4_x64.exe` — only used when `launch_via_steam` is `false` |

> **`config.json` is gitignored** — your personal paths are never committed.

### Vertical mode

When `is_vertical` is `true`, the script randomly picks **two portrait-oriented images** and stitches them side-by-side into a single landscape loading screen. Use tall/portrait photos for best results. Set to `false` to use one image directly.

---

## Steam launcher (.exe)

To add the tool to Steam as a non-Steam game, build a standalone executable:

```
python Sims4_RLS_ExeBuilder.py
```

This produces **`Sims4_RLS_Launcher.exe`** in the same folder. The exe just calls `Sims4_RLS_Launcher.bat` — keep both files together. PyInstaller is installed automatically if needed.

The icon is read from `.DONOTRENAME_DONOTREMOVE/ExeIcon_DONOTRENAME_DONOTREMOVE.ico` automatically.

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
| `[ERROR] Template package not found` | Ensure `.DONOTRENAME_DONOTREMOVE/TemplateLoadingScreen_DONOTRENAME_DONOTREMOVE.package` is present |
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
pip install -r requirements-dev.txt
pytest -v
```

A GitHub Actions workflow (`.github/workflows/ci.yml`) runs the same suite
on every push and pull request.

---

## Do not rename or remove

The `.DONOTRENAME_DONOTREMOVE/` folder must stay intact:

- `TemplateLoadingScreen_DONOTRENAME_DONOTREMOVE.package` — base mod template used to build each package
- `ExeIcon_DONOTRENAME_DONOTREMOVE.ico` — icon embedded into the `.exe` at build time

---

*Built & Maintained by <img src="https://github.com/StuxieDev.png" height="14" alt="StuxieDev" valign="middle"> [StuxieDev](https://github.com/StuxieDev).*
