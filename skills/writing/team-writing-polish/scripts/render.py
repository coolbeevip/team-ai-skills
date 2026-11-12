#!/usr/bin/env python3
"""Validate and render an editorial plan. Dry-run unless --apply is supplied."""
import argparse
import base64
import copy
import hashlib
import html
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

from contracts import ASSETS, content_hash, read_json, resolve_request, validate_plan


def esc(value):
    return html.escape(str(value), quote=True)


def md_text(value):
    # Plan strings are plain text, not executable HTML or remote Markdown images.
    return re.sub(r'([\\`*_{}\[\]()#+!|<>])', r'\\\1', str(value))


def lines(text, width):
    result, line, used = [], '', 0
    for char in text:
        size = .55 if ord(char) < 128 else 1
        if used + size > width and line:
            result.append(line)
            line, used = '', 0
        line += char
        used += size
    if line:
        result.append(line)
    return result


class Renderer:
    def __init__(self, plan, base):
        self.plan, self.base = plan, Path(base).resolve()
        self.facts, self.diagrams, self.charts, self.style, self.contrasts = validate_plan(plan)
        self.assets = {}
        self.hash = content_hash(plan)
        evidence_images = {}
        for block in plan['blocks']:
            if 'image' in block:
                name, _ = self.image(block['image']['path'])
                evidence_images[block['id']] = hashlib.sha256(self.assets[name]).hexdigest()
        if evidence_images:
            self.hash = hashlib.sha256(json.dumps([self.hash, evidence_images], sort_keys=True).encode()).hexdigest()

    def image(self, path):
        source = (self.base / path).resolve()
        if not source.is_relative_to(self.base) or not source.is_file():
            raise ValueError('image must be an existing local file inside the plan directory')
        data = source.read_bytes()
        if data.startswith(b'\x89PNG\r\n\x1a\n'):
            mime, suffix = 'image/png', '.png'
        elif data.startswith(b'\xff\xd8\xff'):
            mime, suffix = 'image/jpeg', '.jpg'
        elif data[:4] == b'RIFF' and data[8:12] == b'WEBP':
            mime, suffix = 'image/webp', '.webp'
        else:
            raise ValueError('source images must be PNG, JPEG or WebP; keep editable SVG in diagram data')
        name = 'assets/' + hashlib.sha256(data).hexdigest()[:20] + suffix
        self.assets[name] = data
        return name, 'data:' + mime + ';base64,' + base64.b64encode(data).decode()

    def ids(self, block):
        ids = list(block['claimIds'])
        if 'diagramId' in block:
            diagram = self.diagrams[block['diagramId']]
            for item in diagram['nodes'] + diagram['edges']:
                ids += item['claimIds']
        if 'chartId' in block:
            ids += [p['claimId'] for p in self.charts[block['chartId']]['points']]
        if 'scene' in block:
            ids += block['scene']['claimIds']
        return list(dict.fromkeys(ids))

    def conditions(self, ids):
        return list(dict.fromkeys(c for key in ids for c in self.facts[key]['conditions']))

    def citations(self, ids):
        return '<p class="citations">来源：' + ' · '.join(
            f'<a href="#source-{esc(key)}">{list(self.facts).index(key) + 1}</a>' for key in ids) + '</p>'

    def diagram(self, diagram, instance):
        cols = max(node['column'] for node in diagram['nodes']) + 1
        width = 320 if cols == 1 else 150
        wrapped = {n['id']: lines(n['label'], 15 if cols == 1 else 6) for n in diagram['nodes']}
        row_height = max(72, max(len(v) for v in wrapped.values()) * 24 + 26)
        pitch = row_height + 42
        height = (max(n['row'] for n in diagram['nodes']) + 1) * pitch
        positions = {n['id']: (174 if cols == 1 else 87 + 174 * n['column'],
                               12 + n['row'] * pitch) for n in diagram['nodes']}
        uid = esc('diagram-' + instance + '-' + diagram['id'])
        svg = f'<svg class="diagram" viewBox="0 0 348 {height}" role="img" aria-labelledby="{uid}-title {uid}-desc"><title id="{uid}-title">{esc(diagram["title"])}</title><desc id="{uid}-desc">{esc(diagram["description"])}</desc>'
        svg += f'<defs><marker id="{uid}-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1L7 4L1 7" fill="none" stroke="var(--text)" stroke-width="1.4"/></marker></defs>'
        for edge in diagram['edges']:
            x1, y1 = positions[edge['from']]
            x2, y2 = positions[edge['to']]
            if y2 > y1:
                middle = y1 + row_height + 20
                d = f'M{x1} {y1 + row_height} V{middle} H{x2} V{y2 - 5}'
            elif y1 == y2:
                direction = 1 if x2 > x1 else -1
                d = f'M{x1 + direction * width / 2} {y1 + row_height / 2} H{x2 - direction * (width / 2 + 5)}'
            else:
                d = f'M{x1 - width / 2} {y1 + row_height / 2} H3 V{y2 + row_height / 2} H{x2 - width / 2 - 5}'
            svg += f'<path class="edge" d="{d}" marker-end="url(#{uid}-arrow)"/>'
        for node in diagram['nodes']:
            x, y = positions[node['id']]
            state = ' pending' if node.get('state') == 'pending' else ''
            svg += f'<rect class="node{state}" x="{x-width/2}" y="{y}" width="{width}" height="{row_height}"/>'
            for i, line in enumerate(wrapped[node['id']]):
                svg += f'<text x="{x}" y="{y + 30 + i * 24}">{esc(line)}</text>'
        return svg + '</svg>'

    def visual(self, block):
        markdown = []
        if 'diagramId' in block:
            d = self.diagrams[block['diagramId']]
            body = self.diagram(d, block['id'])
            caption = d['description']
            name = f'assets/{block["id"]}-{d["id"]}.svg'
            # Standalone source includes its palette/font rules, not only CSS variables.
            standalone = body.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
            standalone = standalone.replace('><title', '><style>' + self.css() + '</style><title', 1)
            self.assets[name] = standalone.encode()
            markdown += [f'![{md_text(d["title"])}]({name})', md_text(caption)]
            markdown += [f'- {n["id"]}: {md_text(n["label"])}' for n in d['nodes']]
            markdown += [f'- {e["from"]} → {e["to"]}' for e in d['edges']]
        elif 'chartId' in block:
            chart = self.charts[block['chartId']]
            quantities = [self.facts[p['claimId']]['quantity'] for p in chart['points']]
            high = max(q['value'] for q in quantities) or 1
            body = f'<div class="chart" role="group" aria-label="{esc(chart["title"])}">'
            markdown += ['| 对象 | 数值 | 单位 |', '| --- | ---: | --- |']
            for point, quantity in zip(chart['points'], quantities):
                value, unit = quantity['value'], quantity['unit']
                body += f'<div class="chart-row"><div class="chart-label"><span>{esc(point["label"])}</span><strong>{esc(value)} {esc(unit)}</strong></div><div class="chart-track"><div class="chart-bar" style="width:{value/high*100:.6f}%"></div></div></div>'
                markdown.append(f'| {md_text(point["label"])} | {value} | {md_text(unit)} |')
            axis = f'量程 0–{high} {quantities[0]["unit"]}；零基线，同一比例'
            body += f'<p class="chart-axis">{esc(axis)}</p></div>'
            markdown.append(md_text(axis))
            caption = '；'.join(chart['conditions'])
            markdown += [md_text(caption)]
        elif 'scene' in block:
            scene = block['scene']
            body = '<svg class="scene" viewBox="0 0 348 196" role="img" aria-label="' + esc(scene['caption']) + '">'
            for i in (2, 1, 0):
                body += f'<rect class="object" x="{24+i*6}" y="{22+i*6}" width="130" height="80"/>'
            for i, line in enumerate(lines(scene['object'], 6)):
                body += f'<text x="89" y="{53+i*23}">{esc(line)}</text>'
            body += '<path class="link" d="M172 70 H194 M188 64 L194 70 L188 76"/>'
            pending = ' pending' if scene['status'] == 'pending' else ''
            body += f'<rect class="state{pending}" x="204" y="28" width="120" height="80"/>'
            for i, line in enumerate(lines(scene['state'], 5)):
                body += f'<text x="264" y="{60+i*23}">{esc(line)}</text>'
            body += '<text x="174" y="162">同一对象 · 不同证据状态</text></svg>'
            caption = '概念示意：' + scene['caption']
            markdown += [md_text(scene['object'] + ' → ' + scene['state']), md_text(caption)]
        elif 'image' in block:
            im = block['image']
            name, uri = self.image(im['path'])
            body = f'<img src="{uri}" alt="{esc(im["alt"])}">'
            identity = {'evidence': '原始证据', 'explanation': '编辑绘图', 'concept': '概念插画'}[im['identity']]
            caption = identity + '：' + im['caption'] + '；来源：' + im['source']
            markdown += [f'![{md_text(im["alt"])}]({name})', md_text(caption)]
        else:
            return '', []
        return '<figure class="visual">' + body + f'<figcaption>{esc(caption)}</figcaption></figure>', markdown

    def block(self, block, include_visual=True):
        ids = self.ids(block)
        conditions = self.conditions(ids)
        visual, visual_md = self.visual(block) if include_visual else ('', [])
        body = f'<section class="unit role-{esc(block["role"])}" id="block-{esc(block["id"])}" data-role="{esc(block["role"])}"><h2>{esc(block["title"])}</h2>'
        body += visual
        body += '<div class="body-copy">' + ''.join(f'<p>{esc(p)}</p>' for p in block['paragraphs']) + '</div>'
        if conditions:
            body += '<div class="conditions">' + ''.join(f'<p>{esc(c)}</p>' for c in conditions) + '</div>'
        body += self.citations(ids) + '</section>'
        md = ['## ' + md_text(block['title']), *visual_md, *map(md_text, block['paragraphs']), *map(md_text, conditions),
              '来源：' + ', '.join(ids)]
        return body, '\n\n'.join(md)

    def css(self):
        s = self.style
        serif = '"Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", serif'
        sans = '"Noto Sans CJK SC", "Source Han Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif'
        fonts = s['fonts']
        heading = f'"{fonts["heading"]}", ' if 'heading' in fonts else ''
        body = f'"{fonts["body"]}", ' if 'body' in fonts else ''
        heading += serif if s['headingFont'] == 'serif' else sans
        body += sans
        tokens = dict(s['colors'])
        tokens.update({'hero-size': f'{s["type"]["hero"]}px', 'section-size': f'{s["type"]["section"]}px',
                       'body-size': f'{s["type"]["body"]}px', 'body-line': s['type']['lineHeight'],
                       'heading-font': heading, 'body-font': body, 'section-space': '32px',
                       'canvas': f'{self.plan["canvas"]["cssWidth"]}px', 'series-0': s['chartSeries'][0]})
        return ':root{' + ';'.join(f'--{k}:{v}' for k, v in tokens.items()) + '}\n' + (ASSETS / 'templates/editorial.css').read_text()

    def sources(self):
        page, md = '<aside class="appendix" aria-label="来源映射"><h2>来源与条件</h2>', ['# 来源与条件']
        for key, fact in self.facts.items():
            source = fact['source']
            location = f'<a href="{esc(source)}">{esc(source)}</a>' if re.match(r'^https?://', source) else esc(source)
            kind = {'fact': '事实', 'judgment': '作者判断', 'recommendation': '建议', 'hypothesis': '待验证假设'}[fact['kind']]
            page += f'<section class="source-entry" id="source-{esc(key)}"><h3>来源 {list(self.facts).index(key) + 1}</h3><p>{esc(fact["text"])}</p><p>{kind} · {location}</p>'
            page += ''.join(f'<p>{esc(c)}</p>' for c in fact['conditions']) + '</section>'
            md += [f'## {key}', md_text(fact['text']), md_text(f'身份：{fact["kind"]}；来源：{source}'), *map(md_text, fact['conditions'])]
        return page + '</aside>', '\n\n'.join(md) + '\n'

    def build(self, preview=False):
        plan = self.plan
        blocks = [b for b in plan['blocks'] if not b.get('appendix')]
        appendices = [b for b in plan['blocks'] if b.get('appendix')]
        hero_role = self.style['heroRole']
        focus = next((b for b in blocks if b['role'] == hero_role and
                      any(k in b for k in ('diagramId', 'chartId', 'scene', 'image'))), None)
        body = '<main data-export="main">'
        hero = plan['mainClaim']
        body += '<header class="hero unit" data-role="hero-claim">'
        logo = (plan.get('brand') or {}).get('logo')
        if logo:
            _, uri = self.image(logo)
            body += f'<img class="brand-logo" src="{uri}" alt="项目标识">'
        if preview:
            body += '<p class="eyebrow">风格预览 · ' + esc(self.style['name']) + '</p>'
        body += '<h1>' + esc(hero['text']) + '</h1>'
        if hero.get('deck'):
            body += '<p class="deck">' + esc(hero['deck']) + '</p>'
        hero_ids = list(dict.fromkeys(hero['claimIds'] + (self.ids(focus) if focus else [])))
        for condition in self.conditions(hero_ids):
            body += '<p class="hero-condition">' + esc(condition) + '</p>'
        md = ['# ' + md_text(hero['text']), md_text(hero.get('deck', '')), *map(md_text, self.conditions(hero_ids))]
        if focus:
            visual, visual_md = self.visual(focus)
            body += visual
            md.extend(visual_md)
        body += self.citations(hero_ids) + '</header>'
        ordered = ([focus] if focus else []) + [b for b in blocks if b is not focus]
        if preview:
            # Same hero as the final article, plus a separately labelled outline.
            body += '</main><section class="preview-outline"><h2>全篇骨架</h2><p>这是版面预览，尚未导出最终长图。</p><ol>'
            for b in ordered:
                body += '<li' + (' class="focus"' if b is focus else '') + f'>{esc(b["title"])} · {esc(b["role"])}'
                if b['paragraphs']:
                    body += '<p>' + esc(b['paragraphs'][0]) + '</p>'
                body += '</li>'
            body += '</ol><p>附录：' + esc('、'.join(b['title'] for b in appendices) or '无正文附录') + '</p></section>'
        else:
            for b in ordered:
                rendered, text = self.block(b, include_visual=b is not focus)
                body += rendered
                md.append(text)
            body += '<nav class="appendix-nav"><a href="#editorial-appendix">来源与附录</a></nav></main>'
        body += '<div id="editorial-appendix">'
        if appendices:
            body += '<aside class="appendix"><h2>附录</h2>'
            md.append('# 附录')
            for b in appendices:
                rendered, text = self.block(b)
                body += rendered
                md.append(text)
            body += '</aside>'
        source_html, source_md = self.sources()
        body += source_html + '</div>'
        template = (ASSETS / 'templates/editorial.html').read_text()
        values = dict(LOCALE=esc(plan['locale']), HASH=self.hash, TITLE=esc(hero['text']), CSS=self.css(),
                      STYLE=esc(plan['styleId']), DENSITY=esc(plan['density']), BODY=body)
        document = re.sub(r'\{\{([A-Z]+)\}\}', lambda match: values[match[1]], template)
        return document, '\n\n'.join(p for p in md if p) + '\n', source_md


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', type=Path, help='validate request and print resolved plan settings')
    parser.add_argument('--plan', type=Path, help='validated editorial plan JSON')
    parser.add_argument('--output', type=Path, help='new output directory; existing nonempty paths are refused')
    parser.add_argument('--preview', action='store_true', help='render first focus and full outline, not final article')
    parser.add_argument('--apply', action='store_true', help='write output; otherwise validate and describe only')
    parser.add_argument('--browser', help='local Chrome/Chromium executable for PNG export')
    args = parser.parse_args()
    if args.request:
        if args.plan or args.apply:
            parser.error('--request is read-only and cannot be combined with --plan or --apply')
        print(json.dumps(resolve_request(read_json(args.request)), ensure_ascii=False, indent=2))
        return 0
    if not args.plan:
        parser.error('--plan or --request is required')
    plan = read_json(args.plan)
    renderer = Renderer(plan, args.plan.parent)
    selection = plan['selection']
    if not args.preview and selection['preview'] != 'skip' and not selection['confirmed']:
        raise ValueError('preview confirmation pending; use --preview or record explicit skip/confirmation')
    document, markdown, sources = renderer.build(args.preview)
    if not args.apply:
        print(json.dumps(dict(dryRun=True, contentSHA256=renderer.hash, style=plan['styleId'],
                              preview=args.preview, contrast=renderer.contrasts), ensure_ascii=False, indent=2))
        return 0
    if not args.output:
        parser.error('--apply requires --output')
    output = args.output.resolve()
    if output == args.plan.parent.resolve() or output.exists() and any(output.iterdir()):
        raise ValueError('choose a new empty output directory; source/old exports are never overwritten')
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.editorial-', dir=output.parent))
    report = dict(contentSHA256=renderer.hash, style=plan['styleId'], styleVersion=plan['styleVersion'],
                  preview=args.preview, contrast=renderer.contrasts, browser='not-run',
                  manualChecks=['source entailment and evidence strength', 'actual glyphs and pixel review',
                                'thumbnail hierarchy and semantic split boundaries', 'human comprehension not tested'])
    code = 0
    try:
        filename = 'layout-preview.html' if args.preview else 'index.html'
        # HTML is the reproducible render source for PNG, even for PNG-only requests.
        if 'html' in plan['outputs'] or 'png' in plan['outputs'] or args.preview:
            (stage / filename).write_text(document, encoding='utf-8')
        if 'markdown' in plan['outputs'] and not args.preview:
            (stage / 'editorial.md').write_text(markdown, encoding='utf-8')
        (stage / 'sources.md').write_text(sources, encoding='utf-8')
        saved_plan = copy.deepcopy(plan)
        for block in saved_plan['blocks']:
            if 'image' in block:
                block['image']['path'] = renderer.image(block['image']['path'])[0]
        if (saved_plan.get('brand') or {}).get('logo'):
            saved_plan['brand']['logo'] = renderer.image(saved_plan['brand']['logo'])[0]
        (stage / 'design-plan.json').write_text(json.dumps(saved_plan, ensure_ascii=False, indent=2) + '\n')
        for name, data in renderer.assets.items():
            path = stage / name
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(data)
        if 'png' in plan['outputs']:
            try:
                from browser import export
                report['browser'] = export(stage / filename, stage, plan, args.preview, args.browser)
            except Exception as error:
                report['browser'] = dict(status='incomplete', reason=str(error))
                code = 2
        report['files'] = {str(p.relative_to(stage)): hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in stage.rglob('*') if p.is_file()}
        (stage / 'qa-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        (stage / 'qa-report.md').write_text('# 制作检查\n\n'
            f'- 内容版本：{plan["contentVersion"]}\n- 内容 SHA-256：{renderer.hash}\n'
            f'- 风格：{plan["styleId"]} / {plan["styleVersion"]}\n'
            f'- 自动检查：{"有未完成项" if code else "已执行所请求格式的检查"}；详见 qa-report.json。\n'
            '- 尚未完成：来源语义保真复核、字体缺字与实际图片查看、缩略图层级和分段边界人工复核。\n'
            '- 未做真人理解或读屏设备测试。自动检查通过不等于全部硬门禁通过。\n', encoding='utf-8')
        if output.exists():
            output.rmdir()  # Only the already-checked empty destination.
        stage.rename(output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    print(json.dumps(dict(output=str(output), status='partial' if code else 'rendered-awaiting-review',
                          contentSHA256=renderer.hash), ensure_ascii=False))
    return code


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        sys.exit(1)
