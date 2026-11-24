#!/usr/bin/env python3
"""Story JSON -> pure inline SVG + SMIL browser long-scroll + JS-free WeChat study output.
Standard library only. Uses waypoints with named motif pins for exact connections.
"""
from __future__ import annotations
import argparse, bisect, html, json, math, re, sys, shutil
from pathlib import Path
from xml.etree import ElementTree as ET
from typing import Any
from motifs import motif_markup, MOTIFS, MOTIF_ANCHORS
from gif_decor import load_decorations, validate_gif_decorations
from palettes import chrome_css

ROOT=Path(__file__).resolve().parents[1]
PAPER='#FCFAF4'


def esc(value): return html.escape(str(value), quote=True)
def fnum(n): return f'{float(n):.2f}'.rstrip('0').rstrip('.') if '.' in f'{float(n):.2f}' else f'{float(n):.2f}'
def vec(v): return (float(v[0]),float(v[1]))
def dist(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])
def lin(a,b,t):return a+(b-a)*t

def bez(p0,p1,p2,p3,t):
    u=1-t
    return (u*u*u*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t*t*t*p3[0],
            u*u*u*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t*t*t*p3[1])

def controls(points, i, tension):
    p0=points[i-1] if i else points[i]
    p1=points[i]; p2=points[i+1]
    p3=points[i+2] if i+2<len(points) else points[i+1]
    t=tension/6
    # Hermite -> Bezier; naturally joins at a shared chapter boundary.
    return (p1,(p1[0]+(p2[0]-p0[0])*t,p1[1]+(p2[1]-p0[1])*t),
            (p2[0]-(p3[0]-p1[0])*t,p2[1]-(p3[1]-p1[1])*t),p2)

def cubic_samples(cp, count=48):
    pts=[bez(*cp,0)]; cumulative=[0.0]
    for k in range(1,count+1):
        p=bez(*cp,k/count)
        cumulative.append(cumulative[-1]+dist(p,pts[-1]));pts.append(p)
    return pts,cumulative

def point_at_length(curve, length):
    total=curve['length'];length=max(0,min(float(length),total)); ps=curve['samples']; cum=curve['cumulative']
    i=max(0,min(bisect.bisect_left(cum,length),len(cum)-1))
    if i==0:return ps[0]
    s=(length-cum[i-1])/max(cum[i]-cum[i-1],1e-9)
    return (lin(ps[i-1][0],ps[i][0],s),lin(ps[i-1][1],ps[i][1],s))

def path_text(curves):
    if not curves:return ''
    st=curves[0]['cp'][0]
    out=[f'M {fnum(st[0])} {fnum(st[1])}']
    for curve in curves:
        _,a,b,c=curve['cp']
        out.append(f'C {fnum(a[0])} {fnum(a[1])} {fnum(b[0])} {fnum(b[1])} {fnum(c[0])} {fnum(c[1])}')
    return ' '.join(out)


SAFE_CUSTOM_TAGS={'g','path','circle','ellipse','rect','line','polyline','polygon','text','tspan','animate','animateTransform','animateMotion','set'}

def custom_markup(name, story, at):
    # Works for free-form themes: Agents may author original motif geometry as JSON markup.
    spec=story.get('customMotifs',{}).get(name)
    if spec is None:raise ValueError(f'Unknown custom motif: {name}')
    if isinstance(spec,str):spec={'svg':spec}
    markup=spec.get('svg','')
    if len(markup)>16000:raise ValueError(f'Custom motif too large: {name}')
    vals=dict(story['palette']);vals['paper']=story['canvas'].get('background',PAPER);vals['cue']=fnum(at)+'s'
    markup=re.sub(r'{{cue([+-]\d+(?:\.\d+)?)}}',lambda m:fnum(max(0,float(at)+float(m.group(1))))+'s',markup)
    for token,replacement in vals.items():
        markup=markup.replace('{{'+token+'}}',str(replacement))
    if re.search(r'{{.*?}}|<!|&(?:#|[A-Za-z])|\b(?:javascript|data):',markup,re.IGNORECASE):
        raise ValueError(f'Unsafe/unexpanded token in motif {name}')
    try:root=ET.fromstring('<g>'+markup+'</g>')
    except ET.ParseError as e:raise ValueError(f'Malformed SVG in custom motif {name}: {e}') from e
    for el in root.iter():
        if el.tag not in SAFE_CUSTOM_TAGS:raise ValueError(f'Unsupported custom SVG tag {el.tag} in {name}')
        for key,value in el.attrib.items():
            if (key.startswith('on') or key.startswith('{') or key in ('href','xlink:href','style','filter','mask','clip-path')
                or re.search(r'(?:https?:|\burl\(|javascript:|data:)',value,re.I)):
                raise ValueError(f'Forbidden custom SVG attribute {key} in {name}')
    ink=esc(story['palette']['ink'])
    return f'<g stroke="{ink}" stroke-linecap="round" stroke-linejoin="round">{markup}</g>'

