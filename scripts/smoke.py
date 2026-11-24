#!/usr/bin/env python3
"""smoke.py — headless check for a browser scroll (growth curve, horizontal overflow, console errors).

Structure only, not art direction:
  · whether body height grows monotonically (a broken spacer jumps)
  · whether the page scrolls sideways (a grow SVG that is too wide often does)
  · whether JavaScript reports an error
Prints JSON to stdout.
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
        sys.exit("Usage: smoke.py <html> [seconds,seconds,...]")
    times = TIMES
    if len(sys.argv) > 2:
        times = [float(x) for x in sys.argv[2].split(",")]
    res = asyncio.run(probe(sys.argv[1], times))
    print(json.dumps(res, ensure_ascii=False, indent=2))
    ok = res["monotonic"] and not res["any_hscroll"] and res["grew"] and not res["errors"]
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
