#!/usr/bin/env python3
"""Narrative arcs for a three-chapter line scroll.

These are story skeletons, not visual styles. Ads arcs that end on a call to
action are intentionally absent: the scroll stays a line that arrives somewhere.
Usage:
  python3 scripts/arcs.py --suggest '一座城市的变迁'
"""
from __future__ import annotations
import argparse, copy, json

ARCS = [
    {
        'id': 'three_act', 'order': 0, 'name': '三幕',
        'line': '同一根线完成一次变化，结尾回到开头的物件或情绪',
        'fits': [],
        'roles': ['起因', '转折', '回响'],
        'emphasis': ['sage', 'orange', 'ink'],
        'motions': ['draw', 'pop', 'still'],
    },
    {
        'id': 'timeline', 'order': 1, 'name': '时间线',
        'line': '同一根线表示时间向前，不往回跳',
        'fits': ['历史', '变迁', '起源', '演变', '年代', '一生', '过去', '未来', '成长'],
        'roles': ['起点', '经过', '此刻'],
        'emphasis': ['ink', 'sage', 'orange'],
        'motions': ['draw', 'sway', 'still'],
    },
    {
        'id': 'man_in_hole', 'order': 2, 'name': '跌入再爬出',
        'line': '线先下沉，再抬到比起点更高的位置',
        'fits': ['失败', '失去', '迷路', '困境', '重新', '归来', '痊愈', '低谷', '跌倒'],
        'roles': ['原本安稳', '坠落', '爬出来'],
        'emphasis': ['sage', 'ink', 'orange'],
        'motions': ['sway', 'draw', 'pop'],
    },
    {
        'id': 'myth_buster', 'order': 3, 'name': '误区纠正',
        'line': '线先穿过一个看起来成立的物件，再折向真正的原因',
        'fits': ['误区', '其实', '真相', '谣言', '以为'],
        'roles': ['大家以为', '其实不然', '因此'],
        'emphasis': ['rose', 'ink', 'orange'],
        'motions': ['still', 'draw', 'pop'],
    },
    {
        'id': 'how_it_works', 'order': 4, 'name': '怎么发生',
        'line': '线按真实顺序穿过步骤，不先给结局再倒叙',
        'fits': ['如何', '怎么', '原理', '步骤', '方法', '制作'],
        'roles': ['先看见', '中间一步', '所以如此'],
        'emphasis': ['orange', 'sage', 'ink'],
        'motions': ['pop', 'draw', 'still'],
    },
    {
        'id': 'story_spine', 'order': 5, 'name': '故事脊柱',
        'line': '线从重复的日常里岔出一次，再回到被改变的日常',
        'fits': ['每天', '直到', '从前', '从此', '忽然', '有一天'],
        'roles': ['每天如此', '直到有一天', '从此以后'],
        'emphasis': ['sage', 'orange', 'rose'],
        'motions': ['sway', 'pop', 'still'],
    },
]


def resolve_arc(token):
    key = str(token).strip().lower()
    for item in ARCS:
        if key == item['id'] or key == item['name'].lower():
            return copy.deepcopy(item)
    names = ', '.join(f"{item['name']}({item['id']})" for item in ARCS)
    raise ValueError(f'Unknown arc: {token}. Choose one of: {names}')


def motions_for(spec, motion='calm'):
    """Last beat stays still. Adjacent beats do not share a family."""
    seq = list(spec['motions'])
    if motion == 'punchy' and seq and seq[0] == 'draw':
        seq[0] = 'pop'
    if motion == 'calm' and seq and seq[0] == 'pop':
        seq[0] = 'draw'
    if seq:
        seq[-1] = 'still'
    families = ['draw', 'pop', 'sway']
    for index in range(1, max(0, len(seq) - 1)):
        if seq[index] == seq[index - 1]:
            seq[index] = next(name for name in families if name != seq[index - 1])
    if len(seq) >= 2 and seq[-1] == seq[-2]:
        blocked = {seq[-1]}
        if len(seq) >= 3:
            blocked.add(seq[-3])
        seq[-2] = next(name for name in families if name not in blocked)
    return seq


def _score(text, spec):
    hits = [term for term in spec['fits'] if term in text]
    return sum(len(term) for term in hits), hits


def suggest_arc(topic, motion='calm'):
    text = topic.strip()
    if not text:
        raise ValueError('Theme cannot be empty')
    ranked = []
    for spec in ARCS:
        score, hits = _score(text, spec)
        ranked.append((score, spec['order'], spec, hits))
    ranked.sort(key=lambda row: (-row[0], row[1]))
    if ranked[0][0] == 0:
        best = resolve_arc('three_act')
        because = '主题没有更具体的骨架，用三幕'
    else:
        best = copy.deepcopy(ranked[0][2])
        because = '主题里有「' + '、'.join(ranked[0][3][:3]) + '」'
    alternate = next(spec for spec in ARCS if spec['id'] != best['id'])
    arc = {
        'id': best['id'],
        'name': best['name'],
        'line': best['line'],
        'roles': list(best['roles']),
        'emphasis': list(best['emphasis']),
        'motions': motions_for(best, motion),
        'because': because,
    }
    return {
        'topic': text,
        'arc': arc,
        'alternate': {'id': alternate['id'], 'name': alternate['name'], 'line': alternate['line']},
    }


def main():
    parser = argparse.ArgumentParser(description='按主题推荐长卷叙事弧')
    parser.add_argument('--suggest', metavar='THEME')
    parser.add_argument('--motion', choices=['calm', 'punchy'], default='calm', help='来自所选色板的动作幅度')
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    if args.suggest:
        result = suggest_arc(args.suggest, args.motion)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return
        arc = result['arc']
        print(f"主题「{result['topic']}」")
        print(f"叙事弧：{arc['name']} {arc['id']} · 推荐")
        print(f"依据：{arc['because']}")
        print(f"线的含义：{arc['line']}")
        print('三幕：' + ' → '.join(arc['roles']))
        print('主角色色：' + ' → '.join(arc['emphasis']))
        print('主角动作：' + ' → '.join(arc['motions']))
        alt = result['alternate']
        print(f"也可改成：{alt['name']} {alt['id']}（{alt['line']}）")
        return
    if not args.list:
        parser.error('pass --suggest THEME or --list')
    for spec in ARCS:
        print(f"{spec['name']} ({spec['id']}) · {spec['line']}")


if __name__ == '__main__':
    main()
