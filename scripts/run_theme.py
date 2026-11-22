#!/usr/bin/env python3
"""One-shot offline V1-style starter generator. AI-Agent should creatively refine story.json after this."""
import argparse, json
from pathlib import Path
from plan_story import plan
from compile_story import build
from validate_story import validate

def main():
    p=argparse.ArgumentParser(description='一行主题 -> 3幕 SVG 长卷起始成品（离线模版）；Agent可继续自由创作。')
    p.add_argument('theme',help='例如：海边的一封信')
    p.add_argument('--palette',help='色板 id 或中文名，例如 sea / 海盐。省略则沿用春笺')
    p.add_argument('--arc',help='叙事弧 id 或中文名，例如 timeline / 时间线。省略则按主题推荐')
    p.add_argument('--output','-o',default='work/generated',help='输出项目目录，默认 work/generated')
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
