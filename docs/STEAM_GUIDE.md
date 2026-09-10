# Steam Artwork Guide

This project ships a full set of custom Steam library artwork for the
non-Steam-game shortcut, in `assets/steam/`, sized to Steam's current
library grid requirements.

## Asset list

| File | Size | Steam slot |
|---|---|---|
| `cover_dark.png` / `cover_light.png` | 600×900 | Portrait grid capsule |
| `wide_cover_dark.png` / `wide_cover_light.png` | 920×430 | Landscape grid capsule |
| `background_dark.png` / `background_light.png` | 3840×1240 | Library hero |
| `logo_dark.png` / `logo_light.png` | 1280×720 | Library logo (transparent background) |

Each slot has a **dark** version and a **light** version — pick whichever
looks better against your own Steam library theme/background; both work
for either the `Sims4RandomLoadingScreen`/`.exe` or `TS4_x64`/`.exe`
shortcut. (`TS4_x64`'s own executable icon is a separate, plumbob-style
icon that mimics Sims 4's own game icon — see `assets/icon_curseforge.*` —
unrelated to which Steam artwork set you pick here.)

Don't have the source repo? The app's **About** tab has a
**Save Steam artwork (.zip)...** button that saves this same set anywhere
you like.

## Applying the artwork

1. Add the executable (`Sims4RandomLoadingScreen.exe` or `TS4_x64.exe`) to
   Steam as a non-Steam game:
   **Steam → Games → Add a Non-Steam Game to My Library**.
2. In your Library, right-click the new entry → **Manage** →
   **Set custom artwork**, and upload the matching file from
   `assets/steam/` (or the zip from the About tab) for each slot
   (grid, hero, logo).

For the full walkthrough with screenshots, see this community guide:
[Adding custom artwork to non-Steam games](https://steamcommunity.com/sharedfiles/filedetails/?id=3582792038).
