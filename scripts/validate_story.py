#!/usr/bin/env python3
"""Static QA: SVG linework, optional transparent GIF accents, timing and page growth.
No dependencies outside the Python standard library.
"""
import argparse, json, re, sys
from pathlib import Path
from xml.etree import ElementTree as ET
from compile_story import prepare, tip_at, grow_schedule, story_svg, valid_story
from gif_decor import load_decorations
from motifs import MOTIF_MOTION
from arcs import resolve_arc


def chapter_hero(chapter):
    hits=[item['hit'] for item in chapter.get('route', []) if isinstance(item, dict) and item.get('hit')]
    objects={item['id']:item for item in chapter.get('objects', [])}
    found=[objects[name] for name in hits if name in objects]
    if not found:return None
    return max(found, key=lambda item: (item.get('scale', 1), item.get('y', 0)))

def visible_family(obj):
    motif=obj.get('motif')
    if motif in MOTIF_MOTION:return MOTIF_MOTION[motif]
    return obj.get('motion') or 'still'

def direction_warnings(story, prepared):
    """Soft checks for arc rhythm. They do not reject a story."""
    notes=[]
    arrivals={item['object']:item['lineArrival'] for item in prepared['connections']}
    families=[]
    for chapter in story['chapters']:
        hits=[item['hit'] for item in chapter.get('route', []) if isinstance(item, dict) and item.get('hit')]
        times=[arrivals[name] for name in hits if name in arrivals]
        if story.get('arc') and chapter.get('duration', 0)>8 and len(times)<2:
            notes.append(f'{chapter["id"]} runs longer than 8 seconds with only one hit. The line should meet another object in this chapter.')
        elif story.get('arc') and len(times)>=2 and times[1]-times[0]>7:
            notes.append(f'{chapter["id"]} leaves {times[1]-times[0]:.1f}s between its first two hits. Keep that gap at 3–5 seconds.')
        hero=chapter_hero(chapter)
        family=visible_family(hero) if hero else None
        families.append(family)
        intended=(hero or {}).get('motion') or chapter.get('motion')
        if hero and intended and hero.get('motif') in MOTIF_MOTION and intended!=MOTIF_MOTION[hero['motif']]:
            notes.append(f'{hero["id"]} asks for {intended}, but the built-in {hero["motif"]} is {MOTIF_MOTION[hero["motif"]]}. Draw this beat as customMotifs.')
        emphasis=chapter.get('emphasis')
        if emphasis and emphasis not in ('ink','sage','orange','rose'):
            notes.append(f'{chapter["id"]} emphasis must be ink, sage, orange, or rose')
    for index in range(1, len(families)):
        if families[index] and families[index]==families[index-1]:
            notes.append(f'Chapter {index} and chapter {index+1} both use {families[index]} for the hero. Change one motion.')
    for index in range(1, len(story['chapters'])):
        left, right=story['chapters'][index-1].get('emphasis'), story['chapters'][index].get('emphasis')
        if left and left==right:
            notes.append(f'Chapter {index} and chapter {index+1} both emphasize {left}. Change one hero color.')
    return notes

SHAPE_RE=re.compile(r'<(?:path|circle|ellipse|rect|polygon|polyline|line)\b')
FILL_RE=re.compile(r'\bfill="([^"]+)"')
PLURALS={'flowers':'flower','hills':'hill','stars':'star','birds':'bird','clouds':'cloud','trees':'tree',
         'waves':'wave','leaves':'leaf','sunset':'sun','sunrise':'sun','hearts':'heart','books':'book',
         'houses':'house','shells':'shell','lanterns':'lantern','balloons':'balloon','butterflies':'butterfly'}
DENSITY_WINDOW=1000
DENSITY_STEP=250
DENSITY_MIN=5
TEXT_CLEARANCE=40
MIN_CHAPTER_OBJECTS=7
HERO_MIN_SHAPES=8
HERO_MIN_FILLS=3

def custom_svg(story, motif):
    spec=story.get('customMotifs',{}).get(motif)
    if spec is None:return None
    return spec if isinstance(spec,str) else spec.get('svg','')

def text_width(line, size):
    return sum(size if ord(ch)>0x2E80 else size*.58 for ch in str(line))

