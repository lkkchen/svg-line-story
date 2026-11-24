#!/usr/bin/env python3
"""Offline fallback story planner. The Agent should elaborate beyond these presets.
This command takes exactly one theme and writes a structurally valid V1-style outline.
"""
import argparse, copy, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from palettes import palette_roles, resolve_palette
from arcs import motions_for, resolve_arc, suggest_arc

ROOT=Path(__file__).resolve().parents[1]
DEFAULT=ROOT/'examples/spring/story.json'

def term_in(text, term):
    if re.search(r'[A-Za-z]', term):
        return re.search(r'(?<![A-Za-z])' + re.escape(term) + r'(?![A-Za-z])', text, re.I) is not None
    return term in text

PRESETS={
  'spring': {'terms':['spring','seed','bloom','garden','sprout'],
    'title':'A line into spring','subtitle':'A LINE INTO SPRING','m':['sprout','flower','boat'],'opener':'pencil',
    'heads':[['Some stories','begin with a seed.'],['Wait for one flower','to open slowly.'],['Carry spring','somewhere far.']],
    'beat':['A small seed wakes.','The flower that was waiting finally opens.','It sets out, carrying a little hope.'],'ending':'May every stretch of the road find something in bloom.'},
  'forest':{'terms':['forest','woods','trees','leaf','leaves'],
    'title':'Into a forest','subtitle':'A LINE INTO THE WOODS','m':['leaf','tree','moon'],'opener':'hill',
    'heads':[['Follow one leaf','into the forest.'],['Meet one tree','and hear the breeze.'],['When the moon rises,','the story goes on.']],
    'beat':['The line picks up a leaf.','The curve goes around a large tree.','Night brings a crescent moon.'],'ending':'Every leaf has its own direction.'},
  'ocean':{'terms':['ocean','sea','beach','island','wave','lighthouse'],
    'title':'Follow the line to the sea','subtitle':'A THREAD TO THE SEA','m':['shell','boat','lighthouse'],'opener':'wave',
    'heads':[['Pick up one','shell from the shore.'],['Let a paper boat','follow the spray.'],['A distant light','is waiting for us.']],
    'beat':['A thin line rounds a shell.','The water lifts a paper boat.','The curve passes a far lighthouse.'],'ending':'May every departure meet a light.'},
  'stars':{'terms':['stars','star','cosmos','galaxy','space','dream'],
    'title':'String the stars together','subtitle':'A LINE OF LITTLE STARS','m':['star','kite','rocket'],'opener':'moon',
    'heads':[['A small star','is kept inside.'],['Look up,','and the kite flies higher.'],['Every distance','has a reason to start.']],
    'beat':['One star flickers.','A kite string reaches the night.','Imagination becomes a small rocket.'],'ending':'Grow up slowly, and still look up.'},
  'books':{'terms':['book','books','reading','library','bookstore'],
    'title':'The journey of a book','subtitle':'FROM WORDS TO WORLDS','m':['book','butterfly','lantern'],'opener':'leaf',
    'heads':[['Open one page.','The story begins.'],['A small dream on paper','lifts off.'],['Under one lamp,','a larger world.']],
    'beat':['An open book meets the first line.','Imagination flies into a butterfly.','It becomes a warm light.'],'ending':'May every book light a distance.'},
  'birthday':{'terms':['birthday','celebration','gift','wish','festival'],
    'title':'Draw a wish as a line','subtitle':'A HAPPY LITTLE WISH','m':['gift','balloon','star'],'opener':'heart',
    'heads':[['One gift,','full of care.'],['A wish on the wind','rises into the sky.'],['The last star','lights up.']],
    'beat':['A gift gives the surprise.','A balloon rises slowly.','Hope becomes starlight at the edge of the sky.'],'ending':'Keep the joy and the wish.'},
  'city':{'terms':['city','street','town','hometown','neighborhood'],
    'title':'A line through a small city','subtitle':'A LITTLE CITY WALK','m':['house','tree','lantern'],'opener':'sun',
    'heads':[['Open the door','and see the morning.'],['Tree shade','slows the time.'],['The lights come on.','The city has warmth.']],
    'beat':['The curve starts at a small house.','It goes around a street tree.','It stops in the light of coming home.'],'ending':'Every small ordinary thing is worth keeping.'},
  'travel':{'terms':['travel','journey','departure','explore','adventure'],
    'title':'Follow the line into the distance','subtitle':'A SMALL ADVENTURE','m':['kite','boat','lighthouse'],'opener':'cloud',
    'heads':[['Pack a small dream','and set out.'],['Wind, waves,','and good weather.'],['A light far away','waits for us to arrive.']],
    'beat':['A kite string marks the first stretch.','A paper boat sets a small sail.','A lighthouse appears at the end of the trip.'],'ending':'The end of the road is a new start.'},
}

