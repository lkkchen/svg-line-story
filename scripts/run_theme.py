#!/usr/bin/env python3
"""One-shot offline V1-style starter generator. AI-Agent should creatively refine story.json after this."""
import argparse, json
from pathlib import Path
from plan_story import plan
from compile_story import build
from validate_story import validate

def main():
    p=argparse.ArgumentParser(description='One theme -> a 3-chapter SVG scroll starter (offline template). The agent can keep writing.')
    p.add_argument('theme',help='For example: a letter by the sea')
    p.add_argument('--palette',help='Palette id or English name, for example sea / Sea salt. Omit to keep Spring.')
    p.add_argument('--arc',help='Arc id or English name, for example timeline / Timeline. Omit to suggest one from the theme.')
    p.add_argument('--output','-o',default='work/generated',help='Output directory. Default: work/generated')
    a=p.parse_args(); dest=Path(a.output)
    dest.mkdir(parents=True,exist_ok=True)
    content=plan(a.theme, palette=a.palette, arc=a.arc)
    input_json=dest/'story.json'
    input_json.write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    errors,warnings,report=validate(content)
    if errors:raise ValueError('\n'.join(errors))
    build(input_json,dest/'dist')
    print('\nNext for an AI Agent: expand the story beats and add customMotifs for unique protagonists.')
    print('Open:',(dest/'dist/index.html').resolve())

if __name__=='__main__':main()