def valid_story(story):
    errors=[]; warnings=[]
    required=['title','duration','canvas','palette','chapters','grow']
    for name in required:
        if name not in story: errors.append(f'Missing required field: {name}')
    if errors:return errors,warnings
    w=story['canvas'].get('width');h=story['canvas'].get('height')
    if w != 750: warnings.append('V1 recommends a width of 750. Other widths work, but the storyboard has to be redesigned.')
    if not isinstance(h,(int,float)) or h<1800:errors.append('canvas.height should be >= 1800')
    if not 12<=story['duration']<=300:errors.append('duration should be between 12 and 300 seconds')
    if len(story['chapters'])<2:errors.append('At least two chapters are needed')
    for key in ('ink','sage','orange','rose','sky','light'):
        if not re.fullmatch(r'#[0-9a-fA-F]{6}', story['palette'].get(key,'')):
            errors.append(f'palette.{key} must be #RRGGBB')
    all_ids=set(); hits=set();old_end=-1
    for idx,ch in enumerate(story['chapters']):
        key=ch.get('id','')
        if not re.fullmatch(r'[A-Za-z][\w-]*',key,flags=re.ASCII):errors.append(f'Chapter {idx+1} needs ASCII id')
        if not 0<=ch['start']<story['duration']:errors.append(f'Invalid chapter start: {key}')
        if ch['start']<old_end-.05:errors.append(f'Overlapping animation schedules at chapter {key}')
        old_end=ch['start']+ch['duration']
        if old_end>story['duration']+.01:errors.append(f'Chapter {key} exceeds total duration')
        if len(ch.get('route',[]))<2:errors.append(f'Chapter {key} requires >= 2 route points')
        for item in ch.get('route',[]):
            if isinstance(item,dict):
                if list(item)!=['hit']: errors.append(f'Route lookup must be {{"hit":"object-id"}} in {key}')
                else:hits.add(item['hit'])
            elif not (isinstance(item,list) and len(item)==2 and all(isinstance(n,(int,float)) for n in item)):
                errors.append(f'Invalid route waypoint in {key}: {item}')
        for obj in ch.get('objects',[]):
            ident=obj.get('id','')
            if ident in all_ids:errors.append(f'Duplicate object id: {ident}')
            if not re.fullmatch(r'[A-Za-z][\w-]*',ident,flags=re.ASCII):errors.append(f'Invalid object id: {ident}')
            all_ids.add(ident)
            if obj.get('motif') not in MOTIFS and obj.get('motif') not in story.get('customMotifs',{}):errors.append(f'Unknown motif: {obj.get("motif")}. Use customMotifs to draw a new one.')
            if not isinstance(obj.get('scale',1),(int,float)) or not .15<=obj.get('scale',1)<=4:
                errors.append(f'Invalid scale on {ident}')
            if any(key not in obj for key in ('x','y')):errors.append(f'Missing x/y on {ident}')
            elif obj['x']<-300 or obj['x']>w+200 or obj['y']<-100 or obj['y']>h+200:
                errors.append(f'Object {ident} far outside canvas')
            if obj.get('reveal')=='touch' and ident not in hits: # hits from later chapter might exist; rechecked below
                pass
    errors += validate_gif_decorations(story, all_ids)
    for hit in hits:
        if hit not in all_ids:errors.append(f'Route pin references unknown object: {hit}')
    for ch in story['chapters']:
        for obj in ch.get('objects',[]):
            if obj.get('reveal')=='touch' and obj['id'] not in hits:
                errors.append(f'Object {obj["id"]} has reveal="touch" but no route pin')
    if old_end < story['duration']-5:warnings.append('Final path ends >5s before the closing card')
    if not (0<story['grow'].get('baseUnits',0)<h):errors.append('grow.baseUnits must be between 0 and canvas.height')
    if story['grow'].get('spacerUnits',0)<=0:errors.append('grow.spacerUnits must be positive')
    return errors,warnings


