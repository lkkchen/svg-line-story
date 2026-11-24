#!/usr/bin/env python3
"""Regression tests for optional transparent GIF accents."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from compile_story import prepare, grow_schedule, story_svg, render_html
from gif_decor import gif_info, load_decorations
from plan_story import plan
from validate_story import validate

def once_gif(frames=24, delay_cs=9, width=2, height=2):
    """Transparent GIF89a with no loop extension. Kept in source so the skill ships no binary assets."""
    header=b'GIF89a'
    logical=width.to_bytes(2,'little')+height.to_bytes(2,'little')+bytes([0x80,0,0])
    palette=bytes([0,0,0,55,87,99])
    body=b''
    for _ in range(frames):
        gce=bytes([0x21,0xF9,0x04,0x01,delay_cs & 255,(delay_cs>>8)&255,0,0])
        desc=bytes([0x2C,0,0,0,0])+width.to_bytes(2,'little')+height.to_bytes(2,'little')+bytes([0])
        body+=gce+desc+bytes([2,2,0x4C,0x01,0])
    return header+logical+palette+body+b'\x3B'

SAMPLE_DECORS={
    'awakening':[{'id':'sprout-sparkles','src':'assets/sprout-sparkles.gif','attachTo':'seedlet','offset':[-93,-155],'width':155,'height':104,'trigger':{'hit':'seedlet'},'playback':'once','z':'front'}],
    'blooming':[{'id':'bloom-petals','src':'assets/petal-drift.gif','attachTo':'blossom','offset':[-55,-140],'width':180,'height':125,'trigger':{'hit':'blossom'},'playback':'once','z':'front'}],
    'journey':[{'id':'boat-water-ripples','src':'assets/boat-ripples.gif','attachTo':'paperboat','offset':[-100,-30],'width':215,'height':123,'trigger':{'hit':'paperboat'},'playback':'once','z':'front'}],
}

class GifDecorationTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.source=Path(tmp.name)
        assets=self.source/'assets'
        assets.mkdir()
        blob=once_gif()
        self.story=json.loads((ROOT/'examples/spring/story.json').read_text(encoding='utf8'))
        for chapter in self.story['chapters']:
            decors=SAMPLE_DECORS.get(chapter['id'])
            if not decors: continue
            chapter['gifDecorations']=decors
            for item in decors:
                (self.source/item['src']).write_bytes(blob)
        self.prepared=prepare(self.story)
        self.decors=load_decorations(self.story,self.prepared,self.source)

    def test_gifs_are_transparent_once_and_small(self):
        self.assertEqual(len(self.decors),3)
        for item in self.decors:
            self.assertLess(len(item['bytes']),100_000)
            info=gif_info(item['bytes'])
            self.assertTrue(info['transparent'])
            self.assertIsNone(info['loopCount'])
            self.assertEqual(info['frames'],24)
            self.assertAlmostEqual(info['naturalSeconds'],2.16,2)

    def test_cue_uses_route_arrival_not_early_reveal(self):
        arrivals={c['object']:c['lineArrival'] for c in self.prepared['connections']}
        for d in self.decors:
            pin=d['trigger']['hit']
            self.assertAlmostEqual(d['begin'],arrivals[pin],2)
            anchor=self.prepared['objects'][d['attachTo']]['anchor']
            self.assertAlmostEqual(d['x'],anchor[0]+d['offset'][0])
            self.assertAlmostEqual(d['y'],anchor[1]+d['offset'][1])

    def test_browser_only_mounts_gif_when_triggered(self):
        html=render_html(self.story,self.prepared,grow_schedule(self.story,self.prepared),decorations=self.decors)
        self.assertIn('function startGif(d)',html)
        self.assertIn('URL.createObjectURL',html)
        self.assertIn('id="gif-image-sprout-sparkles"',html)
        # Placeholder image has no URI prior to JS event.
        imgstart=html.index('id="gif-image-sprout-sparkles"')
        self.assertNotIn(' href=',html[imgstart:imgstart+190])
        # Decoded GIF stored separately in JS config; never fetch remote assets.
        self.assertIn('const GIF_ACCENTS=',html)
        self.assertNotIn('<script src=',html)

    def test_svg_mainline_preserved(self):
        art=story_svg(self.story,self.prepared,decorations=self.decors)
        self.assertIn('stroke-dashoffset',art)
        self.assertIn('animateMotion',art)
        self.assertEqual(art.count('<image '),3)
        self.assertIn('data:image/gif;base64,',art)

    def test_local_assets_required_traversal_forbidden(self):
        unsafe=copy.deepcopy(self.story)
        unsafe['chapters'][0]['gifDecorations'][0]['src']='../../somewhere.gif'
        with self.assertRaises(ValueError):load_decorations(unsafe,prepare(unsafe),self.source)

    def test_dangling_trigger_rejected(self):
        unsafe=copy.deepcopy(self.story)
        unsafe['chapters'][0]['gifDecorations'][0]['trigger']={'hit':'not-on-path'}
        with self.assertRaises(ValueError):load_decorations(unsafe,prepare(unsafe),self.source)

    def test_validator_checks_assets(self):
        errors,warnings,report=validate(self.story,self.source)
        self.assertFalse(errors)
        self.assertEqual(report['gifDecorations'],3)

    def test_theme_drafts_do_not_copy_spring_gifs(self):
        story=plan('a train through the forest')
        self.assertEqual(sum(len(ch.get('gifDecorations',[])) for ch in story['chapters']),0)

if __name__=='__main__':unittest.main(verbosity=2)
