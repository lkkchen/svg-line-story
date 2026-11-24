#!/usr/bin/env python3
"""Named line-art palettes for SVG Story Director.

Role names stay stable across every set: ink is the line and type color,
sage is the second fill, orange is the accent, rose is the soft third fill,
sky and light are pale washes. paper is the page. Changing a set recolors
the scroll; it does not change the drawing grammar.

Usage:
  python3 scripts/palettes.py --suggest 'a letter by the sea'
  python3 scripts/palettes.py --list
"""
from __future__ import annotations
import argparse, copy, json, re

ROLES = ('ink', 'sage', 'orange', 'rose', 'sky', 'light')

# Look package beyond the six role colors. motion is the energy of entrances,
# finish is how fills are rationed, typeStyle is the headline voice.
LOOK = {
    'spring': {'motion': 'calm', 'typeStyle': 'serif titles, loose tracking', 'finish': 'plenty of paper, warm color only in small blocks'},
    'sea': {'motion': 'calm', 'typeStyle': 'serif titles, loose tracking', 'finish': 'pale color like water, few large flat fills'},
    'forest': {'motion': 'calm', 'typeStyle': 'serif titles, loose tracking', 'finish': 'leaves use the second fill, accent only for fruit or light'},
    'dusk': {'motion': 'calm', 'typeStyle': 'serif titles, loose tracking', 'finish': 'little bright color on a lilac ground'},
    'lantern': {'motion': 'punchy', 'typeStyle': 'heavier serif titles, tighter labels', 'finish': 'accent only on lamps and seals, short entrances'},
    'snow': {'motion': 'calm', 'typeStyle': 'serif titles, loose tracking', 'finish': 'wide paper, persimmon red only once'},
    'ink': {'motion': 'calm', 'typeStyle': 'serif titles, even looser tracking', 'finish': 'almost no fill except one seal red'},
    'night': {'motion': 'calm', 'typeStyle': 'serif titles, loose tracking', 'finish': 'warm-white lines on a dark ground, even less fill'},
    'citrus': {'motion': 'punchy', 'typeStyle': 'heavier serif titles, tighter labels', 'finish': 'the second fill can be more saturated, pops are quicker'},
    'blossom': {'motion': 'calm', 'typeStyle': 'serif titles, loose tracking', 'finish': 'pink only for flowers and dots, leaves stay the second fill'},
    'cafe': {'motion': 'calm', 'typeStyle': 'serif titles, loose tracking', 'finish': 'brown lines, caramel only on a cup rim or a glint'},
    'cosmos': {'motion': 'calm', 'typeStyle': 'serif titles, loose tracking', 'finish': 'dark ground, stars use the accent'},
}