def text_boxes(story):
    """Approximate boxes of the compiler's typography, as (label, x0, y0, x1, y1)."""
    H=story['canvas']['height'];boxes=[]
    prologue=story.get('prologue','x');prologue=prologue if isinstance(prologue,list) else [prologue]
    boxes.append(('opening title',70,95,700,419+len(prologue)*42))
    for idx,ch in enumerate(story['chapters']):
        name=f'chapter {idx+1}'
        x,y=ch['labelAt']
        label=f'{ch.get("number",idx+1):0>2}  /  {ch.get("english","CHAPTER")}'
        boxes.append((f'{name} label',x,y-16,x+max(155,text_width(label,18)*1.15),y+24))
        heads=ch.get('headline',[ch.get('title','')])
        wide=max(text_width(ln,53) for ln in heads)
        boxes.append((f'{name} title',x,y+55,x+wide,y+100+(len(heads)-1)*65+12))
        caps=ch.get('caption',[])
        if caps:
            cx,cy=ch.get('captionAt',[x,y+440])
            wide=max(text_width(ln,27) for ln in caps)
            boxes.append((f'{name} caption',cx,cy-25,cx+wide,cy+(len(caps)-1)*44+8))
    top=float(story.get('epilogueTop',H-134))
    boxes.append(('ending',205,top-35,545,H-50))
    return boxes

def box_distance(point, box):
    _,x0,y0,x1,y1=box
    dx=max(x0-point[0],0,point[0]-x1);dy=max(y0-point[1],0,point[1]-y1)
    return (dx*dx+dy*dy)**.5

def name_mismatch(obj):
    motif=obj.get('motif')
    if motif not in MOTIF_MOTION:return None
    for token in re.split(r'[-_]',obj.get('id','').lower()):
        token=PLURALS.get(token,token)
        if token in MOTIF_MOTION and token!=motif:return token
    return None

def richness_warnings(story, prepared):
    """Soft checks for sparse scenes, thin heroes and text crowding. They do not reject a story."""
    notes=[];H=float(story['canvas']['height'])
    for idx,ch in enumerate(story['chapters']):
        name=f'chapter {idx+1} ({ch["id"]})'
        objects=ch.get('objects',[])
        if len(objects)<MIN_CHAPTER_OBJECTS:
            notes.append(f'{name} has only {len(objects)} objects. The minimum is 1 hero + 3 supporting objects + 2 ornament groups + 1 small annotation = {MIN_CHAPTER_OBJECTS}. Add them from the material list.')
        if not any('<text' in (custom_svg(story,o.get('motif')) or '') for o in objects):
            notes.append(f'{name} has no small annotation (a customMotif that contains <text>). Add a year, a place, a number, or a quoted line.')
        hero=chapter_hero(ch)
        svg=custom_svg(story,hero.get('motif')) if hero else None
        if svg is not None:
            shapes=len(SHAPE_RE.findall(svg))
            fills={v.lower() for v in FILL_RE.findall(svg) if v.lower() not in ('none','transparent')}
            if shapes<HERO_MIN_SHAPES or len(fills)<HERO_MIN_FILLS:
                notes.append(f'{name} hero {hero["id"]} has only {shapes} shapes and {len(fills)} fills. The minimum is {HERO_MIN_SHAPES} shapes and {HERO_MIN_FILLS} fills. Add a detail line and a ground shadow.')
        for obj in objects:
            other=name_mismatch(obj)
            if other:notes.append(f'{obj["id"]} is named {other} but drawn as {obj["motif"]}. Rename it, or draw the real {other} with customMotifs.')
    spans=[(o['y'],o['y']+200*float(o.get('scale',1))) for o in prepared['objects'].values()]
    sparse=[];y=500.0
    while y+DENSITY_WINDOW<=H-300:
        count=sum(1 for top,bottom in spans if top<y+DENSITY_WINDOW and bottom>y)
        if count<DENSITY_MIN:
            if sparse and y<=sparse[-1][1]:sparse[-1]=[sparse[-1][0],y+DENSITY_WINDOW,min(sparse[-1][2],count)]
            else:sparse.append([y,y+DENSITY_WINDOW,count])
        y+=DENSITY_STEP
    for top,bottom,count in sparse:
        notes.append(f'y={top:.0f}–{bottom:.0f} is sparse: only {count} objects in {DENSITY_WINDOW} design units, below the minimum of {DENSITY_MIN}. Add a supporting object, an ornament, or a small annotation from the material list.')
    boxes=text_boxes(story)
    for box in boxes:
        nearest=min(box_distance(p,box) for seg in prepared['segments'] for curve in seg['curves'] for p in curve['samples'])
        if nearest<TEXT_CLEARANCE:
            notes.append(f'{box[0]} is only {nearest:.0f} design units from the main line. Keep text at least 70 away. Move the type or change a waypoint.')
    return notes

