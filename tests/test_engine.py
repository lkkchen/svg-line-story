#!/usr/bin/env python3
"""pytest-free unit smoke tests for the reusable renderer."""
import copy, json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from compile_story import prepare, valid_story, render_html, story_svg, grow_schedule, custom_markup
from motifs import motif_markup
from arcs import motions_for, resolve_arc, suggest_arc
from palettes import PALETTES, contrast, resolve_palette, suggest
from plan_story import plan
from validate_story import validate

class StoryTests(unittest.TestCase):
    def setUp(self):self.story=json.loads((ROOT/'examples/spring/story.json').read_text(encoding='utf8'))
    def test_pins_and_growth(self):
        p=prepare(self.story)
        self.assertEqual(len(p['segments']),3)
        self.assertTrue(all(e['pathPointError']==0 for e in p['connections']))
        grow=grow_schedule(self.story,p)
        self.assertEqual(grow[-1]['visibleDesignHeight'],4050)
        self.assertTrue(all(grow[i]['to']<=grow[i+1]['to'] for i in range(len(grow)-1)))
    def test_pure_svg(self):
        p=prepare(self.story);markup=story_svg(self.story,p)
        self.assertIn('animateMotion',markup)
        self.assertIn('stroke-dashoffset',markup)
        self.assertNotIn('<image',markup)
        self.assertNotIn('<script',markup)
    def test_browser_reduced_motion_hold(self):
        p=prepare(self.story)
        doc=render_html(self.story,p,grow_schedule(self.story,p))
        self.assertIn('prefers-reduced-motion: reduce', doc)
        self.assertIn('Play from the start', doc)
        self.assertIn('id="dock-peek"', doc)
        self.assertIn('DOCK_IDLE_MS', doc)
        self.assertIn('const SOUND=null', doc)
        self.assertNotIn('id="btn-sound"', doc)
    def test_browser_sound_cues(self):
        self.story['sound']={'bed':{'start':1,'silence':[3,4],'fadeOut':20,'fadeDur':2},
            'cues':[{'t':1.5,'id':'paper'},{'t':2,'id':'bell'}]}
        p=prepare(self.story)
        grow=grow_schedule(self.story,p)
        doc=render_html(self.story,p,grow)
        self.assertIn('id="btn-sound"', doc)
        self.assertIn('"id":"paper"', doc)
        self.story['sound']={'cues':[{'t':1,'id':'nope'}]}
        with self.assertRaises(ValueError): render_html(self.story,p,grow)
    def test_topic_preset(self):
        s=plan('a little dream among the stars');p=prepare(s)
        self.assertEqual(s['chapters'][0]['objects'][2]['motif'],'star')
        self.assertTrue('rocket' in [x['motif'] for x in p['objects'].values()])
    def test_unknown_topic_fallback(self):
        self.assertTrue(prepare(plan('a poem about time')))
    def test_non_spring_draft_does_not_open_with_pencil(self):
        forest=plan('a letter in the forest')
        motifs=[obj['motif'] for obj in forest['chapters'][0]['objects']]
        hits=[item['hit'] for item in forest['chapters'][0]['route'] if isinstance(item, dict)]
        self.assertNotIn('pencil', motifs)
        self.assertNotIn('pencil', hits)
        self.assertIn('hill', motifs)
        self.assertIn('opening', hits)
        self.assertTrue(prepare(forest))
        generic=plan('a poem about time')
        self.assertNotIn('pencil', [obj['motif'] for obj in generic['chapters'][0]['objects']])
        spring=plan('a line into spring')
        self.assertIn('pencil', [obj['motif'] for obj in spring['chapters'][0]['objects']])
    def test_custom_motif(self):
        self.story['customMotifs']={'fox':{'svg':'<path d="M100 180 Q60 80 100 40 Q140 80 100 180 Z" fill="{{sage}}" stroke="{{ink}}" stroke-width="3"/>','anchorLocal':[100,180]}}
        target=self.story['chapters'][0]['objects'][2]
        target['motif']='fox'
        p=prepare(self.story)
        self.assertIn('M100 180',story_svg(self.story,p))
    def test_unsafe_custom_motif_rejected(self):
        self.story['customMotifs']={'unsafe':{'svg':'<image href="http://evil.invalid/p.png"/>'}}
        with self.assertRaises(ValueError):custom_markup('unsafe',self.story,5)
    def test_custom_motif_text_allowed(self):
        self.story['customMotifs']={'screen':{'svg':'<text x="20" y="40" stroke="none" fill="{{ink}}">Hello, <tspan>World!</tspan></text>'}}
        self.assertIn('World!',custom_markup('screen',self.story,1))
    def test_cue_offsets(self):
        self.story['customMotifs']={'late':{'svg':'<circle r="4"><set attributeName="r" to="9" begin="{{cue+0.6}}"/><set attributeName="r" to="2" begin="{{cue-9}}"/></circle>'}}
        markup=custom_markup('late',self.story,5)
        self.assertIn('begin="5.6s"',markup)
        self.assertIn('begin="0s"',markup)
    def test_long_story_layout_fields(self):
        self.story.update({'masthead':'1024 / PROGRAMMERS DAY','prologue':['first line','second line'],
            'signature':'THE NEXT LINE IS YOURS','epilogueLines':['ending one',{'text':'1024','size':80,'bold':True}],
            'backgroundShapes':[{'cx':100,'cy':5000,'rx':80,'ry':90,'fill':'rose','opacity':.3}],
            'backgroundFlourishes':[[60,5200]],'duration':64})
        self.story['canvas']['height']=6000
        p=prepare(self.story);markup=story_svg(self.story,p)
        for text in ('1024 / PROGRAMMERS DAY','second line','THE NEXT LINE IS YOURS','ending one','cy="5000"','M60 5200'):
            self.assertIn(text,markup)
        self.assertNotIn('THE LINE JOURNAL',markup)
        self.assertEqual(len(grow_schedule(self.story,p)),16)
        self.assertIn('00:00 / 01:04',render_html(self.story,p,grow_schedule(self.story,p)))
    def test_discontinuous_path_rejected(self):
        self.story['chapters'][1]['route'][0]=[1,1]
        with self.assertRaisesRegex(ValueError,'Path discontinuity'):prepare(self.story)
    def test_palette_catalog_contrast(self):
        ids=set()
        self.assertGreaterEqual(len(PALETTES), 10)
        for item in PALETTES:
            self.assertNotIn(item['id'], ids)
            ids.add(item['id'])
            self.assertGreaterEqual(contrast(item['ink'], item['paper']), 4.5)
    def test_suggest_matches_scene_and_offers_range(self):
        sea=suggest('a letter by the sea')
        self.assertEqual(sea['note'], 'matched')
        self.assertEqual(sea['choices'][0]['id'], 'sea')
        self.assertTrue(sea['choices'][0]['recommended'])
        night=suggest('the sea late at night')
        self.assertEqual(night['choices'][0]['id'], 'night')
        self.assertIn('sea', [item['id'] for item in night['choices'][:3]])
        cosmos=suggest('a little dream among the stars')
        self.assertEqual(cosmos['choices'][0]['id'], 'cosmos')
        open_theme=suggest('a poem about time')
        self.assertEqual(open_theme['note'], 'open')
        self.assertEqual(open_theme['choices'][0]['id'], 'spring')
        self.assertTrue(any(item['id'] in ('night', 'cosmos') for item in open_theme['choices']))
        self.assertGreaterEqual(len({item['id'] for item in open_theme['choices']}), 5)
    def test_plan_palette_recolors_story(self):
        story=plan('a letter by the sea', palette='Sea salt')
        self.assertEqual(story['paletteName'], 'sea')
        self.assertEqual(story['palette']['ink'], '#163E4C')
        self.assertEqual(story['canvas']['background'], '#F3F7F6')
        self.assertEqual(plan('a letter by the sea')['palette']['ink'], '#375763')
    def test_spring_motif_keeps_authored_fills(self):
        colors=dict(self.story['palette'])
        colors['paper']=self.story['canvas']['background']
        self.assertIn('#E9B776', motif_markup('pencil', colors, 0))
    def test_other_palette_recolors_motif_and_chrome(self):
        story=plan('a night voyage', palette='night')
        colors=dict(story['palette']); colors['paper']=story['canvas']['background']
        flower=motif_markup('flower', colors, 0)
        self.assertNotIn('#F0BFAE', flower)
        self.assertIn(story['palette']['orange'], flower)
        self.assertIn(story['palette']['ink'], flower)
        prepared=prepare(story)
        doc=render_html(story, prepared, grow_schedule(story, prepared))
        self.assertIn('--paper:#17202C', doc)
        spring=render_html(self.story, prepare(self.story), grow_schedule(self.story, prepare(self.story)))
        self.assertEqual(spring.count('--paper:'), 1)
    def test_arc_and_look_package(self):
        self.assertEqual(suggest_arc('how a city changes')['arc']['id'], 'timeline')
        self.assertEqual(suggest_arc('standing up after failure')['arc']['id'], 'man_in_hole')
        self.assertEqual(suggest_arc('a poem about time')['arc']['id'], 'three_act')
        moves=motions_for(resolve_arc('how_it_works'), 'calm')
        self.assertEqual(moves[-1], 'still')
        self.assertNotEqual(moves[0], moves[1])
        sea=resolve_palette('Sea salt')
        self.assertEqual(sea['motion'], 'calm')
        self.assertTrue(sea['finish'])
        story=plan('how a city changes', palette='ink', arc='Timeline')
        self.assertEqual(story['arc'], 'timeline')
        self.assertEqual(story['chapters'][0]['emphasis'], 'ink')
        self.assertEqual(story['chapters'][-1]['motion'], 'still')
        self.assertEqual(resolve_palette('lantern')['motion'], 'punchy')
    def test_adjacent_motion_warning(self):
        story=json.loads((ROOT/'examples/spring/story.json').read_text(encoding='utf8'))
        for chapter in story['chapters']:
            chapter.pop('gifDecorations',None)
            for obj in chapter['objects']:
                if obj['id']=='seedlet':
                    obj['motif']='flower'
        errors, warnings, report=validate(story, ROOT/'examples/spring')
        self.assertEqual(errors, [])
        self.assertTrue(any('pop' in item for item in warnings))
        self.assertTrue(report)

    def test_richness_warnings(self):
        story=copy.deepcopy(self.story)
        for chapter in story['chapters']:chapter.pop('gifDecorations',None)
        story['chapters'][2]['objects'][3]['id']='far-hills'
        errors, warnings, report=validate(story, ROOT/'examples/spring')
        self.assertEqual(errors, [])
        joined='\n'.join(warnings)
        self.assertIn('has only 4 objects', joined)
        self.assertIn('no small annotation', joined)
        self.assertIn('sparse', joined)
        self.assertIn('far-hills is named hill but drawn as tree', joined)
        self.assertNotIn('butterfly is named', joined)
    def test_thin_custom_hero_and_text_clearance(self):
        story=copy.deepcopy(self.story)
        for chapter in story['chapters']:chapter.pop('gifDecorations',None)
        story['customMotifs']={'thin':{'svg':'<path d="M60 180Q100 80 140 180Z" fill="{{sage}}"/>'}}
        story['chapters'][1]['objects'][1]['motif']='thin'
        head=story['chapters'][1]
        anchor=prepare(story)['objects']['blossom']['anchor']
        head['captionAt']=[anchor[0]-20,anchor[1]+10]
        _, warnings, _=validate(story, ROOT/'examples/spring')
        joined='\n'.join(warnings)
        self.assertIn('hero blossom has only 1 shape', joined)
        self.assertIn('chapter 2 caption is only', joined)

if __name__=='__main__':unittest.main(verbosity=2)
