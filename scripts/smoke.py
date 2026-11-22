#!/usr/bin/env python3
"""smoke.py — 浏览器长卷的无头体检（撑高曲线 + 横向溢出 + 控制台报错）。

只做结构判断，不做美术判断：
  · body 高度是否随时间单调增长（撑高器接不上会跳一下）
  · 是否出现横向滚动（超宽撑高 svg 常见）
  · 是否有 JS 报错
输出 JSON 到 stdout。
"""
import asyncio
import json
import os
import sys
from pathlib import Path

TIMES = [0, 3, 8, 13, 18, 24, 30]
EXE = "/root/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome"


async def probe(path, times, width=440, height=900):
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        kw = {"args": ["--no-sandbox"]}
        if os.path.exists(EXE):
            kw["executable_path"] = EXE
        b = await p.chromium.launch(**kw)
        pg = await b.new_page(viewport={"width": width, "height": height})
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.on("console", lambda m: errors.append("console: " + m.text) if m.type == "error" else None)
        await pg.goto("file://" + str(Path(path).resolve()))
        await pg.wait_for_timeout(300)

        curve = []
        for t in times:
            await pg.evaluate(
                "(t)=>document.querySelectorAll('svg').forEach(s=>{"
                "s.pauseAnimations&&s.pauseAnimations();s.setCurrentTime&&s.setCurrentTime(t)})", t)
            await pg.wait_for_timeout(160)
            h = await pg.evaluate("document.body.scrollHeight")
            hs = await pg.evaluate(
                "document.documentElement.scrollWidth > document.documentElement.clientWidth + 1")
            curve.append({"t": t, "height": h, "hscroll": hs})

        scripts = await pg.evaluate("document.querySelectorAll('script').length")
        styles = await pg.evaluate("document.querySelectorAll('style').length")
        await b.close()

    heights = [c["height"] for c in curve]
    return {
        "curve": curve,
        "monotonic": all(b >= a - 2 for a, b in zip(heights, heights[1:])),
        "any_hscroll": any(c["hscroll"] for c in curve),
        "grew": heights[-1] > heights[0] * 2,
        "script_tags": scripts,
        "style_tags": styles,
        "errors": errors[:5],
    }


def main():
    if len(sys.argv) < 2:
        sys.exit("用法: smoke.py <html> [秒,秒,...]")
    times = TIMES
    if len(sys.argv) > 2:
        times = [float(x) for x in sys.argv[2].split(",")]
    res = asyncio.run(probe(sys.argv[1], times))
    print(json.dumps(res, ensure_ascii=False, indent=2))
    ok = res["monotonic"] and not res["any_hscroll"] and res["grew"] and not res["errors"]
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