def term_in(text, term):
    if re.search(r'[A-Za-z]', term):
        return re.search(r'(?<![A-Za-z])' + re.escape(term) + r'(?![A-Za-z])', text, re.I) is not None
    return term in text

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
        'id': 'spring', 'order': 0, 'name': 'Spring', 'surface': 'light',
        'mood': 'cream paper, ink-blue line, sage green and warm apricot',
        'fits': ['spring', 'seed', 'bloom', 'garden', 'field', 'sprout'],
        **{k: SPRING[k] for k in ('paper', *ROLES)},
    },
    {
        'id': 'sea', 'order': 1, 'name': 'Sea salt', 'surface': 'light',
        'mood': 'shallow-sea paper, deep teal line, kelp green and sand gold',
        'fits': ['sea', 'ocean', 'beach', 'lighthouse', 'shell', 'boat', 'island', 'wave', 'harbor', 'tide'],
        'paper': '#F3F7F6', 'ink': '#163E4C', 'sage': '#2F7C78',
        'orange': '#D08948', 'rose': '#F0C4B0', 'sky': '#D5E8E5', 'light': '#E5F0ED',
    },
    {
        'id': 'forest', 'order': 2, 'name': 'Woods', 'surface': 'light',
        'mood': 'leaf paper, pine-soot line, moss green and clay orange',
        'fits': ['forest', 'woods', 'leaf', 'leaves', 'tree', 'trees', 'moss', 'mushroom'],
        'paper': '#F3F0E4', 'ink': '#1E3326', 'sage': '#4F7346',
        'orange': '#C4622E', 'rose': '#E2BC94', 'sky': '#D9E3CE', 'light': '#E7EDDC',
    },
    {
        'id': 'dusk', 'order': 3, 'name': 'Dusk', 'surface': 'light',
        'mood': 'lilac paper, dusk-purple line, olive second fill and plum pink',
        'fits': ['dusk', 'twilight', 'lavender', 'memory', 'purple'],
        'paper': '#F6F1F7', 'ink': '#332C4E', 'sage': '#6E7F62',
        'orange': '#C67B62', 'rose': '#E4B8CC', 'sky': '#E6DCEC', 'light': '#EFE6F1',
    },
    {
        'id': 'lantern', 'order': 4, 'name': 'Lanterns', 'surface': 'light',
        'mood': 'warm paper, cinnabar-brown line, bronze second fill and true-red accent',
        'fits': ['lantern', 'lanterns', 'new year', 'festival', 'reunion'],
        'paper': '#FBF3EA', 'ink': '#5C241F', 'sage': '#7A6244',
        'orange': '#E24B32', 'rose': '#F0B39A', 'sky': '#F4E0D0', 'light': '#F7EADF',
    },
    {
        'id': 'snow', 'order': 5, 'name': 'First snow', 'surface': 'light',
        'mood': 'snow paper, slate-blue line, frost blue and persimmon red',
        'fits': ['snow', 'winter', 'ice', 'frost', 'cold'],
        'paper': '#F5F8FB', 'ink': '#2C3E52', 'sage': '#6E8EA3',
        'orange': '#E06A4F', 'rose': '#E4D0CB', 'sky': '#E2EDF5', 'light': '#EEF3F7',
    },
    {
        'id': 'ink', 'order': 6, 'name': 'Ink', 'surface': 'light',
        'mood': 'rice paper, dense ink line, pale ink second fill and one seal red',
        'fits': ['ink', 'calligraphy', 'brush painting', 'rice paper', 'landscape'],
        'paper': '#F6F3EC', 'ink': '#242422', 'sage': '#7A756C',
        'orange': '#C4312A', 'rose': '#E3D5C8', 'sky': '#EBE6DE', 'light': '#F0EBE4',
    },
    {
        'id': 'night', 'order': 7, 'name': 'Night voyage', 'surface': 'dark',
        'mood': 'night paper, warm-white line, moon-teal second fill and amber accent',
        'fits': ['night', 'midnight', 'after dark', 'night voyage'],
        'paper': '#17202C', 'ink': '#F3E7D0', 'sage': '#7EAF9E',
        'orange': '#E3A45A', 'rose': '#D9A898', 'sky': '#243246', 'light': '#1E2A3A',
    },
    {
        'id': 'citrus', 'order': 8, 'name': 'Citrus', 'surface': 'light',
        'mood': 'warm-white paper, olive line, bright leaf green and citrus orange',
        'fits': ['summer', 'sunlight', 'lemon', 'orange', 'citrus', 'fruit'],
        'paper': '#FFF8EE', 'ink': '#2E3A22', 'sage': '#6E9A32',
        'orange': '#F0841E', 'rose': '#F6C896', 'sky': '#F6E6C4', 'light': '#FBF3DE',
    },
    {
        'id': 'blossom', 'order': 9, 'name': 'Blossom', 'surface': 'light',
        'mood': 'pale blossom paper, plum-brown line, young leaf green and cherry pink',
        'fits': ['cherry', 'blossom', 'peach blossom', 'love', 'pink'],
        'paper': '#FFF6F6', 'ink': '#5A3140', 'sage': '#8EAA8C',
        'orange': '#E06B86', 'rose': '#F6C2C8', 'sky': '#F8E4E6', 'light': '#FDEEEE',
    },
    {
        'id': 'cafe', 'order': 10, 'name': 'Cafe', 'surface': 'light',
        'mood': 'coffee paper, deep brown line, olive second fill and caramel',
        'fits': ['coffee', 'cafe', 'bookstore', 'reading', 'bread', 'tea'],
        'paper': '#F6EFE6', 'ink': '#3A291F', 'sage': '#6F7D52',
        'orange': '#C47A3A', 'rose': '#E4C2A4', 'sky': '#EFE2D2', 'light': '#F4EBDF',
    },
    {
        'id': 'cosmos', 'order': 11, 'name': 'Star sea', 'surface': 'dark',
        'mood': 'night-sky paper, starlight-white line, vine purple and star gold',
        'fits': ['star', 'stars', 'cosmos', 'galaxy', 'space', 'rocket', 'night sky'],
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
        hits = [term for term in item['fits'] if term_in(text, term)]
        ranked.append((sum(len(term) for term in hits), item['order'], item, hits))
    ranked.sort(key=lambda row: (-row[0], row[1]))
    if ranked[0][0] == 0:
        note = 'open'
        picked = [(resolve_palette('spring'), 'The theme has no clear place or season, so Spring is the steady choice')]
    else:
        note = 'matched'
        picked = []
        for score, _order, item, hits in ranked:
            if score <= 0 or len(picked) >= 3:
                break
            picked.append((_with_look(item), 'The theme contains ' + ', '.join(hits[:3])))
    have = {item['id'] for item, _why in picked}
    if not have & {'night', 'cosmos'}:
        prefer = 'cosmos' if any(term_in(text, word) for word in ('star', 'stars', 'cosmos', 'galaxy', 'space')) else 'night'
        picked.append((resolve_palette(prefer), 'A dark alternative, set apart from the light papers'))
        have.add(prefer)
    rest = [_with_look(item) for item in PALETTES if item['id'] not in have]
    while len(picked) < limit and rest:
        nxt = max(rest, key=lambda item: min(_distance(item, chosen) for chosen, _why in picked))
        picked.append((nxt, 'Its hue sits farther from the sets above'))
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
    mark = ' · recommended' if item['recommended'] else ''
    swatch = ' '.join(f"{label} {item[key]}" for label, key in (('paper', 'paper'), ('line', 'ink'), ('second', 'sage'), ('accent', 'orange')))
    look = f"motion {item.get('motion', 'calm')} · {item.get('finish', '')}"
    return f"{index}. {item['name']} {item['id']}{mark}\n   {item['mood']}\n   Why: {item['because']}\n   {look}\n   {swatch}"


def main():
    parser = argparse.ArgumentParser(description='List or suggest SVG scroll palettes')
    parser.add_argument('--suggest', metavar='THEME', help='Offer 5 palettes for a theme. The first is the recommendation.')
    parser.add_argument('--list', action='store_true', help='List every palette')
    parser.add_argument('--json', action='store_true', help='Print JSON')
    args = parser.parse_args()
    if args.suggest:
        result = suggest(args.suggest)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return
        print(f"Theme: {result['topic']}")
        if result['note'] == 'open':
            print('No obvious scene color. The first set is the steady recommendation. The later sets sit farther away.')
        else:
            print('The first set fits this theme most closely.')
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
        print(f"  paper {item['paper']}  line {item['ink']}  second {item['sage']}  accent {item['orange']}")


if __name__ == '__main__':
    main()