def prepare(story):
    errors,warnings=valid_story(story)
    if errors:raise ValueError('\n'.join(errors))
    objects={}
    for ch in story['chapters']:
        for o in ch.get('objects',[]):
            q={**o,'chapter':ch['id']}
            scale=o.get('scale',1)
            custom=story.get('customMotifs',{}).get(o['motif'],{})
            if isinstance(custom,str):custom={}
            anchor=o.get('anchorLocal',custom.get('anchorLocal',MOTIF_ANCHORS.get(o['motif'],[100,180])))
            q['anchor']=(o['x']+float(anchor[0])*scale,o['y']+float(anchor[1])*scale)
            objects[o['id']]=q

    def resolve(waypoint):
        if isinstance(waypoint,dict):return objects[waypoint['hit']]['anchor']
        return vec(waypoint)

    chapters=story['chapters'];all_points=[];region_ix=[]
    for j,ch in enumerate(chapters):
        pts=[resolve(p) for p in ch['route']]
        if j and dist(pts[0],all_points[-1])>1e-5:
            raise ValueError(f'Path discontinuity at chapter {ch["id"]}: previous end {all_points[-1]}, next start {pts[0]}')
        begin=len(all_points)-1 if j else 0
        all_points.extend(pts[1:] if j else pts)
        end=len(all_points)-1
        region_ix.append((begin,end))
    tension=float(story.get('pathTension',1.0))
    if not .2<=tension<=1.6:raise ValueError('pathTension should be between 0.2 and 1.6')
    segments=[]; cue={}; connections=[]
    for cidx,ch in enumerate(chapters):
        begin,end=region_ix[cidx];curves=[];way_lengths=[0.0]
        for j in range(begin,end):
            cp=controls(all_points,j,tension)
            samp,distances=cubic_samples(cp)
            curve={'cp':cp,'samples':samp,'cumulative':distances,'length':distances[-1]}
            curves.append(curve);way_lengths.append(way_lengths[-1]+curve['length'])
        total=way_lengths[-1]
        if total<1:raise ValueError(f'Empty route in {ch["id"]}')
        pth=path_text(curves)
        seg={'id':ch['id'],'start':ch['start'],'duration':ch['duration'],'curves':curves,
            'path':pth,'length':total,'way_lengths':way_lengths,'points':all_points[begin:end+1]}
        segments.append(seg)
        for j,wp in enumerate(ch['route']):
            if isinstance(wp,dict):
                obj=objects[wp['hit']]; ident=obj['id']
                raw_cue=ch['start']+ch['duration']*way_lengths[j]/total
                if ident not in cue:cue[ident]=max(0,raw_cue-float(obj.get('leadSeconds',.18)))
                connections.append({'object':ident,'chapter':ch['id'],'x':round(resolve(wp)[0],3),'y':round(resolve(wp)[1],3),
                                    'pathPointError':0.0,'lineArrival':round(raw_cue,2),'revealAt':round(cue[ident],2)})
    for obj in objects.values():
        if obj.get('reveal')=='touch': obj['reveal_time']=cue[obj['id']]
        else:obj['reveal_time']=float(obj.get('reveal',0))
        obj['motion_time']=cue.get(obj['id'],obj['reveal_time'])
        if not 0<=obj['reveal_time']<=story['duration']:
            raise ValueError(f'Invalid reveal time for {obj["id"]}')
    return {'objects':objects,'segments':segments,'cues':cue,'connections':connections,'warnings':warnings}


def point_on_segment(seg,ratio):
    target=seg['length']*max(0,min(1,ratio))
    cum=seg['way_lengths'];index=min(len(seg['curves'])-1,max(0,bisect.bisect_right(cum,target)-1))
    return point_at_length(seg['curves'][index],target-cum[index])

def tip_at(data,t):
    segs=data['segments']
    if t<segs[0]['start']:return segs[0]['points'][0]
    for seg in segs:
        if seg['start']<=t<=seg['start']+seg['duration']:
            return point_on_segment(seg,(t-seg['start'])/seg['duration'])
        if t<seg['start']:return segs[max(0,segs.index(seg)-1)]['points'][-1]
    return segs[-1]['points'][-1]


def grow_schedule(story, prepared, steps=None):
    g=story['grow']; base=float(g['baseUnits']);spacer=float(g['spacerUnits']);H=float(story['canvas']['height'])
    steps=steps or int(g.get('steps',max(8,round(float(story['duration'])/4))))
    initial=float(g.get('initialPercent',120));advance=float(g.get('aheadUnits',390))
    # Optional hold: wait for intro typography before the page starts growing.
    begin_at=float(g.get('beginAt',0.08))
    schedule=[];duration=float(story['duration']);lastp=initial
    span=max(0.01,duration-begin_at)
    for idx in range(steps):
        st=begin_at+idx*span/steps
        ed=begin_at+(idx+1)*span/steps
        y=max(tip_at(prepared,st+j*(ed-st)/8)[1] for j in range(9))
        target=(H if idx==steps-1 else min(H,y+advance))
        percent=max(lastp,100*(target-base)/spacer)
        schedule.append({'begin':round(st,2),'duration':round(ed-st,2),'from':round(lastp,4),'to':round(percent,4),
                         'visibleDesignHeight':round(base+percent*spacer/100,2)})
        lastp=percent
    return schedule


def reveal_anim(t,dur=.9):
    if t<=.001:return ''
    return f'<animate attributeName="opacity" from="0" to="1" begin="{fnum(t)}s" dur="{fnum(dur)}s" fill="freeze" restart="never"/>'

def fade_group(t,inner,dur=.75):
    """Wrap markup so it fades in at absolute time t (staggered chapter/title lines)."""
    if t<=.001:return inner
    return f'<g opacity="0">{reveal_anim(t,dur)}{inner}</g>'

def typetext(x,y,words,size=32,color='#375763',extra=''):
    return f'<text x="{fnum(x)}" y="{fnum(y)}" font-size="{size}" fill="{esc(color)}" {extra}>{esc(words)}</text>'

def palette_color(story,value):
    return story['palette'].get(value,value)

