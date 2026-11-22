#!/usr/bin/env python3
"""Named line-art palettes for SVG Story Director.

Role names stay stable across every set: ink is the line and type color,
sage is the second fill, orange is the accent, rose is the soft third fill,
sky and light are pale washes. paper is the page. Changing a set recolors
the scroll; it does not change the drawing grammar.

Usage:
  python3 scripts/palettes.py --suggest '海边的一封信'
  python3 scripts/palettes.py --list
"""
from __future__ import annotations
import argparse, copy, json

ROLES = ('ink', 'sage', 'orange', 'rose', 'sky', 'light')

# Look package beyond the six role colors. motion is the energy of entrances,
# finish is how fills are rationed, typeStyle is the headline voice.
LOOK = {
    'spring': {'motion': 'calm', 'typeStyle': '衬线标题，字距松开', 'finish': '留白多，暖色只占小块'},
    'sea': {'motion': 'calm', 'typeStyle': '衬线标题，字距松开', 'finish': '浅色如水纹，少用大块平涂'},
    'forest': {'motion': 'calm', 'typeStyle': '衬线标题，字距松开', 'finish': '叶子用辅色，点缀只做果子或光'},
    'dusk': {'motion': 'calm', 'typeStyle': '衬线标题，字距松开', 'finish': '藕荷底上少用亮色'},
    'lantern': {'motion': 'punchy', 'typeStyle': '衬线标题略重，英文标签收紧', 'finish': '点缀色只给灯和印，入场短促'},
    'snow': {'motion': 'calm', 'typeStyle': '衬线标题，字距松开', 'finish': '大留白，柿子红只出现一次'},
    'ink': {'motion': 'calm', 'typeStyle': '衬线标题，字距更松', 'finish': '除印章红外尽量不填色'},
    'night': {'motion': 'calm', 'typeStyle': '衬线标题，字距松开', 'finish': '深底上线条用暖白，填色更少'},
    'citrus': {'motion': 'punchy', 'typeStyle': '衬线标题略重，英文标签收紧', 'finish': '辅色可以更饱和，弹出更快'},
    'blossom': {'motion': 'calm', 'typeStyle': '衬线标题，字距松开', 'finish': '粉色只做花和点，叶子仍用辅色'},
    'cafe': {'motion': 'calm', 'typeStyle': '衬线标题，字距松开', 'finish': '褐色线，焦糖只做杯沿或光点'},
    'cosmos': {'motion': 'calm', 'typeStyle': '衬线标题，字距松开', 'finish': '深底，星星用点缀色'},
}

# The historical V1 set. Built-in motifs keep their authored hex fills only
# when a story still uses these exact colors on this paper.
SPRING = {
    'id': 'spring',
    'paper': '#FCFAF4',
    'ink': '#375763',
    'sage': '#98B99F',
    'orange': '#D68E5C',
    'rose': '#F0C5B6',
    'sky': '#E5EDEA',
    'light': '#E5ECE2',
}

