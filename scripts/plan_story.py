#!/usr/bin/env python3
"""Offline fallback story planner. The Agent should elaborate beyond these presets.
This command takes exactly one theme and writes a structurally valid V1-style outline.
"""
import argparse, copy, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from palettes import palette_roles, resolve_palette
from arcs import motions_for, resolve_arc, suggest_arc

ROOT=Path(__file__).resolve().parents[1]
DEFAULT=ROOT/'examples/spring/story.json'

PRESETS={
  'spring': {'terms':['春','种子','生长','花朵','花开','植物','治愈'],
    'title':'一笔画出春天','subtitle':'A LINE INTO SPRING','m':['sprout','flower','boat'],'opener':'pencil',
    'heads':[['有些故事，','从一颗种子开始。'],['等一朵花，','慢慢盛开。'],['把春天，','送到远方。']],
    'beat':['一颗小小的种子醒来。','等待的花朵终于绽放。','带着希望轻轻远行。'],'ending':'愿每一段路，都有花开。'},
  'forest':{'terms':['森林','树木','林间','叶子','山林'],
    'title':'走进一座森林','subtitle':'A LINE INTO THE WOODS','m':['leaf','tree','moon'],'opener':'hill',
    'heads':[['跟着一片叶，','走进森林。'],['遇见一棵树，','听见微风。'],['月亮升起时，','故事还在继续。']],
    'beat':['线条捡起一片叶子。','曲线绕过一棵大树。','夜色里遇见弯弯的月亮。'],'ending':'每一片叶子，都有自己的方向。'},
  'ocean':{'terms':['海洋','大海','海边','海岛','海浪','灯塔'],
    'title':'沿着线去看海','subtitle':'A THREAD TO THE SEA','m':['shell','boat','lighthouse'],'opener':'wave',
    'heads':[['捡起一枚，','海边的贝壳。'],['让小纸船，','跟着浪花走。'],['遥远的光，','正在等着我们。']],
    'beat':['细线绕过一枚贝壳。','水纹托起小纸船。','曲线经过远方灯塔。'],'ending':'愿每次启航，都能遇见光。'},
  'stars':{'terms':['星空','星星','宇宙','银河','航天','太空','梦想'],
    'title':'把星星串起来','subtitle':'A LINE OF LITTLE STARS','m':['star','kite','rocket'],'opener':'moon',
    'heads':[['心里藏着，','一颗小星星。'],['抬头时，','风筝飞得更高。'],['所有远方，','都有启程的理由。']],
    'beat':['一颗星星闪烁。','风筝线连接夜空。','想象力变成小火箭。'],'ending':'慢慢长大，也别忘记抬头。'},
  'books':{'terms':['书','阅读','知识','图书','学习','书店'],
    'title':'一本书的旅程','subtitle':'FROM WORDS TO WORLDS','m':['book','butterfly','lantern'],'opener':'leaf',
    'heads':[['翻开一页，','故事开始了。'],['纸上的小梦，','轻轻飞起来。'],['一盏灯下，','遇见更大的世界。']],
    'beat':['翻开的书连接第一条线。','想象力飞成一只蝴蝶。','最后化作温暖的灯光。'],'ending':'愿每一本书，都能照亮远方。'},
  'birthday':{'terms':['生日','庆祝','礼物','祝福','节日'],
    'title':'把祝福画成线','subtitle':'A HAPPY LITTLE WISH','m':['gift','balloon','star'],'opener':'heart',
    'heads':[['一个礼物，','装满心意。'],['祝福乘着风，','飘向天空。'],['最后一颗星，','亮起了。']],
    'beat':['礼物送出惊喜。','一只气球缓缓上升。','希望变成天边的星光。'],'ending':'把快乐和愿望，都好好收藏。'},
  'city':{'terms':['城市','街道','小镇','家乡','社区','建筑'],
    'title':'一条线逛小城','subtitle':'A LITTLE CITY WALK','m':['house','tree','lantern'],'opener':'sun',
    'heads':[['推开门，','看见清晨。'],['树影斑驳，','时间慢下来。'],['灯光亮起，','城市有了温度。']],
    'beat':['曲线从小屋起步。','绕过街边大树。','最后停在晚归的灯光里。'],'ending':'每一处小小日常，都值得珍惜。'},
  'travel':{'terms':['旅行','旅程','远方','出发','探索','冒险'],
    'title':'沿着线去远方','subtitle':'A SMALL ADVENTURE','m':['kite','boat','lighthouse'],'opener':'cloud',
    'heads':[['背上小小的梦，','出发吧。'],['有风，有浪，','也有好天气。'],['远方的灯光，','等我们抵达。']],
    'beat':['风筝线指明第一段路。','纸船轻轻扬帆。','灯塔出现在旅途尽头。'],'ending':'路的尽头，是新的开始。'},
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
    found=next((p for p in PRESETS.values() if any(key in text for key in p['terms'])),None)
    if found is None:
        # A coherent generic draft; the Agent must use its own reasoning to design bespoke motifs and scenes.
        found={'title':text[:5]+'的旅程','subtitle':'ONE LINE, ONE STORY',
          'm':['leaf','heart','star'],'opener':'sun',
          'heads':[['一条小小的线，','悄悄出发。'],['在路的中间，','遇见温柔。'],['继续向前，','就会有光。']],
          'beat':['线条成为故事的起点。','途中发生一次改变。','把主题转化为温暖的结尾。'],
          'ending':'愿每一段故事，都有回响。'}
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
        ch['title']=['启程','相遇','远方'][idx] if found is not PRESETS['spring'] else ['初醒','盛放','远行'][idx]
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
    pa.add_argument('theme',help='任意中文主题，例如：森林里的星光、海边的一封信')
    pa.add_argument('--palette',help='色板 id 或中文名，例如 sea / 海盐。省略则沿用春笺')
    pa.add_argument('--arc',help='叙事弧 id 或中文名，例如 timeline / 时间线。省略则按主题推荐')
    pa.add_argument('--output','-o',default='story.json')
    args=pa.parse_args()
    result=plan(args.theme, palette=args.palette, arc=args.arc)
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(f'Created {path} for theme: {args.theme}\nNext: compile with compile_story.py --input {path}')
    print('Note: The offline planner is a motif-limited first draft. A creative Agent should rewrite beats/geometry for unique themes.')
    print('Note: The spring pencil opening is sample framing only. Non-spring drafts start on a theme object; replace that opener with this story\'s own origin.')

if __name__=='__main__':main()
