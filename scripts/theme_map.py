#!/usr/bin/env python3
"""theme_map.py — 让 SVG 长卷真正吃 palette。

问题：24 个内置 motif 里有 41 个硬编码十六进制色
（叶子的 #C3D6AF、铅笔的 #E9B776……），改 story.json 的 palette 只换得掉
墨线/底色，叶子还是春天绿。做红白风、万圣节暗调时会一眼穿帮。

做法：不碰原库，编译后按「色相家族」重映射。
  - 绿系 (hue 70–170)    → palette.sage
  - 暖橙/琥珀 (25–65)     → palette.orange
  - 粉/珊瑚 (330–360,0–20) → palette.rose
  - 冷灰蓝 (170–250)      → palette.sky
  - 高亮低饱和（奶油）     → palette.light
  - 暗色 (L<0.32)         → palette.ink
映射时保留原色的明度差（阴影/高光关系不丢），只替换色相与饱和基准。

用法：
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
    # 保留原色的明度差，但夹住范围：否则浅粉类颜色会被压成近白，形体消失
    new_l = max(max(0.03, tl - 0.34), min(min(0.97, tl + 0.18), tl + (l - ref_l) * 0.85))
    # 饱和度不低于目标色的 45%，保证「红就是红」，不会褪成灰
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
        print("重映射 %d 种颜色（palette: %s）" % (len(mapping), json.dumps(palette, ensure_ascii=False)))
        for fam in sorted(fams):
            items = fams[fam][:6]
            print("  %-6s %2d 种：" % (fam, len(fams[fam])) +
                  ", ".join("%s→%s" % (x, y) for x, y in items))
        residual = [c for c in set(HEX_RE.findall(out))
                    if classify(colorsys.rgb_to_hls(*hex_to_rgb(c))[0:1] + colorsys.rgb_to_hls(*hex_to_rgb(c))[1:])
                    in ("sage", "orange") and c.upper() not in {v.upper() for v in palette.values()}]
        print("  映射后仍留在绿/橙家族的颜色：%d 种" % len(residual))
    print("→ %s" % a.output)


if __name__ == "__main__":
    sys.exit(main())
