# Steam Artwork Guide

This project ships a full set of custom Steam library artwork for the
non-Steam-game shortcut, in `assets/steam/`, sized to Steam's current
library grid requirements.

## Asset list

| File | Size | Steam slot |
|---|---|---|
| `cover.png` | 600×900 | Portrait grid capsule |
| `wide_cover.png` | 920×430 | Landscape grid capsule |
| `background.png` | 3840×1240 | Library hero |
| `logo.png` | 1280×720 | Library logo (transparent background) |

Each of these also has an `_alt` version (e.g. `cover_alt.png`) that uses
the CurseForge-launcher branding (`assets/alt_icon.*`) instead of the
standard one. Use whichever matches the shortcut you're skinning:

- Standard set → `Launcher.exe` / `Launcher` shortcut
- `_alt` set → `TS4_x64.exe` (CurseForge pre-launch) shortcut

## Applying the artwork

1. Add the executable (`Launcher.exe` or `TS4_x64.exe`) to Steam as a
   non-Steam game: **Steam → Games → Add a Non-Steam Game to My Library**.
2. In your Library, right-click the new entry → **Manage** →
   **Set custom artwork**, and upload the matching file from
   `assets/steam/` for each slot (grid, hero, logo).

For the full walkthrough with screenshots, see this community guide:
[Adding custom artwork to non-Steam games](https://steamcommunity.com/sharedfiles/filedetails/?id=3582792038).