PALETTES = [
    {
        'id': 'spring', 'order': 0, 'name': '春笺', 'surface': 'light',
        'mood': '奶油纸，墨蓝线，鼠尾草绿和暖杏',
        'fits': ['春', '种子', '花开', '生长', '治愈', '花园', '田野', '嫩芽', '春天'],
        **{k: SPRING[k] for k in ('paper', *ROLES)},
    },
    {
        'id': 'sea', 'order': 1, 'name': '海盐', 'surface': 'light',
        'mood': '浅海纸，深青线，海藻绿和沙金',
        'fits': ['海', '沙滩', '灯塔', '贝壳', '船', '岛', '浪', '渔', '港', '潮', '海洋'],
        'paper': '#F3F7F6', 'ink': '#163E4C', 'sage': '#2F7C78',
        'orange': '#D08948', 'rose': '#F0C4B0', 'sky': '#D5E8E5', 'light': '#E5F0ED',
    },
    {
        'id': 'forest', 'order': 2, 'name': '林间', 'surface': 'light',
        'mood': '草木纸，松烟线，苔绿和陶土橙',
        'fits': ['森林', '树林', '林间', '叶子', '树叶', '大树', '山林', '苔藓', '蘑菇', '树'],
        'paper': '#F3F0E4', 'ink': '#1E3326', 'sage': '#4F7346',
        'orange': '#C4622E', 'rose': '#E2BC94', 'sky': '#D9E3CE', 'light': '#E7EDDC',
    },
    {
        'id': 'dusk', 'order': 3, 'name': '暮紫', 'surface': 'light',
        'mood': '藕荷纸，暮紫线，橄榄辅色和梅粉',
        'fits': ['黄昏', '暮色', '薰衣草', '回忆', '紫色', '暮'],
        'paper': '#F6F1F7', 'ink': '#332C4E', 'sage': '#6E7F62',
        'orange': '#C67B62', 'rose': '#E4B8CC', 'sky': '#E6DCEC', 'light': '#EFE6F1',
    },
    {
        'id': 'lantern', 'order': 4, 'name': '灯会', 'surface': 'light',
        'mood': '暖宣纸，朱褐线，青铜辅色和正红点缀',
        'fits': ['灯笼', '花灯', '灯会', '春节', '元宵', '庙会', '中秋', '团圆', '红灯'],
        'paper': '#FBF3EA', 'ink': '#5C241F', 'sage': '#7A6244',
        'orange': '#E24B32', 'rose': '#F0B39A', 'sky': '#F4E0D0', 'light': '#F7EADF',
    },
    {
        'id': 'snow', 'order': 5, 'name': '初雪', 'surface': 'light',
        'mood': '雪青纸，石板蓝线，霜蓝辅色和柿子红',
        'fits': ['雪', '冬天', '冬日', '冰', '霜', '寒冷'],
        'paper': '#F5F8FB', 'ink': '#2C3E52', 'sage': '#6E8EA3',
        'orange': '#E06A4F', 'rose': '#E4D0CB', 'sky': '#E2EDF5', 'light': '#EEF3F7',
    },
    {
        'id': 'ink', 'order': 6, 'name': '水墨', 'surface': 'light',
        'mood': '宣纸，浓墨线，淡墨辅色和一枚印章红',
        'fits': ['水墨', '书法', '国画', '宣纸', '山水', '墨色'],
        'paper': '#F6F3EC', 'ink': '#242422', 'sage': '#7A756C',
        'orange': '#C4312A', 'rose': '#E3D5C8', 'sky': '#EBE6DE', 'light': '#F0EBE4',
    },
    {
        'id': 'night', 'order': 7, 'name': '夜航', 'surface': 'dark',
        'mood': '夜色纸，暖白线，月青辅色和琥珀点缀',
        'fits': ['深夜', '黑夜', '午夜', '夜晚', '夜航', '入夜'],
        'paper': '#17202C', 'ink': '#F3E7D0', 'sage': '#7EAF9E',
        'orange': '#E3A45A', 'rose': '#D9A898', 'sky': '#243246', 'light': '#1E2A3A',
    },
    {
        'id': 'citrus', 'order': 8, 'name': '柑橘', 'surface': 'light',
        'mood': '暖白纸，橄榄绿线，亮叶绿和柑橘橙',
        'fits': ['夏天', '阳光', '柠檬', '橙子', '柑橘', '水果', '活力'],
        'paper': '#FFF8EE', 'ink': '#2E3A22', 'sage': '#6E9A32',
        'orange': '#F0841E', 'rose': '#F6C896', 'sky': '#F6E6C4', 'light': '#FBF3DE',
    },
    {
        'id': 'blossom', 'order': 9, 'name': '樱时', 'surface': 'light',
        'mood': '浅樱纸，梅褐线，嫩叶绿和樱粉',
        'fits': ['樱', '桃花', '告白', '恋爱', '粉色'],
        'paper': '#FFF6F6', 'ink': '#5A3140', 'sage': '#8EAA8C',
        'orange': '#E06B86', 'rose': '#F6C2C8', 'sky': '#F8E4E6', 'light': '#FDEEEE',
    },
    {
        'id': 'cafe', 'order': 10, 'name': '咖啡馆', 'surface': 'light',
        'mood': '咖啡纸，深褐线，橄榄辅色和焦糖',
        'fits': ['咖啡', '书店', '阅读', '面包', '下午茶', '街角'],
        'paper': '#F6EFE6', 'ink': '#3A291F', 'sage': '#6F7D52',
        'orange': '#C47A3A', 'rose': '#E4C2A4', 'sky': '#EFE2D2', 'light': '#F4EBDF',
    },
    {
        'id': 'cosmos', 'order': 11, 'name': '星海', 'surface': 'dark',
        'mood': '夜空纸，星光白线，藤紫辅色和星金',
        'fits': ['星', '宇宙', '银河', '太空', '火箭', '夜空'],
        'paper': '#141628', 'ink': '#E8E3F6', 'sage': '#9A9AD4',
        'orange': '#F0B14E', 'rose': '#D4A8C8', 'sky': '#262844', 'light': '#1C1E36',
    },
]