def decor_bg(story):
    W=story['canvas']['width'];H=story['canvas']['height'];p=story['palette']
    paper=f'''<rect width="{W}" height="{H}" fill="{esc(story['canvas'].get('background',PAPER))}"/>'''
    if 'backgroundShapes' in story or 'backgroundFlourishes' in story:
        shapes=''.join(f'''<ellipse cx="{fnum(s['cx'])}" cy="{fnum(s['cy'])}" rx="{fnum(s['rx'])}" ry="{fnum(s['ry'])}" fill="{esc(palette_color(story,s.get('fill','sky')))}" opacity="{fnum(s.get('opacity',.35))}"/>'''
                       for s in story.get('backgroundShapes',[]))
        marks=''.join(f'<path d="M{fnum(x)} {fnum(y)}q24 -22 46 0m-33 21q22 -18 41 1"/>' for x,y in story.get('backgroundFlourishes',[]))
        return f'''{paper}{shapes}<g stroke="{esc(p['sage'])}" stroke-width="2" fill="none" stroke-linecap="round" opacity=".57">{marks}</g>'''
    # Treat background with restraint: V1 clean flat fills and line-based flourishes, no stock textures.
    return f'''{paper}
       <ellipse cx="626" cy="308" rx="255" ry="275" fill="{esc(p['sky'])}" opacity=".41"/>
       <ellipse cx="65" cy="1790" rx="185" ry="240" fill="{esc(p['light'])}" opacity=".44"/>
       <ellipse cx="618" cy="2820" rx="225" ry="290" fill="{esc(p['sky'])}" opacity=".30"/>
       <g stroke="{esc(p['sage'])}" stroke-width="2" fill="none" stroke-linecap="round" opacity=".57">
          <path d="M70 653q25 -26 47 0m-32 22q24 -21 41 1"/>
          <path d="M607 1710q23 -22 45 0m-34 20q21 -16 40 1"/>
          <path d="M70 3160q29 -19 52 0"/>
       </g>'''

def motif_palette(story):
    pal=dict(story['palette'])
    pal['paper']=story['canvas'].get('background',PAPER)
    return pal

def svg_objects(story,prepared,z):
    pieces=[];colors=motif_palette(story)
    for obj in prepared['objects'].values():
        if obj.get('z','front')!=z:continue
        ident=obj['id'];a=obj['reveal_time'];style=('opacity="0"' if a>.001 else 'opacity="1"')
        art=(motif_markup(obj['motif'],colors,obj['motion_time'])
             if obj['motif'] in MOTIFS else custom_markup(obj['motif'],story,obj['motion_time']))
        scale=obj.get('scale',1)
        pieces.append(f'''<g id="obj-{esc(ident)}" {style}>
           {reveal_anim(a, obj.get('fadeDuration',.7))}
           <g transform="translate({fnum(obj['x'])} {fnum(obj['y'])}) scale({fnum(scale)})">{art}</g>
         </g>''')
    return '\n'.join(pieces)

def svg_routes(story, prepared):
    palette=story['palette'];ink=esc(palette['ink']);paper=esc(story['canvas'].get('background',PAPER));orange=esc(palette['orange'])
    o=[]
    for s in prepared['segments']:
        length=math.ceil(s['length']+3)
        d=esc(s['path']);start=fnum(s['start']);dur=fnum(s['duration'])
        o.append(f'''<g id="line-{esc(s['id'])}" stroke-dasharray="{length}" stroke-dashoffset="{length}" fill="none" stroke-linecap="round" stroke-linejoin="round">
             <animate attributeName="stroke-dashoffset" from="{length}" to="0" begin="{start}s" dur="{dur}s" fill="freeze" restart="never"/>
             <path d="{d}" stroke="{paper}" stroke-width="11"/>
             <path d="{d}" stroke="{ink}" stroke-width="4.5"/>
           </g>
           <g opacity="0"><set attributeName="opacity" to="1" begin="{start}s"/>
             <circle r="6" fill="{orange}" stroke="{paper}" stroke-width="2.5">
               <animateMotion path="{d}" begin="{start}s" dur="{dur}s" fill="freeze" restart="never"/>
             </circle><set attributeName="opacity" to="0" begin="{fnum(s['start']+s['duration'])}s"/>
           </g>''')
    return '\n'.join(o)

