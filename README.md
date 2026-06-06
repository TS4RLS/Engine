# Sims 4 Random Loading Screen Generator

Picks a random image from a folder of your choice and installs it as your
Sims 4 loading screen mod — every time you run it.

---

## Requirements

- **Python 3.6+** — https://www.python.org/downloads/
  - Tick "Add Python to PATH" during install
- **Pillow** — installed automatically by the `.bat` file (or run `pip install Pillow`)
- **`.DONOTRENAME_DONOTREMOVE/TemplateLoadingScreen_DONOTRENAMEORREMOVE.package`** — must remain in the `.DONOTRENAME_DONOTREMOVE` folder; do not rename or remove either the file or the folder

---

## Setup

1. **Copy `config.example.json` to `config.json`** and fill in your paths:

   ```json
   {
     "images_folder": "C:/Users/YourName/Pictures/Sims4LoadingScreens",
     "mods_folder":   "C:/Users/YourName/Documents/Electronic Arts/The Sims 4/Mods"
   }
   ```

   - `images_folder` — folder containing your PNG/JPG images (sub-folders scanned too)
   - `mods_folder` — your Sims 4 Mods folder (usually under `Documents\Electronic Arts\The Sims 4\Mods`)

   `config.json` is gitignored and never committed — your paths stay local.

2. **Put your images** (PNG, JPG, BMP, WebP) in `images_folder`.

3. **Double-click `Sims4_RLS_Launcher.bat`** (or `Sims4_RLS_Launcher.exe`) before launching the game.
   It will install Pillow if needed, pick a random image, and write the mod to your Mods folder.

4. **Launch The Sims 4** — your random loading screen will be active.

---

## Configuration reference

All settings live in `config.json`. Copy from `config.example.json` to get started.

| Key | Required | Default | Description |
|---|---|---|---|
| `images_folder` | yes | — | Folder of source images |
| `mods_folder` | yes | — | Your Sims 4 Mods folder |
| `is_vertical` | no | `true` | If `true`, combines 2 portrait images side-by-side; if `false`, uses 1 image directly |
| `launch_game` | no | `true` | Auto-launch Sims 4 after generating the mod |
| `launch_via_steam` | no | `true` | Launch via Steam (`steam://rungameid/...`) |
| `game_exe` | no | `""` | Direct path to `TS4_x64.exe` (only used when `launch_via_steam` is `false`) |
| `target_width` | no | `1920` | Output image width |
| `target_height` | no | `1080` | Output image height |

---

## Optional: Steam launcher `.exe`

If you want to add the launcher to Steam as a non-Steam game, you can build a standalone `.exe`:

```
python Sims4_RLS_ExeBuilder.py
```

This produces `Sims4_RLS_Launcher.exe` in the same folder. The exe simply calls
`Sims4_RLS_Launcher.bat` next to it — keep both files together.

---

## How it works

The Sims 4 loading screen is a single `.package` file (DBPF format) containing
a PNG image at a specific resource key. This script:

1. Scans `images_folder` and picks one (or two, in vertical mode) at random
2. Resizes/crops the image(s) to match the template's resolution (centre-crop, aspect-ratio safe)
3. If `is_vertical` is `true`, combines two portrait images side-by-side into one landscape image
4. Splices the new image into the template's GFX resource
5. Writes a valid DBPF 2.0 `.package` file to `mods_folder\RandomLoadingScreen\`

The output file is called `RandomLoadingScreen.package`. It won't conflict
with other mods as long as you don't have another loading screen `.package`
in your Mods folder.

> **Note:** Only ONE loading screen `.package` can be active at a time. If you
> have another custom loading screen mod installed, remove it first.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `config.json not found` | Copy `config.example.json` to `config.json` and fill in your paths |
| `config.json missing required key` | Check `config.example.json` for all required keys |
| `[ERROR] Images folder not found` | Update `images_folder` in `config.json` |
| `[ERROR] Mods folder not found` | Update `mods_folder` in `config.json` |
| `[ERROR] Template package not found` | Ensure `TemplateLoadingScreen_DONOTRENAMEORREMOVE.package` is inside the `.DONOTRENAME_DONOTREMOVE` folder |
| `[ERROR] No images found` | Check the folder path and file formats |
| Loading screen unchanged in game | Delete `localthumbcache.package` from your Mods folder, then relaunch |
| Game still shows blue loading screen | Ensure no other loading screen `.package` exists in Mods |
| Python not found | Install Python and tick "Add to PATH" |

---

## Image tips

- **Resolution:** 1920×1080 recommended; the script resizes automatically
- **Vertical mode:** Use portrait-oriented images (taller than wide) for best results when `is_vertical` is `true`
- **Format:** PNG gives best quality; JPG works fine too
- **Count:** Works with as few as 1 image or thousands
- **Variety:** The more images you add, the more variety you get!
