#!/usr/bin/env python3
"""Render isolated, synthetic five-style examples with the installed local browser."""
import argparse
import copy
import html
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
STYLES = [('tech-magazine','科技杂志'), ('swiss-rational','瑞士理性主义'),
          ('data-journalism','数据新闻'), ('modern-minimal','现代极简'),
          ('illustrated-narrative','插画叙事')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='new directory; defaults to a temporary directory')
    parser.add_argument('--only', choices=[s[0] for s in STYLES], help='one profile for debugging')
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='editorial-styles-'))
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        parser.error('output must be empty')
    skill = out / 'isolated-skill'
    shutil.copytree(ROOT / 'skills/writing/team-writing-polish', skill,
                    ignore=shutil.ignore_patterns('__pycache__'))
    def hashes():
        return {str(p.relative_to(skill)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in skill.rglob('*') if p.is_file()}
    before = hashes()
    source = out / 'input'
    shutil.copytree(ROOT / 'tests/fixtures/editorial', source)
    original = json.loads((source / 'plan.json').read_text())
    results = []
    for style, name in STYLES:
        if args.only and style != args.only:
            continue
        for audience in ('ceo', 'cto'):
            plan = copy.deepcopy(original)
            plan['styleId'], plan['audience'] = style, audience
            if audience == 'cto':
                plan['purpose'] = 'technical_review'
                plan['mainClaim'].update(text='已有测试改善，泛化尚未验证',
                                         deck='先区分评测范围，再判断独立验证缺口。')
                order = ['mechanism', 'comparison', 'new-tasks', 'boundary']
                plan['blocks'] = [copy.deepcopy(next(b for b in original['blocks'] if b['id'] == key)) for key in order]
                plan['blocks'][0]['paragraphs'] = ['当前20个任务已经参与优化。相同模型、权限和成功规则使前后结果可以在该范围内比较，但不能代替独立样本上的评测。', '未做独立盲测是证据缺口，不是过拟合已经发生的证据。']
            path = source / f'{audience}-{style}.json'
            path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
            destination = out / audience / style
            command = [sys.executable, str(skill / 'scripts/render.py'), '--plan', str(path),
                       '--output', str(destination), '--apply']
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError(f'{audience}/{style}: {result.stdout}\n{result.stderr}')
            qa = json.loads((destination / 'qa-report.json').read_text())
            results.append(dict(audience=audience,style=style,contentSHA256=qa['contentSHA256'],browser=qa['browser']))
            if audience == 'ceo':
                preview = out / 'previews' / style
                result = subprocess.run(command[:-2] + [str(preview), '--apply', '--preview'], capture_output=True, text=True)
                if result.returncode:
                    raise RuntimeError(f'preview {style}: {result.stdout}\n{result.stderr}')
            print(f'{audience}/{style}: rendered', flush=True)
    for audience in ('ceo', 'cto'):
        assert len({r['contentSHA256'] for r in results if r['audience']==audience}) == 1
    assert hashes() == before, 'runtime changed the isolated skill installation'
    (out / 'skill-hashes.json').write_text(json.dumps(before, ensure_ascii=False, indent=2)+'\n')
    sections = []
    for style,name in STYLES:
        if args.only and style != args.only:
            continue
        sections.append(f'<section><h2>{html.escape(name)}</h2><img src="previews/{style}/cover-preview.png" alt="{html.escape(name)}首屏预览"><p><a href="previews/{style}/layout-preview.html">首屏与骨架</a> · <a href="ceo/{style}/index.html">观点版全文</a> · <a href="cto/{style}/index.html">机制版全文</a></p></section>')
    gallery = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>五种编辑风格对照</title><style>
body{margin:0;padding:32px;background:#f6f4ee;color:#202521;font:17px/1.65 system-ui}h1{font-size:32px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:32px}section{min-width:0}img{width:100%;height:auto;border:1px solid #59615b}a{color:#28584a}a:focus-visible{outline:3px solid #28584a;outline-offset:4px}</style><h1>同一材料，五种编辑表达</h1><p>合成测试数据，不代表真实收益。各风格使用同一内容版本；图像为实际浏览器导出。以下名称只用于选择预览，不写入成品。</p><main>'''
    (out / 'index.html').write_text(gallery + ''.join(sections) + '</main></html>')
    (out / 'checks.json').write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n')
    print(out, flush=True)


if __name__ == '__main__':
    main()