def svg_typography(story):
    p=story['palette'];ink=esc(p['ink']);sage=esc(p['sage'])
    s=[]
    prologue=story.get('prologue','A line grows slowly and leads us into the next chapter.')
    prologue=prologue if isinstance(prologue,list) else [prologue]
    # Opening title card: masthead → title → subtitle → prologue lines, one by one.
    open_bits=[
        fade_group(.12, typetext(71,125,story.get('masthead','THE LINE JOURNAL   /   NO. 01'),18,p['ink'],'letter-spacing="4"')+f'<path d="M72 148H315" stroke="{sage}" stroke-width="2"/>', .7),
        fade_group(.55, typetext(71,280,story['title'],64,p['ink'],'font-weight="600"'), .85),
        fade_group(1.05, typetext(74,345,story.get('subtitle','A SMALL STORY IN LINES'),19,p['sage'],'letter-spacing="4"'), .7),
    ]
    # Prologue three lines — timing overridable for a slower open.
    prog_at=float(story.get('prologueTextAt',1.5))
    prog_step=float(story.get('prologueTextStep',.4))
    prog_fade=float(story.get('prologueTextFade',.65))
    open_bits.extend(fade_group(prog_at+i*prog_step, typetext(74,419+i*42,ln,25,p['ink']), prog_fade) for i,ln in enumerate(prologue))
    # Optional 0%→100% tick under the last prologue line, lasting the intro hold
    # (grow.beginAt − introHold … grow.beginAt), default hold 0.3s.
    hold=float(story.get('introHold',.3)); action=float(story.get('grow',{}).get('beginAt',0) or 0)
    if action>hold>0 and prologue:
        # Hold window = right after last prologue line; Loading + 0%→100% run together.
        pct_y=419+(len(prologue)-1)*42+38; pct_begin=action-hold
        orange=esc(p.get('orange','#D68E5C')); label=esc(story.get('introLoadingText','Loading'))
        loading=f'''<g opacity="0"><set attributeName="opacity" to="1" begin="{pct_begin:.3f}s"/>
          <text x="74" y="{fnum(pct_y)}" font-size="22" font-family="Menlo, Consolas, monospace" fill="{sage}" letter-spacing="2">{label}</text></g>'''
        ticks=[]
        for i in range(101):
            t0=pct_begin+hold*i/100
            bit=f'<set attributeName="opacity" to="1" begin="{t0:.3f}s"/>'
            if i<100:
                bit+=f'<set attributeName="opacity" to="0" begin="{(pct_begin+hold*(i+1)/100):.3f}s"/>'
            ticks.append(f'<g opacity="0">{bit}<text x="188" y="{fnum(pct_y)}" font-size="22" font-family="Menlo, Consolas, monospace" fill="{orange}" letter-spacing="1">{i}%</text></g>')
        open_bits.append(f'<g id="intro-percent">{loading}{"".join(ticks)}</g>')
    s.append(f'''<g font-family="Georgia, 'Noto Serif CJK SC', 'Songti SC', 'STSong', serif">
      {''.join(open_bits)}
    </g>''')
    for idx,ch in enumerate(story['chapters']):
        x,y=vec(ch['labelAt'])
        # First act can fade early while the line/canvas wait on grow.beginAt / chapter start.
        if idx==0 and story.get('introTextAt') is not None:
            begin=max(0,float(story['introTextAt']))
        else:
            begin=max(0,float(ch['start'])+.6)
        headline=ch.get('headline',[ch['title']]);caption=ch.get('caption',[])
        cx,cy=vec(ch.get('captionAt',[x,y+440]))
        # Each chapter line fades in on its own beat (label → headlines → captions).
        # First chapter can use a slower stagger via introTextStep / introTextFade.
        if idx==0:
            step=float(story.get('introTextStep',.7))
            fade_label=float(story.get('introTextFade',.95))
            fade_head=fade_label+.1; fade_cap=fade_label-.05
        else:
            step=.42; fade_label=.7; fade_head=.8; fade_cap=.7
        t=begin;bits=[]
        bits.append(fade_group(t, typetext(x,y, f'{ch.get("number",idx+1):0>2}  /  {ch.get("english","CHAPTER")}',18,p['sage'],'font-family="Georgia, serif" letter-spacing="3"')+f'<path d="M{fnum(x)} {fnum(y+22)}h155" stroke="{sage}" stroke-width="2"/>', fade_label))
        t+=step
        for i,ln in enumerate(headline):
            bits.append(fade_group(t, typetext(x,y+100+i*65,ln,53,p['ink'],'font-weight="600"'), fade_head));t+=step
        for i,ln in enumerate(caption):
            bits.append(fade_group(t, typetext(cx,cy+i*44,ln,27,p['ink']), fade_cap));t+=step*.95
        s.append(f'''<g id="chapter-type-{esc(ch['id'])}" font-family="'Noto Serif CJK SC','Songti SC','STSong',serif">
          {''.join(bits)}
        </g>''')
    H=story['canvas']['height'];signature=story.get('signature','ONE LINE. MANY STORIES.')
    if 'epilogueLines' in story:
        y=float(story.get('epilogueTop',H-134));rows=[]
        for item in story['epilogueLines']:
            item=item if isinstance(item,dict) else {'text':item}
            size=float(item.get('size',32));y+=float(item.get('dy',0))
            extra='text-anchor="middle"'+(' font-weight="600"' if item.get('bold') else '')
            if item.get('latin'):extra+=' font-family="Georgia,serif" letter-spacing="3"'
            rows.append(typetext(375,y,item['text'],size,palette_color(story,item.get('color','ink')),extra))
            y+=size*1.6
        rule=float(story.get('epilogueTop',H-134))-141
        s.append(f'''<g opacity="0" font-family="'Noto Serif CJK SC','Songti SC','STSong',serif">
       {reveal_anim(story.get('epilogueAt',story['duration']-2.1),1.5)}
       <path d="M205 {fnum(rule)}h340" stroke="{sage}" stroke-dasharray="5 10" stroke-width="2"/>
       <circle cx="375" cy="{fnum(rule)}" r="7" fill="{esc(p['orange'])}"/>
       {''.join(rows)}
       {typetext(375,y+12,signature,17,p['sage'],'text-anchor="middle" letter-spacing="4" font-family="Georgia,serif"')}
    </g>''')
        return '\n'.join(s)
    s.append(f'''<g opacity="0" font-family="'Noto Serif CJK SC','Songti SC','STSong',serif">
       {reveal_anim(story['duration']-2.1,1.5)}
       <path d="M205 {fnum(H-275)}h340" stroke="{sage}" stroke-dasharray="5 10" stroke-width="2"/>
       <circle cx="375" cy="{fnum(H-275)}" r="7" fill="{esc(p['orange'])}"/>
       {typetext(375,H-134,story.get('epilogue','May every stretch of the road find something in bloom.'),32,p['ink'],'text-anchor="middle" font-weight="600"')}
       {typetext(375,H-78,signature,17,p['sage'],'text-anchor="middle" letter-spacing="4" font-family="Georgia,serif"')}
    </g>''')
    return '\n'.join(s)

