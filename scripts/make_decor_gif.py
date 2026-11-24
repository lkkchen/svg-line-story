#!/usr/bin/env python3
"""Create tiny transparent line-art GIF accents for the SVG Story Director.

This OPTIONAL asset-authoring script needs Pillow. The story compiler does not.
Usage: python3 scripts/make_decor_gif.py --kind petals --output stories/<slug>/assets/petals.gif
"""
from __future__ import annotations
import argparse
import math
from pathlib import Path
try:
    from PIL import Image, ImageDraw
except ImportError as e:
    raise SystemExit('Asset generation needs Pillow: python3 -m pip install pillow') from e

from palettes import gif_slots


def frame(kind, index, total, size, slots):
    w,h=size
    t=index/total
    im=Image.new('P',size,0)
    flat=[v for triplet in slots for v in triplet] + [0,0,0] * (256 - len(slots))
    im.putpalette(flat)
    d=ImageDraw.Draw(im)
    if kind == 'sparkles':
        dots=[(.23,.59,9,0),(.53,.36,14,.31),(.72,.66,11,.6),(.36,.22,7,.13)]
        for x0,y0,r,phase in dots:
            x=int(x0*w);y=int(y0*h)
            f=.5+.5*math.sin(2*math.pi*(t+phase))
            rr=max(1,int(r*f)); col=7 if f>.7 else 4
            d.line((x-rr,y,x+rr,y),fill=col,width=2)
            d.line((x,y-rr,x,y+rr),fill=col,width=2)
            if rr>4:
                d.ellipse((x-2,y-2,x+2,y+2),fill=3)
        d.arc((int(w*.1),int(h*.24),int(w*.85),int(h*.84)),20,90,fill=2,width=1)
    elif kind == 'petals':
        for j in range(5):
            q=(t+(j*.19))%1
            x=int(w*(.16+.7*((j*.27+q*.55)%1)))
            y=int(h*(-.2+1.35*q))
            angle=(j*37+t*160) * math.pi/180
            rx=9+((j*3)%5);ry=4+(j%3)
            dx=rx*math.cos(angle);dy=rx*math.sin(angle)
            # Two soft nested outlines make petal-like hand-drawn accents.
            d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=4,outline=6,width=1)
            d.line((x-dx*.5,y-dy*.5,x+dx*.5,y+dy*.5),fill=6,width=1)
        d.arc((12,14,w-12,h-15),210,262,fill=2,width=1)
    elif kind == 'ripples':
        for k in range(3):
            u=(t+k/3)%1
            rx=13+int(u*(w*.38))
            ry=3+int(u*(h*.16))
            cx=w//2; cy=int(h*.49+k*5)
            col=[1,2,8][k]
            d.arc((cx-rx,cy-ry,cx+rx,cy+ry),188,345,fill=col,width=2)
            d.arc((cx-rx,cy-ry,cx+rx,cy+ry),8,154,fill=col,width=1)
        for j in range(3):
            x=int(w*(.25+.25*j));y=int(h*(.26+.12*math.sin((t+j*.3)*2*math.pi)))
            d.ellipse((x-2,y-2,x+2,y+2),fill=5,outline=1)
    elif kind == 'flutter':
        cx=w//2;cy=h//2
        fl=.15+.85*abs(math.cos(2*math.pi*t*2))
        dx=12+round(fl*23)
        d.ellipse((cx-dx,cy-23,cx-3,cy+3),fill=4,outline=1,width=2)
        d.ellipse((cx+3,cy-23,cx+dx,cy+3),fill=4,outline=1,width=2)
        d.ellipse((cx-dx+9,cy,cx-3,cy+18),fill=7,outline=1,width=2)
        d.ellipse((cx+3,cy,cx+dx-9,cy+18),fill=7,outline=1,width=2)
        d.line((cx,cy-13,cx,cy+16),fill=1,width=3)
        d.arc((cx-14,cy-24,cx+3,cy-9),175,245,fill=1,width=1)
        d.arc((cx-3,cy-24,cx+14,cy-9),295,365,fill=1,width=1)
    else:
        raise ValueError(f'Unknown GIF kind: {kind}')
    return im


def generate(output,kind='petals',width=160,height=110,frames=24,frame_ms=90,playback='once',palette='spring'):
    if not 80 <= width <= 480 or not 60 <= height <= 360:
        raise ValueError('GIF size: width 80-480, height 60-360')
    if not 8 <= frames <= 72:
        raise ValueError('frames must be 8-72')
    slots=gif_slots(palette)
    imgs=[frame(kind,i,frames,(width,height),slots) for i in range(frames)]
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    kwargs={'save_all':True,'append_images':imgs[1:],'duration':frame_ms,
            'transparency':0,'disposal':2,'optimize':False}
    if playback == 'loop':kwargs['loop']=0
    imgs[0].save(output,format='GIF',**kwargs)
    return output


def main():
    p=argparse.ArgumentParser(description='Transparent, small, vector-like GIF embellishment generator (optional Pillow)')
    p.add_argument('--kind',choices=['sparkles','petals','ripples','flutter'],default='petals')
    p.add_argument('--output',required=True)
    p.add_argument('--width',type=int,default=160)
    p.add_argument('--height',type=int,default=110)
    p.add_argument('--frames',type=int,default=24)
    p.add_argument('--frame-ms',type=int,default=90)
    p.add_argument('--playback',choices=['once','loop'],default='once')
    p.add_argument('--palette',default='spring',help='Palette id or English name. It must match paletteName in story.json.')
    a=p.parse_args()
    print(generate(a.output,a.kind,a.width,a.height,a.frames,a.frame_ms,a.playback,a.palette))

if __name__=='__main__':main()