def _rgb(value):
    h = str(value).strip().lstrip('#')
    if len(h) != 6:
        raise ValueError(f'Expected #RRGGBB, got {value}')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(rgb):
    return '#{:02X}{:02X}{:02X}'.format(*[max(0, min(255, int(round(c)))) for c in rgb])


def mix(a, b, t):
    t = max(0.0, min(1.0, float(t)))
    left, right = _rgb(a), _rgb(b)
    return _hex(tuple(left[i] * (1 - t) + right[i] * t for i in range(3)))


def _channel(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rel_luminance(value):
    r, g, b = _rgb(value)
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast(a, b):
    hi, lo = rel_luminance(a), rel_luminance(b)
    if hi < lo:
        hi, lo = lo, hi
    return (hi + 0.05) / (lo + 0.05)


def _norm(value):
    return str(value).strip().upper()


def is_spring_colors(palette):
    if not all(_norm(palette.get(k, '')) == _norm(SPRING[k]) for k in ROLES):
        return False
    paper = palette.get('paper')
    return paper is None or _norm(paper) == _norm(SPRING['paper'])


def _with_look(item):
    row = copy.deepcopy(item)
    row.update(LOOK.get(row['id'], {}))
    return row


def resolve_palette(token):
    key = str(token).strip().lower()
    for item in PALETTES:
        if key == item['id'] or key == item['name'].lower():
            return _with_look(item)
    names = ', '.join(f"{item['name']}({item['id']})" for item in PALETTES)
    raise ValueError(f'Unknown palette: {token}. Choose one of: {names}')


def palette_roles(spec):
    return {k: spec[k] for k in ROLES}


def _distance(a, b):
    total = 0
    for key in ('ink', 'sage', 'orange', 'paper'):
        left, right = _rgb(a[key]), _rgb(b[key])
        total += sum((left[i] - right[i]) ** 2 for i in range(3))
    return total ** 0.5


def suggest(topic, limit=5):
    text = topic.strip()
    if not text:
        raise ValueError('Theme cannot be empty')
    ranked = []
    for item in PALETTES:
        hits = [term for term in item['fits'] if term in text]
        ranked.append((sum(len(term) for term in hits), item['order'], item, hits))
    ranked.sort(key=lambda row: (-row[0], row[1]))
    if ranked[0][0] == 0:
        note = 'open'
        picked = [(resolve_palette('spring'), '主题里没有明显的场景或季节，春笺最稳妥')]
    else:
        note = 'matched'
        picked = []
        for score, _order, item, hits in ranked:
            if score <= 0 or len(picked) >= 3:
                break
            picked.append((_with_look(item), '主题里有「' + '、'.join(hits[:3]) + '」'))
    have = {item['id'] for item, _why in picked}
    if not have & {'night', 'cosmos'}:
        prefer = 'cosmos' if any(word in text for word in ('星', '宇宙', '银河', '太空')) else 'night'
        picked.append((resolve_palette(prefer), '深色备选，和浅色纸拉开差距'))
        have.add(prefer)
    rest = [_with_look(item) for item in PALETTES if item['id'] not in have]
    while len(picked) < limit and rest:
        nxt = max(rest, key=lambda item: min(_distance(item, chosen) for chosen, _why in picked))
        picked.append((nxt, '色相和前面几套差得更开'))
        rest = [item for item in rest if item['id'] != nxt['id']]
    choices = []
    for index, (item, because) in enumerate(picked[:limit]):
        row = _with_look(item)
        row['recommended'] = index == 0
        row['because'] = because
        choices.append(row)
    return {'topic': text, 'note': note, 'choices': choices}


def _hexa(value, alpha):
    r, g, b = _rgb(value)
    return f'#{r:02X}{g:02X}{b:02X}{max(0, min(255, int(round(alpha * 255)))):02X}'


def chrome_css(palette, paper):
    """Extra :root block. Empty for the hand-tuned spring chrome."""
    merged = dict(palette)
    merged['paper'] = paper
    if is_spring_colors(merged):
        return ''
    ink, sage, orange = palette['ink'], palette['sage'], palette['orange']
    rose, sky, light = palette['rose'], palette['sky'], palette['light']
    dark = rel_luminance(paper) < 0.4
    if dark:
        page = mix(paper, '#000000', 0.35)
        bar = mix(paper, ink, 0.08)
        rail = mix(paper, ink, 0.16)
        muted = mix(ink, sage, 0.35)
        dock = mix(paper, ink, 0.1)
        hover = mix(paper, sage, 0.24)
        selected = mix(paper, sage, 0.32)
        hair = _hexa(ink, 0.2)
        shadow = _hexa('#000000', 0.35)
        dock_shadow = _hexa('#000000', 0.45)
    else:
        page = mix(paper, ink, 0.05)
        bar = mix(paper, '#FFFFFF', 0.45)
        rail = mix(paper, ink, 0.08)
        muted = mix(ink, sage, 0.42)
        dock = mix(paper, '#FFFFFF', 0.5)
        hover = mix(sage, paper, 0.78)
        selected = mix(sage, paper, 0.66)
        hair = _hexa(ink, 0.14)
        shadow = _hexa(ink, 0.08)
        dock_shadow = _hexa(ink, 0.18)
    variables = {
        '--paper': paper,
        '--ink': ink,
        '--sage': sage,
        '--orange': orange,
        '--rose': rose,
        '--sky': sky,
        '--light': light,
        '--page': page,
        '--bar': bar,
        '--rail': rail,
        '--tint': mix(paper, light, 0.55),
        '--muted': muted,
        '--muted-2': mix(muted, paper, 0.35),
        '--kicker': mix(sage, ink, 0.35),
        '--line': mix(sage, paper, 0.28),
        '--edge': rail,
        '--footer': muted,
        '--dock': dock,
        '--dock-border': mix(sage, paper, 0.4),
        '--dock-ink': mix(ink, sage, 0.25),
        '--dot': orange,
        '--seek': sage,
        '--btn': mix(ink, sage, 0.3),
        '--hover': hover,
        '--selected': selected,
        '--selected-ink': ink,
        '--hair': hair,
        '--shadow': shadow,
        '--dock-shadow': dock_shadow,
    }
    body = ';'.join(f'{key}:{value}' for key, value in variables.items())
    return f':root{{{body}}}'


def gif_slots(token='spring'):
    """10 indexed GIF colors. Slot 0 is the transparent key, matching make_decor_gif."""
    spec = resolve_palette(token)
    if spec['id'] == 'spring':
        return [(0, 0, 0), (55, 87, 99), (152, 185, 159), (214, 142, 92), (240, 197, 182),
                (229, 237, 234), (211, 168, 130), (246, 219, 195), (177, 197, 187), (251, 250, 244)]
    colors = [
        (0, 0, 0),
        _rgb(spec['ink']),
        _rgb(spec['sage']),
        _rgb(spec['orange']),
        _rgb(spec['rose']),
        _rgb(spec['sky']),
        _rgb(mix(spec['orange'], spec['ink'], 0.22)),
        _rgb(mix(spec['rose'], spec['paper'], 0.4)),
        _rgb(mix(spec['sage'], spec['sky'], 0.4)),
        _rgb(spec['paper']),
    ]
    return colors


def _format_choice(index, item):
    mark = ' · 推荐' if item['recommended'] else ''
    swatch = ' '.join(f"{label} {item[key]}" for label, key in (('纸', 'paper'), ('线', 'ink'), ('辅色', 'sage'), ('点缀', 'orange')))
    look = f"动作 {item.get('motion', 'calm')} · {item.get('finish', '')}"
    return f"{index}. {item['name']} {item['id']}{mark}\n   {item['mood']}\n   依据：{item['because']}\n   {look}\n   {swatch}"


def main():
    parser = argparse.ArgumentParser(description='列出或推荐 SVG 长卷配色')
    parser.add_argument('--suggest', metavar='THEME', help='按主题给出 5 套可选项，第 1 套是推荐')
    parser.add_argument('--list', action='store_true', help='列出全部色板')
    parser.add_argument('--json', action='store_true', help='用 JSON 输出')
    args = parser.parse_args()
    if args.suggest:
        result = suggest(args.suggest)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return
        print(f"主题「{result['topic']}」")
        if result['note'] == 'open':
            print('没有明显场景色。第 1 套是稳妥推荐，后面几套差别更大。')
        else:
            print('第 1 套最贴这个主题。')
        print()
        for index, item in enumerate(result['choices'], start=1):
            print(_format_choice(index, item))
            print()
        return
    rows = [resolve_palette(item['id']) for item in PALETTES]
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return
    if not args.list:
        parser.error('pass --suggest THEME or --list')
    for item in rows:
        print(f"{item['name']} ({item['id']}) · {item['mood']}")
        print(f"  纸 {item['paper']}  线 {item['ink']}  辅色 {item['sage']}  点缀 {item['orange']}")


if __name__ == '__main__':
    main()