def svg_debug(prepared):
    out=['<g id="anchor-debug" visibility="hidden" pointer-events="none">']
    done=set()
    for c in prepared['connections']:
        if c['object'] in done:continue
        done.add(c['object']);x=c['x'];y=c['y']
        out.append(f'''<circle cx="{x}" cy="{y}" r="22" fill="#F29C90" opacity=".2"/>
         <circle cx="{x}" cy="{y}" r="5" fill="#C45348"/>
         <path d="M{x-22} {y}h44 M{x} {y-22}v44" stroke="#C45348" stroke-width="1.5"/>
         {typetext(x+29,y-18,f'{c["object"]} @{c["revealAt"]}s',16,'#B24943')}''')
    out.append('</g>')
    return ''.join(out)

def svg_gif_accents(decorations, z, gif_mode='inline'):
    """SMIL gates visibility; for browser the source is added at the cue by JS.

    gif_mode:
      inline      - data:image/gif;base64 in <image> (standalone / story.svg)
      placeholder - <image> with no href (browser: JS injects at cue)
      off         - omit decorations
    """
    if gif_mode == 'off':
        return ''
    out = []
    for item in decorations:
        if item['z'] != z:
            continue
        t, duration = item['begin'], item['duration']
        a = item['fadeIn'] / duration
        b = 1 - item['fadeOut'] / duration
        gate = f'''<g id="gif-decor-{esc(item['id'])}" opacity="0" pointer-events="none">
          <animate attributeName="opacity" values="0;1;1;0"
            keyTimes="0;{fnum(a)};{fnum(b)};1" begin="{fnum(t)}s"
            dur="{fnum(duration)}s" fill="freeze" restart="never"/>'''
        href = f' href="data:image/gif;base64,{item["base64"]}"' if gif_mode == 'inline' else ''
        out.append(gate + f'''
          <image id="gif-image-{esc(item['id'])}" x="{fnum(item['x'])}" y="{fnum(item['y'])}"
            width="{fnum(item['width'])}" height="{fnum(item['height'])}"
            preserveAspectRatio="xMidYMid meet"{href}/>
        </g>''')
    return '\n'.join(out)

def story_svg(story,prepared,with_debug=True,decorations=(),gif_mode='inline'):
    W=story['canvas']['width'];H=story['canvas']['height']
    return f'''<svg id="story-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" style="width:100%;height:auto;display:block;overflow:visible;pointer-events:none" role="img" aria-label="{esc(story['title'])}">
      {decor_bg(story)}
      {svg_objects(story,prepared,'back')}
      {svg_gif_accents(decorations,'back',gif_mode)}
      {svg_routes(story,prepared)}
      {svg_objects(story,prepared,'front')}
      {svg_gif_accents(decorations,'front',gif_mode)}
      {svg_typography(story)}
      {svg_debug(prepared) if with_debug else ''}
    </svg>'''

def grow_svg(story, schedule):
    W=story['canvas']['width'];g=story['grow'];initial=g.get('initialPercent',120)
    animations='\n'.join(f'''<animate attributeName="width" values="{fnum(x['from'])}%;{fnum(x['to'])}%" begin="{fnum(x['begin'])}s" dur="{fnum(x['duration'])}s" fill="freeze" restart="never"/>''' for x in schedule)
    return f'''<svg id="grow-svg" xmlns="http://www.w3.org/2000/svg" width="{fnum(initial)}%" viewBox="0 0 {W} {g['spacerUnits']}" preserveAspectRatio="xMidYMid meet" style="display:inline-block;max-width:none !important;vertical-align:top;pointer-events:none">{animations}</svg>'''

def base_svg(story):
    return f'''<svg width="100%" viewBox="0 0 {story['canvas']['width']} {story['grow']['baseUnits']}" style="display:block;width:100%;pointer-events:none"></svg>'''