def validate(story, asset_root=None):
    failures=[];warnings=[]
    errors,warns=valid_story(story);failures+=errors;warnings+=warns
    if failures:return failures,warnings,{}
    try:
        prepared=prepare(story)
        schedule=grow_schedule(story,prepared)
        gif_count=sum(len(ch.get('gifDecorations', [])) for ch in story['chapters'])
        if gif_count and asset_root is None:
            failures.append('GIF decorations require asset_root (source story.json directory) for validation')
            return failures,warnings,{}
        decorations=load_decorations(story,prepared,Path(asset_root or '.'))
        svg=story_svg(story,prepared,decorations=decorations)
        root=ET.fromstring(svg)
        tags={node.tag.rsplit('}',1)[-1] for node in root.iter()}
        for banned in ('script','foreignObject','use','video'):
            if banned in tags:failures.append(f'Forbidden SVG tag <{banned}>')
        for banned in ('data:image/png','data:image/jpeg','<script','<style'):
            if banned in svg:failures.append(f'Embedded unsupported content: {banned}')
        images=[el for el in root.iter() if el.tag.rsplit('}',1)[-1]=='image']
        if len(images)!=len(decorations):failures.append('Unexpected number of SVG <image> elements')
        for img in images:
            if not img.get('href','').startswith('data:image/gif;base64,'):
                failures.append('Every <image> must use an approved local transparent GIF')
        conns=prepared['connections']
        if not conns:failures.append('No connected object pins. A coherent line-story needs at least one hit.')
        if any(x['pathPointError']>1 for x in conns):failures.append('A path missed an interaction anchor')
        for i,x in enumerate(schedule):
            if x['to']+0.001<x['from']:failures.append(f'Grow step {i} shrinks the page')
            if x['to']+0.001<x.get('from',0):failures.append('Nonmonotonic grow')
        if abs(schedule[-1]['visibleDesignHeight']-story['canvas']['height'])>1.5:
            failures.append('Grow animation does not reach full story height')
        # A visual QA proxy; clipping is tested more precisely in Playwright.
        if len(story['chapters'])>7:warnings.append('Longer stories need careful scroll/viewport performance testing')
        if story.get('arc'):
            try:resolve_arc(story['arc'])
            except ValueError as exc:failures.append(str(exc))
        warnings.extend(direction_warnings(story, prepared))
        warnings.extend(richness_warnings(story, prepared))
        for c in story['chapters']:
            if any(len(ln)>15 for ln in c.get('headline',[])):
                warnings.append(f'Heading in {c["id"]} may be wider than its text column')
        report={'chapters':len(story['chapters']),'paths':len(prepared['segments']),
                'motifs':len(prepared['objects']),'gifDecorations':len(decorations),'connections':len(conns),
                'pathLengths':{p['id']:round(p['length'],2) for p in prepared['segments']},
                'finalCanvasHeight':schedule[-1]['visibleDesignHeight'],
                'triggerTimes':{name:round(t,2) for name,t in prepared['cues'].items()}}
        return failures,warnings,report
    except Exception as e:failures.append(str(e));return failures,warnings,{}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',default=str(Path(__file__).resolve().parents[1]/'examples/spring/story.json'))
    p.add_argument('--json-report',default='')
    a=p.parse_args();story=json.loads(Path(a.input).read_text(encoding='utf8'))
    errors,warnings,report=validate(story,Path(a.input).resolve().parent)
    for item in errors:print('ERROR',item)
    for item in warnings:print('WARN',item)
    if a.json_report:
        Path(a.json_report).write_text(json.dumps({'errors':errors,'warnings':warnings,'report':report},ensure_ascii=False,indent=2),encoding='utf8')
    if errors:sys.exit(1)
    print('PASS: story, core SVG motifs, optional local transparent GIFs, path pins, SMIL page growth')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
