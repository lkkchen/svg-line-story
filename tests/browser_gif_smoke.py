#!/usr/bin/env python3
"""Optional real Chromium GIF cue/replay test (requires Playwright + Chromium).

Usage: python3 tests/browser_gif_smoke.py [path/to/index.html] [output-preview.png]
"""
from pathlib import Path
import json
import os
import sys
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print('SKIP: pip install playwright; playwright install chromium')
    sys.exit(0)

ROOT=Path(__file__).resolve().parents[1]
PAGE=Path(sys.argv[1] if len(sys.argv)>1 else ROOT/'examples/spring/dist/index.html').resolve()
OUT=Path(sys.argv[2] if len(sys.argv)>2 else Path(os.environ.get('TMPDIR','/tmp'))/'svg-story-gif-preview.png').resolve()
OUT.parent.mkdir(parents=True,exist_ok=True)
CUES=json.loads((PAGE.parent/'cues.json').read_text())
DECORS=CUES['gifDecorations']
assert len(DECORS)>=2,'Test requires GIF-enabled example'

with sync_playwright() as p:
    chromium='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None
    browser=p.chromium.launch(headless=True,executable_path=chromium,args=['--allow-file-access-from-files'])
    page=browser.new_page(viewport={'width':440,'height':850},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(PAGE.read_text(encoding='utf8'),wait_until='load')
    page.evaluate('''() => { document.getElementById('story-svg').pauseAnimations(); document.getElementById('grow-svg').pauseAnimations(); }''')
    def seek(t):
        page.evaluate('''(t) => {document.getElementById('story-svg').setCurrentTime(t);
                       document.getElementById('grow-svg').setCurrentTime(t)}''',t)
        page.wait_for_timeout(180)
    def gif_src(ident):
        return page.locator('#gif-image-'+ident).get_attribute('href')
    def gif_opacity(ident):
        return float(page.locator('#gif-decor-'+ident).evaluate('(el)=>getComputedStyle(el).opacity'))
    seek(0.1)
    assert not any(gif_src(d['id']) for d in DECORS), 'GIF decoded before cue'
    first=DECORS[0]
    seek(first['begin']+.35)
    href_one=gif_src(first['id'])
    assert href_one and href_one.startswith('blob:'), 'GIF was not mounted on cue'
    assert gif_opacity(first['id'])>.3,'GIF visibility SMIL did not begin'
    page.screenshot(path=str(OUT),full_page=True)
    seek(first['end']+.1)
    assert not gif_src(first['id']), 'GIF was not detached after active interval'
    seek(first['begin']+.35)
    href_two=gif_src(first['id'])
    assert href_two and href_two.startswith('blob:') and href_two!=href_one, 'Seek must create fresh GIF decoder'
    seek(0)
    assert not gif_src(first['id']), 'Rewind must clear GIF'
    # Check the other accents are not preloaded and mount at their own arrival.
    for d in DECORS[1:]:
        seek(d['begin']+.2)
        assert gif_src(d['id']) and gif_src(d['id']).startswith('blob:'),(d['id'],gif_src(d['id']))
        assert page.evaluate('document.documentElement.scrollWidth')<=442, 'Horizontal overflow'
        seek(d['end']+.05)
        assert not gif_src(d['id']),d['id']
    assert not errors,errors
    print('PASS browser GIF cue/start-once/seek/replay/end; GIF count',len(DECORS),'preview:',OUT)
    page.close();browser.close()
