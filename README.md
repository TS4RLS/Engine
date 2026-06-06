# Sims 4 Random Loading Screen Generator

Picks a random image from a folder of your choice and installs it as your
Sims 4 loading screen mod — every time you run it.

---

## Requirements

- **Python 3.6+** — https://www.python.org/downloads/
  - Tick "Add Python to PATH" during install
- **Pillow** — installed automatically by the `.bat` file (or run `pip install Pillow`)

---

## Setup

1. **Edit `random_loading_screen.py`** — change the SETTINGS block at the top:

   ```python
   IMAGES_FOLDER = r"C:\Users\YourName\Pictures\Sims4LoadingScreens"
   MODS_FOLDER   = r"C:\Users\YourName\Documents\Electronic Arts\The Sims 4\Mods"
   ```

   Your Mods folder is usually:
   - `C:\Users\<name>\Documents\Electronic Arts\The Sims 4\Mods`

2. **Put your images** (PNG, JPG, BMP, WebP) in `IMAGES_FOLDER`.
   Sub-folders are scanned too, so you can organise them however you like.

3. **Double-click `Launch_RandomLoadingScreen.bat`** before launching the game.
   It will install Pillow if needed, pick a random image, and write the mod.

4. **Launch The Sims 4** — your random loading screen will be active.

---

## Optional: auto-launch the game

In `random_loading_screen.py`, set:

```python
LAUNCH_GAME = True
```

And either point `GAME_EXE` at `TS4_x64.exe`, or set `LAUNCH_VIA_STEAM = True`.

---

## How it works

The Sims 4 loading screen is a single `.package` file (DBPF format) containing
a PNG image at a specific resource key. This script:

1. Scans your images folder and picks one at random
2. Resizes/crops it to 1920×1080 (centre crop, aspect-ratio safe)
3. Writes a valid DBPF 2.0 `.package` file with the correct resource key
4. Copies it to your Mods folder, replacing the previous random screen

The output file is called `RandomLoadingScreen.package`. It won't conflict
with other mods as long as you don't have another loading screen `.package`
in your Mods folder.

> **Note:** Only ONE loading screen `.package` can be active at a time. If you
> have another custom loading screen mod installed, remove it first.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `[ERROR] Images folder not found` | Update `IMAGES_FOLDER` in the script |
| `[ERROR] Mods folder not found` | Update `MODS_FOLDER` in the script |
| `[ERROR] No images found` | Check the folder path and file formats |
| Loading screen unchanged in game | Delete `localthumbcache.package` from your Mods folder, then relaunch |
| Game still shows blue loading screen | Ensure no other loading screen `.package` exists in Mods |
| Python not found | Install Python and tick "Add to PATH" |

---

## Image tips

- **Resolution:** 1920×1080 recommended; the script resizes automatically
- **Format:** PNG gives best quality; JPG works fine too
- **Count:** Works with as few as 1 image or thousands
- **Variety:** The more images you add, the more variety you get!