SOUND_VOICES={'paper','key','bell','gear','pen','hum','wing','tick','blip','click','beep','beep2','connect','switch','train','notify','radio','humback','gpu','glass','keys','rocket','warm'}

def resolve_sound(story, prepared):
    spec=story.get('sound')
    if not spec: return None
    arrivals={item['object']:item['lineArrival'] for item in prepared['connections']}
    def mark(value, label):
        if isinstance(value,str):
            if value not in arrivals: raise ValueError(f'sound {label} unknown hit: {value}')
            return arrivals[value]
        if isinstance(value,(int,float)): return float(value)
        raise ValueError(f'sound {label} must be a time or object id')
    cues=[]
    for item in spec.get('cues',[]):
        voice=item.get('id')
        if voice not in SOUND_VOICES: raise ValueError(f'unknown sound voice: {voice}')
        if 'hit' in item: t=mark(item['hit'],'cue')+float(item.get('offset',0))
        elif 't' in item: t=float(item['t'])
        else: raise ValueError('sound cue needs t or hit')
        if not 0<=t<=float(story['duration'])+0.05: raise ValueError(f'sound cue out of range: {voice}@{t:.2f}')
        cues.append({'t':round(t,2),'id':voice})
    cues.sort(key=lambda cue:(cue['t'],cue['id']))
    bed=spec.get('bed')
    resolved_bed=None
    if bed:
        silence=bed.get('silence',[story['duration'],story['duration']])
        resolved_bed={
            'start':round(mark(bed.get('start',0),'bed.start'),2),
            'silence':[round(mark(silence[0],'bed.silence'),2),round(mark(silence[1],'bed.silence'),2)],
            'fadeOut':round(mark(bed.get('fadeOut',story['duration']),'bed.fadeOut'),2),
            'fadeDur':float(bed.get('fadeDur',4)),
        }
    return {'cues':cues,'bed':resolved_bed}