def apply_palette(story, token):
    spec=resolve_palette(token)
    story['palette']=palette_roles(spec)
    story['canvas']['background']=spec['paper']
    story['paletteName']=spec['id']
    return story

def replace_sample_pencil(story, opener):
    """Spring's pencil is sample framing, not a required opening for every draft."""
    if opener == 'pencil':
        return story
    chapter = story['chapters'][0]
    for obj in chapter.get('objects', []):
        if obj.get('id') == 'pencil':
            obj['id'] = 'opening'
            obj['motif'] = opener
    for index, waypoint in enumerate(chapter.get('route', [])):
        if isinstance(waypoint, dict) and waypoint.get('hit') == 'pencil':
            chapter['route'][index] = {'hit': 'opening'}
    return story

def apply_arc(story, token, motion='calm'):
    spec=resolve_arc(token)
    moves=motions_for(spec, motion)
    story['arc']=spec['id']
    for chapter, role, emphasis, move in zip(story['chapters'], spec['roles'], spec['emphasis'], moves):
        chapter['role']=role
        chapter['emphasis']=emphasis
        chapter['motion']=move
    return story

def plan(topic, palette=None, arc=None):
    text=topic.strip();base=json.loads(DEFAULT.read_text(encoding='utf8'))
    if not text:raise ValueError('Theme cannot be empty')
    found=next((p for p in PRESETS.values() if any(term_in(text, key) for key in p['terms'])),None)
    if found is None:
        # A coherent generic draft; the Agent must use its own reasoning to design bespoke motifs and scenes.
        found={'title':text if len(text)<=42 else text[:42].rstrip()+'…','subtitle':'ONE LINE, ONE STORY',
          'm':['leaf','heart','star'],'opener':'sun',
          'heads':[['A small line','sets out quietly.'],['Halfway along,','it meets something gentle.'],['Keep going,','and there is light.']],
          'beat':['The line becomes the start of the story.','Something changes along the way.','The theme turns into a warm ending.'],
          'ending':'May every story leave an echo.'}
    base['theme']=text;base['title']=found['title'];base['subtitle']=found['subtitle'];base['epilogue']=found['ending']
    # Template GIF accents belong only to the original spring example. An Agent
    # should author new transparent details for each new theme, not paste petals
    # into a train, book or city story.
    for chapter in base['chapters']:
        chapter.pop('gifDecorations', None)
    chs=base['chapters']; ids=['seedlet','blossom','paperboat']
    for idx,(ch,key) in enumerate(zip(chs,ids)):
        ch['headline']=copy.deepcopy(found['heads'][idx]);ch['storyBeat']=found['beat'][idx]
        ch['objects']=[{**o,'motif':found['m'][idx]} if o['id']==key else o for o in ch['objects']]
        ch['title']=['Departure','Meeting','Distance'][idx] if found is not PRESETS['spring'] else ['Waking','In bloom','Setting out'][idx]
    # Simplify decor of specific presets so a sunflower doesn't appear in a city story.
    if found is not PRESETS['spring']:
        for ch in chs:
            for ob in ch['objects']:
                if ob['id']=='wild-flowers':ob['id']='small-star';ob['motif']='star'
    replace_sample_pencil(base, found.get('opener', 'sun'))
    motion='calm'
    if palette:
        apply_palette(base, palette)
        motion=resolve_palette(palette).get('motion', 'calm')
    chosen=arc or suggest_arc(text, motion)['arc']['id']
    apply_arc(base, chosen, motion)
    return base


def main():
    pa=argparse.ArgumentParser(description='One topic -> a fully formed offline SVG-story outline for the agent to refine')
    pa.add_argument('theme',help='Any theme, for example: starlight in a forest, a letter by the sea')
    pa.add_argument('--palette',help='Palette id or English name, for example sea / Sea salt. Omit to keep Spring.')
    pa.add_argument('--arc',help='Arc id or English name, for example timeline / Timeline. Omit to suggest one from the theme.')
    pa.add_argument('--output','-o',default='story.json')
    args=pa.parse_args()
    result=plan(args.theme, palette=args.palette, arc=args.arc)
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(f'Created {path} for theme: {args.theme}\nNext: compile with compile_story.py --input {path}')
    print('Note: The offline planner is a motif-limited first draft. A creative Agent should rewrite beats/geometry for unique themes.')
    print('Note: The spring pencil opening is sample framing only. Non-spring drafts start on a theme object; replace that opener with this story\'s own origin.')

if __name__=='__main__':main()
