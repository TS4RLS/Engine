"""One-off generator for assets/icon.png, assets/icon.ico, assets/icon.icns,
assets/logo.png, and the sibling Website repo's matching icon.png,
logo.png, and favicon.ico.

Run with: python src/build/create_project_assets.py
Requires Pillow (dev-only; not a runtime dependency of the app itself).

Reproduces the existing hand-made icon/logo in code: three "photo frame"
diamonds (a loading-screen thumbnail motif - a little scene with a sun/moon
dot and a tree/mountain) arranged diagonally on a green rounded square.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parent.parent.parent / "assets"
ASSETS.mkdir(exist_ok=True)

# Sibling Website repo's assets/ - gets its own copy of icon.png/logo.png
# (so the site never drifts out of sync with the app's branding) plus
# favicon.ico, which is a Website-only asset that has no business living
# in this repo.
WEBSITE_ASSETS = Path(__file__).resolve().parent.parent.parent.parent / "Website" / "assets"

BG = (46, 125, 50, 255)      # green 800 - background, and the wordmark text
DARK = (27, 94, 32, 255)     # green 900 - diamond frames and the tree
WHITE = (255, 255, 255, 255)
LIGHT = (139, 195, 74, 255)  # light green 500 - the dot in each frame

FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"

TILE_COUNT = 3
TILE_SIZE_FRAC = 0.339      # each diamond tile's square bounding box, of `size`
TILE_START_FRAC = 0.069     # first tile's top-left corner, of `size`
TILE_STEP_FRAC = 0.260      # diagonal offset between tiles, of `size`
INNER_DIAMOND_RATIO = 0.7233  # inner (white) diamond's half-diagonal / outer's
TREE_APEX_FRAC = 0.441      # of tile size, from the tile's top edge
TREE_BASE_FRAC = 0.740
TREE_BASE_HALF_WIDTH_FRAC = 0.1412  # of tile size
DOT_CENTER_FRAC = 0.40      # of tile size, from the tile's top-left corner
DOT_RADIUS_FRAC = 0.06      # of tile size


def draw_tile(draw: ImageDraw.ImageDraw, ox: float, oy: float, ts: float) -> None:
    """One diamond "photo frame" tile at (ox, oy), ts x ts."""
    cx, cy = ox + ts / 2, oy + ts / 2
    outer_r = ts / 2
    inner_r = outer_r * INNER_DIAMOND_RATIO

    draw.polygon(
        [(cx, cy - outer_r), (cx + outer_r, cy), (cx, cy + outer_r), (cx - outer_r, cy)],
        fill=DARK,
    )
    draw.polygon(
        [(cx, cy - inner_r), (cx + inner_r, cy), (cx, cy + inner_r), (cx - inner_r, cy)],
        fill=WHITE,
    )

    apex_y = oy + ts * TREE_APEX_FRAC
    base_y = oy + ts * TREE_BASE_FRAC
    base_half = ts * TREE_BASE_HALF_WIDTH_FRAC
    draw.polygon([(cx, apex_y), (cx - base_half, base_y), (cx + base_half, base_y)], fill=DARK)

    dot_r = ts * DOT_RADIUS_FRAC
    dot_cx = ox + ts * DOT_CENTER_FRAC
    dot_cy = oy + ts * DOT_CENTER_FRAC
    draw.ellipse([dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r], fill=LIGHT)


def draw_glyph(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    radius = size * 0.185
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=BG)

    tile_size = size * TILE_SIZE_FRAC
    for i in range(TILE_COUNT):
        offset = size * TILE_START_FRAC + i * size * TILE_STEP_FRAC
        draw_tile(draw, offset, offset, tile_size)

    return img


def draw_wordmark() -> Image.Image:
    width, height = 1102, 300
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    icon_size = 236
    icon = draw_glyph(icon_size)
    icon_y = (height - icon_size) // 2
    img.paste(icon, (19, icon_y), icon)

    text_x = 19 + icon_size + 30

    acronym_font = ImageFont.truetype(FONT_BOLD, 140)
    acronym = "TS4RLS"
    acronym_bbox = draw.textbbox((0, 0), acronym, font=acronym_font)
    acronym_top = icon_y - 6
    draw.text(
        (text_x, acronym_top - acronym_bbox[1]),
        acronym,
        font=acronym_font,
        fill=BG,
    )

    tagline_font = ImageFont.truetype(FONT_BOLD, 34)
    tagline = "The Sims 4 Random Loading Screen"
    tagline_top = acronym_top + (acronym_bbox[3] - acronym_bbox[1]) + 14
    draw.text(
        (text_x, tagline_top),
        tagline,
        font=tagline_font,
        fill=BG,
    )

    return img


def main() -> None:
    logo = draw_wordmark()
    logo.save(ASSETS / "logo.png")

    icon_sizes = [16, 24, 32, 48, 64, 128, 256]
    icon_base = draw_glyph(256)
    icon_base.save(ASSETS / "icon.png")
    icon_base.save(ASSETS / "icon.ico", sizes=[(s, s) for s in icon_sizes])

    icon_hires = draw_glyph(1024)
    icon_hires.save(ASSETS / "icon.icns")

    print(
        f"Wrote {ASSETS / 'logo.png'}, {ASSETS / 'icon.png'}, "
        f"{ASSETS / 'icon.ico'}, {ASSETS / 'icon.icns'}"
    )

    # The website gets its own copies of icon.png/logo.png (kept in sync
    # with the app's own branding) plus favicon.ico, which isn't used by
    # the Engine app itself - it's only for the Website repo's
    # <link rel="shortcut icon">. icon_hires (not icon_base) is used for
    # the website's icon.png since it's already published there at
    # 1024x1024 - reusing icon_base would silently downgrade it to 256x256.
    if WEBSITE_ASSETS.is_dir():
        favicon_sizes = [16, 32, 48]
        icon_base.save(WEBSITE_ASSETS / "favicon.ico", sizes=[(s, s) for s in favicon_sizes])
        icon_hires.save(WEBSITE_ASSETS / "icon.png")
        logo.save(WEBSITE_ASSETS / "logo.png")
        print(
            f"Wrote {WEBSITE_ASSETS / 'favicon.ico'}, "
            f"{WEBSITE_ASSETS / 'icon.png'}, {WEBSITE_ASSETS / 'logo.png'}"
        )
    else:
        print(f"Skipped Website assets - no sibling checkout at {WEBSITE_ASSETS}")


if __name__ == "__main__":
    main()