# HTML and controls are separate small templates so designers can change the frame without the core compiler.
def render_html(story, prepared, schedule, decorations=()):
    art=story_svg(story,prepared,with_debug=True,decorations=decorations,gif_mode='placeholder')
    grow=grow_svg(story,schedule);base=base_svg(story)
    css=(ROOT/'templates/browser.css').read_text(encoding='utf8')+chrome_css(story['palette'], story['canvas'].get('background',PAPER))
    js=(ROOT/'templates/controls.js').read_text(encoding='utf8')
    samples=[]
    for i in range(round(story['duration']*4)+1):
        t=min(story['duration'],i*.25);x,y=tip_at(prepared,t);samples.append(round(y,2))
    js=js.replace('/*__TIMELINE_CONFIG__*/',f'const TIMELINE={json.dumps({"duration":story["duration"],"height":story["canvas"]["height"],"width":story["canvas"]["width"],"tipYs":samples},separators=(",",":"))};')
    gif_config = [{'id':d['id'],'begin':d['begin'],'end':d['end'],'base64':d['base64']} for d in decorations]
    js=js.replace('/*__GIF_ACCENTS__*/', 'const GIF_ACCENTS='+json.dumps(gif_config,separators=(',',':'))+';')
    sound=resolve_sound(story, prepared)
    js=js.replace('/*__SOUND_CONFIG__*/', 'const SOUND='+('null' if sound is None else json.dumps(sound,separators=(',',':')))+';')
    sound_btn='<button id="btn-sound" type="button" aria-pressed="false">♪ Sound</button>' if sound else ''
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
         <meta name="description" content="{esc(story['theme'])} · an SVG + SMIL hand-drawn scroll, with optional transparent GIF accents"><title>{esc(story['title'])} · SVG Line Story</title>
         <style>{css}</style></head><body>
         <header class="topbar"><div class="top-inner"><span class="brand-mark">〰</span><span class="brand-name">LINE / STORY</span><span class="brand-sub">SVG · SMIL{' · GIF ACCENTS' if decorations else ''}</span><span class="edition">EDITION 001</span></div></header>
         <div class="kicker"><span class="kicker-line"></span><span>A STORY DRAWN IN A SINGLE THREAD</span></div>
         <main id="paper" class="paper"><div id="stage" class="stage">
             <section class="canvas-layer">{art}</section>
             <section class="grow-layer">{grow}</section>
             <section class="base-layer">{base}</section>
         </div></main>
         <div class="footer-note"><span>ONE THREAD · {len(story['chapters'])} CHAPTERS · {int(story['duration'])} SECONDS</span><span>VECTOR STORY{' + GIF DETAILS' if decorations else ''}</span></div>
         <div class="dock-slot"><div class="dock" role="group" aria-label="Scroll playback controls"><div class="dock-title"><span><i class="dot"></i> STORY TIMELINE</span><span class="dock-tools">{sound_btn}<span id="clock">00:00 / {int(story['duration'])//60:02d}:{int(story['duration'])%60:02d}</span></span></div>
           <input type="range" id="seek" min="0" max="{story['duration']}" step="0.05" value="0" aria-label="Seek the story timeline">
           <div class="buttons"><button id="btn-play" type="button">Ⅱ Pause</button><button id="btn-restart" type="button">↺ Replay</button><button id="btn-follow" class="selected" type="button">◉ Follow</button><button id="btn-debug" type="button">⊹ Anchors</button></div>
         </div><button type="button" class="dock-peek" id="dock-peek" tabindex="-1" aria-hidden="true" aria-label="Show the scroll controls"><span class="dock-peek-bar"></span></button></div><script>{js}</script></body></html>'''


def build(source:Path,out:Path):
    story=json.loads(source.read_text(encoding='utf8'))
    prepared=prepare(story);schedule=grow_schedule(story,prepared)
    decorations=load_decorations(story,prepared,source.parent)
    out.mkdir(parents=True,exist_ok=True)
    (out/'index.html').write_text(render_html(story,prepared,schedule,decorations=decorations),encoding='utf8')
    (out/'story.svg').write_text(story_svg(story,prepared,decorations=decorations),encoding='utf8')
    for d in decorations:
        target=out/d['src']
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.resolve() != (source.parent/d['src']).resolve():
            shutil.copy2(source.parent/d['src'],target)
    (out/'story.json').write_text(json.dumps(story,ensure_ascii=False,indent=2),encoding='utf8')
    result={'title':story['title'],'theme':story['theme'],'duration':story['duration'],
      'objectPins':[{'object':o['id'],'x':round(o['anchor'][0],2),'y':round(o['anchor'][1],2)} for o in prepared['objects'].values()],
      'cues':{k:round(v,2) for k,v in prepared['cues'].items()},'connections':prepared['connections'],
      'pathLengths':{s['id']:round(s['length'],2) for s in prepared['segments']},
       'grow':schedule,'warnings':prepared['warnings'],
      'gifDecorations':[{'id':d['id'],'src':d['src'],'begin':d['begin'],'end':d['end'],
                         'naturalDuration':d['naturalDuration'],'mode':d['playback'],
                         'frames':d['gifInfo']['frames'],'loopCount':d['gifInfo']['loopCount']}
                        for d in decorations]}
    (out/'cues.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    lines=[f'# {story["title"]} · Storyboard','',
           f'**Theme**: {story["theme"]}  **Duration**: {story["duration"]} seconds  **Palette**: {story.get("paletteName","custom")}  **Arc**: {story.get("arc","three_act")}',
           '', '| Chapter | Time | Scene | Objects the line must hit |','|---|---|---|---|']
    for ch in story['chapters']:
        hits=', '.join(str(x['hit']) for x in ch['route'] if isinstance(x,dict))
        role=ch.get('role', '')
        lines.append(f'| {ch.get("number", "")} | {fnum(ch["start"])}–{fnum(ch["start"]+ch["duration"])}s | {role} {ch["title"]} · {" / ".join(ch.get("headline", []))} | {hits} |')
    lines+=['','## Path cues','', '| Object | Arrival | Reveal | Position |','|---|---:|---:|---|']
    for c in prepared['connections']:
        lines.append(f'| {c["object"]} | {c["lineArrival"]:.2f}s | {c["revealAt"]:.2f}s | ({c["x"]:.1f}, {c["y"]:.1f}) |')
    if decorations:
        lines+=['','## Small GIF accents (they do not replace the SVG)','',
                '| GIF | Area | Starts | Ends | Playback |','|---|---|---:|---:|---|']
        for d in decorations:
            lines.append(f'| {d["id"]} | {d["src"]} | {d["begin"]:.2f}s | {d["end"]:.2f}s | {d["playback"]} |')
    lines+=['','## Review notes','', '- Positions are 750px design units, not CSS pixels.',
            '- The path, the heroes, and the important motion stay inline SVG. Small transparent GIFs are local decoration only.',
            '- The browser page mounts each GIF at its cue. After a pause or a seek it starts again from the first frame. Frame-accurate GIF seeking is not supported.',
            '- story.svg embeds GIFs up front. SMIL only controls visibility, so a GIF may not begin on its first frame when it appears.']
    (out/'STORYBOARD.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(f'Generated: {out.resolve()}')
    print('Paths:',result['pathLengths']);print('Cues:',result['cues'])
    print('SVG path/anchor errors:',[item['pathPointError'] for item in result['connections']])
    print('Grow final:',result['grow'][-1]['visibleDesignHeight'])
    return out


def main():
    parser=argparse.ArgumentParser(description='Compile story.json into pure SVG + SMIL long-scroll pages (zero Python deps).')
    parser.add_argument('--input',default=str(ROOT/'examples/spring/story.json'))
    parser.add_argument('--output',default=str(ROOT/'examples/spring/dist'))
    args=parser.parse_args()
    try:build(Path(args.input),Path(args.output))
    except (KeyError,ValueError,TypeError,FileNotFoundError) as e:
        print('Compilation failed:',e,file=sys.stderr);sys.exit(1)

if __name__=='__main__':main()
