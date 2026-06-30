"""Generate menu-bar template icons: a coffee cup, plus steam-animation frames.

Outputs into icons/:
  cup_off.png        — cup, no steam (idle state)
  cup_on_0..3.png    — cup with steam at 4 animation phases (caffeinated state)

Template images = black shapes on transparent; macOS auto-tints them for light/dark
menu bars. Rendered at 2x (36px) for retina; rumps shows them at ~18pt.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

ICONS = Path(__file__).resolve().parent / "icons"
S = 36  # 2x canvas (18pt menu bar)
BLACK = (0, 0, 0, 255)


def draw_cup(d: ImageDraw.ImageDraw) -> None:
    """A small espresso cup with a handle, centered horizontally, sitting low."""
    # cup body: slightly tapered, rounded bottom
    left, right, top, bottom = 9, 25, 20, 31
    d.rounded_rectangle([left, top, right, bottom], radius=3, fill=BLACK)
    # saucer
    d.rounded_rectangle([7, 32, 27, 34], radius=1, fill=BLACK)
    # handle (right side) — drawn as an arc ring, then punch the inside
    d.arc([23, 21, 31, 29], start=300, end=60, fill=BLACK, width=2)


def steam_wave(d: ImageDraw.ImageDraw, x0: int, phase: float) -> None:
    """A wavy vertical steam wisp rising from the cup, animated by `phase`."""
    pts = []
    for i in range(0, 13):
        y = 17 - i  # rise from y~17 up to y~5
        x = x0 + 2.0 * math.sin((i / 2.4) + phase)
        pts.append((x, y))
    d.line(pts, fill=BLACK, width=2, joint="curve")


def render(steam: bool, phase: float, out: Path) -> None:
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if steam:
        steam_wave(d, 14, phase)
        steam_wave(d, 20, phase + 1.7)
    draw_cup(d)
    img.save(out)


def main() -> None:
    ICONS.mkdir(exist_ok=True)
    render(False, 0.0, ICONS / "cup_off.png")
    for i in range(4):
        render(True, i * (math.pi / 2), ICONS / f"cup_on_{i}.png")
    print(f"wrote icons to {ICONS}")


if __name__ == "__main__":
    main()
