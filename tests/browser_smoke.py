#!/usr/bin/env python3
"""Optional integration test. Needs playwright + an installed Chromium, but core skill does not."""
from pathlib import Path
import os, sys, json
try:
 from playwright.sync_api import sync_playwright
except ImportError:
 print('SKIP: pip install playwright; python -m playwright install chromium');sys.exit(0)
ROOT=Path(__file__).resolve().parents[1]
PAGE=Path(sys.argv[1] if len(sys.argv)>1 else ROOT/'examples/spring/dist/index.html').resolve()
OUT=Path(sys.argv[2] if len(sys.argv)>2 else Path(os.environ.get('TMPDIR','/tmp'))/'svg-story-preview.png').resolve()
OUT.parent.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,args=['--allow-file-access-from-files'])
 for width,height in [(440,850),(1280,860)]:
  page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
  errors=[]
  page.on('pageerror',lambda e: errors.append(str(e)))
  page.set_content(PAGE.read_text(encoding="utf8"),wait_until="load")
  page.wait_for_timeout(800)
  samples=[]
  for t in [0,6,12,18,26,31.9]:
   page.evaluate("(t)=>{document.getElementById('story-svg').setCurrentTime(t);document.getElementById('grow-svg').setCurrentTime(t)}",t)
   page.wait_for_timeout(100)
   info=page.evaluate("""() => ({stageHeight:document.getElementById('stage').getBoundingClientRect().height, pageWidth:document.documentElement.scrollWidth, viewport:innerWidth,svgTime:document.getElementById('story-svg').getCurrentTime(), path:document.querySelector('[id^=line-]').getAttribute('stroke-dasharray')})""")
   assert info['pageWidth']<=width+2,(width,t,info)
   samples.append((t,round(info['stageHeight'],1)))
  assert all(b[1]>=a[1]-2 for a,b in zip(samples,samples[1:])),samples
  assert not errors,errors
  print('PASS',width,'stage heights=',samples)
  if width==440:
   page.evaluate("() => {document.getElementById('btn-follow').click();document.getElementById('story-svg').setCurrentTime(31.9);document.getElementById('grow-svg').setCurrentTime(31.9)}")
   page.wait_for_timeout(350)
   page.screenshot(path=str(OUT),full_page=True)
   print('screenshot',OUT)
  page.close()
 browser.close()
