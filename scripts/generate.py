#!/usr/bin/env python3
"""Build themes/Kanagawa-<Variant>/: the Vimix cursors (src/) recolored by palette role.

Dark variants start from src/svg (dark body, light outline), light ones from src/svg-white.
Each source colour is swapped for a palette role, the SVGs are rendered with rsvg-convert,
and xcursorgen packs them using Vimix's own src/config and src/cursorList.

Usage: scripts/generate.py [path/to/palette.json]   (default: ../.github/palette.json)
Needs rsvg-convert (librsvg) and xcursorgen (xorg-xcursorgen).
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
VARIANTS = ["wave", "dragon", "lotus"]
# Vimix renders each nominal size (24, 30, 36, 48 in src/config) at these pixel sizes.
SIZES = {"x1": 32, "x1_25": 40, "x1_5": 48, "x2": 64}

# Body and outline, per source set: the dark set has a dark body and light outline,
# the white set the other way round. Either way the body becomes ui.bg, the outline ui.fg.
BASE = {
    "svg": {"#333333": "ui.bg", "#ffffff": "ui.fg"},
    "svg-white": {"#ffffff": "ui.bg", "#323232": "ui.fg"},
}
# Everything else, the same in both sets.
ACCENTS = {
    "#151515": "ui.bg_m3",  # inner details (text, cell, dnd)
    "#1a1a1a": "ui.bg_m3",
    "#dcdcdc": "ui.fg_dim",  # light parts (pencil, zoom, x-cursor)
    "#cecece": "ui.fg_dim",
    "#c7c7c7": "ui.fg_dim",
    "#1976d2": "syn.fun",  # resize dots, spinner
    "#4caf50": "term.green",  # copy badge, spinner
    "#38d83c": "syn.string",  # copy plus
    "#ffc107": "diag.warning",  # help badge, spinner
    "#ff3d00": "term.red",  # spinner
    "#ed1515": "diag.error",  # not-allowed, no-drop
    "#ff2a2a": "diag.error",  # pirate
    "#f67400": "syn.constant",  # x-cursor, wayland-cursor
    # wait/progress spinner segments: light and dark shade of each hue
    "#ff645d": "syn.special3",
    "#ff4332": "syn.preproc",
    "#ff9508": "syn.constant",
    "#fbb114": "diag.warning",
    "#ffd305": "syn.identifier",
    "#fdcf01": "term.yellow",
    "#52cf30": "syn.string",
    "#3bbd1c": "term.green",
    "#14adf6": "syn.special1",
    "#1191f4": "syn.fun",
    "#ca70e1": "syn.number",
    "#b452cb": "syn.statement",
}
# Left as they are: the drop shadow, and Inkscape's editor border colour (not drawn).
KEEP = {"#000000", "#666666"}
HEX = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")


def roles(variant):
    """Map each role to its hex; a role missing from the palette raises KeyError later."""
    return {role: color["hex"] for color in variant["colors"].values() for role in color["usage"]}


def recolor(svg, mapping):
    def swap(m):
        h = m[0].lower()
        if len(h) == 4:  # #fff -> #ffffff
            h = "#" + "".join(c * 2 for c in h[1:])
        if h in KEEP:
            return m[0]
        if h not in mapping:
            raise SystemExit(f"unmapped colour {h}; add it to ACCENTS or KEEP")
        return mapping[h]

    return HEX.sub(swap, svg)


def build(name, source, mapping, out):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for svg in sorted((SRC / source).glob("*.svg")):
            text = recolor(svg.read_text(), mapping)
            for folder, px in SIZES.items():
                (tmp / folder).mkdir(exist_ok=True)
                subprocess.run(["rsvg-convert", "-w", str(px), "-h", str(px), "-o", tmp / folder / f"{svg.stem}.png"],
                               input=text.encode(), check=True)
        shutil.rmtree(out, ignore_errors=True)
        (out / "cursors").mkdir(parents=True)
        for config in sorted((SRC / "config").glob("*.cursor")):
            # configs name their images relative to the folder they run in (x1/default.png)
            subprocess.run(["xcursorgen", config, out / "cursors" / config.stem], cwd=tmp, check=True)
    # cursorList: "<alias> <existing cursor>" per line, as Vimix's build.sh reads it
    for line in (SRC / "cursorList").read_text().splitlines():
        alias, target = line.split(" ", 1)
        link = out / "cursors" / alias
        if not link.exists():
            link.symlink_to(target)
    (out / "index.theme").write_text(f"[Icon Theme]\nName={name}\nComment=Vimix cursors in Kanagawa colors\n")
    # The theme is installed on its own, so it carries the GPL text with it.
    shutil.copy(ROOT / "LICENSE", out / "LICENSE")


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / ".github" / "palette.json"
    variants = json.loads(path.read_text())["variants"]
    for v in VARIANTS:
        r = roles(variants[v])
        source = "svg" if variants[v]["appearance"] == "dark" else "svg-white"
        mapping = {h: r[role] for h, role in {**BASE[source], **ACCENTS}.items()}
        out = ROOT / "themes" / f"Kanagawa-{v.capitalize()}"
        build(f"Kanagawa {v.capitalize()}", source, mapping, out)
        print(out.relative_to(ROOT))


if __name__ == "__main__":
    main()
