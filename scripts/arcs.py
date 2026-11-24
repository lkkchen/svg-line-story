#!/usr/bin/env python3
"""Narrative arcs for a three-chapter line scroll.

These are story skeletons, not visual styles. Ads arcs that end on a call to
action are intentionally absent: the scroll stays a line that arrives somewhere.
Usage:
  python3 scripts/arcs.py --suggest 'how a city changes'
"""
from __future__ import annotations
import argparse, copy, json, re

ARCS = [
    {
        'id': 'three_act', 'order': 0, 'name': 'Three acts',
        'line': 'One line completes a change, and the ending returns to the opening object or feeling',
        'fits': [],
        'roles': ['Cause', 'Turn', 'Echo'],
        'emphasis': ['sage', 'orange', 'ink'],
        'motions': ['draw', 'pop', 'still'],
    },
    {
        'id': 'timeline', 'order': 1, 'name': 'Timeline',
        'line': 'One line means time moving forward, never jumping back',
        'fits': ['history', 'changes', 'origin', 'evolution', 'lifetime', 'the past', 'the future', 'growing up'],
        'roles': ['Start', 'Passing through', 'This moment'],
        'emphasis': ['ink', 'sage', 'orange'],
        'motions': ['draw', 'sway', 'still'],
    },
    {
        'id': 'man_in_hole', 'order': 2, 'name': 'Fall and climb',
        'line': 'The line sinks first, then rises higher than where it began',
        'fits': ['failure', 'loss', 'lost', 'trouble', 'again', 'return', 'recovery', 'low point', 'fall'],
        'roles': ['Steady', 'The fall', 'Climbing out'],
        'emphasis': ['sage', 'ink', 'orange'],
        'motions': ['sway', 'draw', 'pop'],
    },
    {
        'id': 'myth_buster', 'order': 3, 'name': 'Myth busting',
        'line': 'The line first passes through something that looks true, then turns toward the real cause',
        'fits': ['myth', 'actually', 'truth', 'rumor', 'everyone thinks'],
        'roles': ['What people think', 'Not so', 'Therefore'],
        'emphasis': ['rose', 'ink', 'orange'],
        'motions': ['still', 'draw', 'pop'],
    },
    {
        'id': 'how_it_works', 'order': 4, 'name': 'How it works',
        'line': 'The line passes through the steps in real order, without showing the ending first',
        'fits': ['how', 'why it works', 'principle', 'steps', 'method', 'making'],
        'roles': ['First sight', 'The middle step', 'So this is why'],
        'emphasis': ['orange', 'sage', 'ink'],
        'motions': ['pop', 'draw', 'still'],
    },
    {
        'id': 'story_spine', 'order': 5, 'name': 'Story spine',
        'line': 'The line leaves a repeated day once, then returns to a day that has changed',
        'fits': ['every day', 'until', 'once upon', 'from then on', 'suddenly', 'one day'],
        'roles': ['Every day', 'Until one day', 'From then on'],
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


def term_in(text, term):
    if re.search(r'[A-Za-z]', term):
        return re.search(r'(?<![A-Za-z])' + re.escape(term) + r'(?![A-Za-z])', text, re.I) is not None
    return term in text


def _score(text, spec):
    hits = [term for term in spec['fits'] if term_in(text, term)]
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
        because = 'The theme has no more specific skeleton, so use three acts'
    else:
        best = copy.deepcopy(ranked[0][2])
        because = 'The theme contains ' + ', '.join(ranked[0][3][:3])
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
    parser = argparse.ArgumentParser(description='Suggest a narrative arc for a scroll from a theme')
    parser.add_argument('--suggest', metavar='THEME')
    parser.add_argument('--motion', choices=['calm', 'punchy'], default='calm', help='Motion amount from the chosen palette')
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    if args.suggest:
        result = suggest_arc(args.suggest, args.motion)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return
        arc = result['arc']
        print(f"Theme: {result['topic']}")
        print(f"Arc: {arc['name']} {arc['id']} · recommended")
        print(f"Why: {arc['because']}")
        print(f"What the line means: {arc['line']}")
        print('Three chapters: ' + ' → '.join(arc['roles']))
        print('Hero colors: ' + ' → '.join(arc['emphasis']))
        print('Hero motions: ' + ' → '.join(arc['motions']))
        alt = result['alternate']
        print(f"Could also be: {alt['name']} {alt['id']} ({alt['line']})")
        return
    if not args.list:
        parser.error('pass --suggest THEME or --list')
    for spec in ARCS:
        print(f"{spec['name']} ({spec['id']}) · {spec['line']}")


if __name__ == '__main__':
    main()
