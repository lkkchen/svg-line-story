#!/usr/bin/env python3
"""theme_map.py — make an SVG scroll actually use its palette.

Problem: 24 built-in motifs contain 41 hardcoded hex colors
(a leaf's #C3D6AF, a pencil's #E9B776, and so on). Changing palette
in story.json only recolors the ink line and the paper. The leaf stays
spring green. A red-and-white story, or a dark Halloween one, shows it at once.

What it does: leave the motif library alone, then remap by hue family after compile.
  - greens (hue 70–170)       → palette.sage
  - warm orange / amber (25–65) → palette.orange
  - pink / coral (330–360, 0–20) → palette.rose
  - cool gray-blue (170–250)  → palette.sky
  - bright and low-saturation (cream) → palette.light
  - dark (L<0.32)             → palette.ink
The remap keeps the original lightness gaps, so shadows and highlights stay.
Only the hue and the saturation base change.

Usage:
  python3 theme_map.py <in.html|svg> <out> --story story.json [--report]
"""
import argparse
import colorsys
import json
import re
import sys
from pathlib import Path

HEX_RE = re.compile(r"#[0-9A-Fa-f]{6}\b")


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def rgb_to_hex(r, g, b):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(v * 255))) for v in (r, g, b))


def classify(hls):
    h, l, s = hls
    deg = h * 360
    if l < 0.32:
        return "ink"
    if s < 0.12:
        return "light" if l > 0.85 else "sky"
    if 70 <= deg <= 175:
        return "sage"
    if 25 <= deg < 70:
        return "orange"
    if deg >= 330 or deg < 22:
        return "rose"
    if 175 <= deg < 260:
        return "sky"
    return "light"


def remap(color, palette, ref_l=0.62):
    rgb = hex_to_rgb(color)
    h, l, s = colorsys.rgb_to_hls(*rgb)
    family = classify((h, l, s))
    target = palette.get(family)
    if not target:
        return color, family
    th, tl, ts = colorsys.rgb_to_hls(*hex_to_rgb(target))
    # Keep the original lightness gap, but clamp it. Otherwise a pale pink collapses toward white and the shape disappears.
    new_l = max(max(0.03, tl - 0.34), min(min(0.97, tl + 0.18), tl + (l - ref_l) * 0.85))
    # Saturation stays at least 45% of the target, so a red stays red instead of fading to gray.
    new_s = max(ts * 0.45, min(1.0, ts * (0.55 + 0.9 * s)))
    r, g, b = colorsys.hls_to_rgb(th, new_l, new_s)
    return rgb_to_hex(r, g, b), family


def run(html, palette, report=False):
    mapping, fams = {}, {}
    for c in set(HEX_RE.findall(html)):
        low = c.upper()
        if low in {v.upper() for v in palette.values()}:
            continue
        new, fam = remap(low, palette)
        if new.upper() != low:
            mapping[c] = new
            fams.setdefault(fam, []).append((low, new))

    def sub(m):
        return mapping.get(m.group(0), mapping.get(m.group(0).upper(), m.group(0)))

    out = HEX_RE.sub(sub, html)
    return out, mapping, fams


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--story", required=True)
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()

    palette = json.loads(Path(a.story).read_text(encoding="utf8"))["palette"]
    html = Path(a.input).read_text(encoding="utf8")
    out, mapping, fams = run(html, palette)

    Path(a.output).parent.mkdir(parents=True, exist_ok=True)
    Path(a.output).write_text(out, encoding="utf8")

    if a.report:
        print("Remapped %d colors (palette: %s)" % (len(mapping), json.dumps(palette, ensure_ascii=False)))
        for fam in sorted(fams):
            items = fams[fam][:6]
            print("  %-6s %2d colors: " % (fam, len(fams[fam])) +
                  ", ".join("%s→%s" % (x, y) for x, y in items))
        residual = [c for c in set(HEX_RE.findall(out))
                    if classify(colorsys.rgb_to_hls(*hex_to_rgb(c))[0:1] + colorsys.rgb_to_hls(*hex_to_rgb(c))[1:])
                    in ("sage", "orange") and c.upper() not in {v.upper() for v in palette.values()}]
        print("  Colors still in the green or orange family after remapping: %d" % len(residual))
    print("→ %s" % a.output)


if __name__ == "__main__":
    sys.exit(main())
