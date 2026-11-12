"""Local editorial contracts; no network or repository-level dependencies."""
import hashlib
import copy
import json
import math
import re
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
STYLE_IDS = ('tech-magazine', 'swiss-rational', 'data-journalism',
             'modern-minimal', 'illustrated-narrative')


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'duplicate JSON key: {key}')
            result[key] = value
        return result

    def invalid(value):
        raise ValueError(f'non-finite JSON number: {value}')
    return json.loads(Path(path).read_text(encoding='utf-8'),
                      object_pairs_hook=unique, parse_constant=invalid)


def validate(value, schema, path='$'):
    """Validate the JSON Schema subset used by the two bundled contracts."""
    if 'anyOf' in schema:
        for candidate in schema['anyOf']:
            try:
                validate(value, candidate, path)
                return
            except ValueError:
                pass
        raise ValueError(f'{path}: does not match any allowed form')
    if 'enum' in schema and not any(type(value) is type(item) and value == item for item in schema['enum']):
        raise ValueError(f'{path}: unknown value {value!r}')
    kind = schema.get('type')
    types = {'object': dict, 'array': list, 'string': str, 'integer': int,
             'number': (int, float), 'boolean': bool, 'null': type(None)}
    if kind and (not isinstance(value, types[kind]) or
                 kind in ('integer', 'number') and isinstance(value, bool)):
        raise ValueError(f'{path}: expected {kind}')
    if isinstance(value, dict):
        props = schema.get('properties', {})
        missing = set(schema.get('required', [])) - value.keys()
        unknown = value.keys() - props.keys()
        if missing or unknown and schema.get('additionalProperties') is False:
            raise ValueError(f'{path}: missing={sorted(missing)}, unknown={sorted(unknown)}')
        for key, child in value.items():
            if key in props:
                validate(child, props[key], f'{path}.{key}')
    elif isinstance(value, list):
        if len(value) < schema.get('minItems', 0):
            raise ValueError(f'{path}: too few items')
        for i, child in enumerate(value):
            validate(child, schema.get('items', {}), f'{path}[{i}]')
    elif isinstance(value, str):
        if len(value.strip()) < schema.get('minLength', 0):
            raise ValueError(f'{path}: empty text')
        if 'pattern' in schema and not re.search(schema['pattern'], value):
            raise ValueError(f'{path}: invalid format')
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        if not math.isfinite(value) or value < schema.get('minimum', -math.inf) or value > schema.get('maximum', math.inf):
            raise ValueError(f'{path}: number outside permitted range')


def request_defaults(request):
    validate(request, read_json(ASSETS / 'request.schema.json'))
    if 'audience' not in request:
        raise ValueError('resolve audience from user/context before producing request JSON')
    result = dict(audience='ceo', purpose='understand', visual_style='auto',
                  preview='auto', formats=['html', 'png', 'markdown'], locale='zh-CN',
                  density='comfortable', brand=None, source_scope='supplied-only')
    result.update(request)
    if isinstance(result['visual_style'], dict) and result['audience'] != 'both':
        raise ValueError('per-audience visual_style requires audience=both')
    canvas = dict(css_width=400, export_scale=2.7, split_policy='semantic',
                  max_export_pixels=24_000_000, target_channel_limits={})
    canvas.update(result.get('canvas', {}))
    result['canvas'] = canvas
    return result


def resolve_request(request):
    """Map snake_case request to plan settings, never invent editorial content."""
    req = request_defaults(request)
    modes = ['ceo', 'cto'] if req['audience'] == 'both' else [req['audience']]
    plans = []
    for audience in modes:
        chosen = req['visual_style']
        if isinstance(chosen, dict):
            chosen = chosen[audience]
        style = 'tech-magazine' if chosen == 'auto' else chosen
        preview = req['preview']
        if preview == 'auto' and chosen != 'auto':
            preview = 'skip'
        limits = req['canvas']['target_channel_limits']
        plans.append(dict(
            audience=audience, styleId=style, styleVersion='1.0',
            purpose=req['purpose'], outputs=req['formats'], locale=req['locale'],
            density=req['density'], brand=req['brand'],
            canvas=dict(cssWidth=req['canvas']['css_width'], scale=req['canvas']['export_scale'],
                        splitPolicy=req['canvas']['split_policy'],
                        maxExportPixels=req['canvas']['max_export_pixels'],
                        targetChannelLimits={
                            {'max_width_px': 'maxWidthPx', 'max_height_px': 'maxHeightPx',
                             'max_total_pixels': 'maxTotalPixels'}[k]: v for k, v in limits.items()}),
            selection=dict(reason='default recommendation' if chosen == 'auto' else 'explicit style',
                           preview=preview, confirmed=False)))
    return plans


def index(items, label):
    result = {item['id']: item for item in items}
    if len(result) != len(items):
        raise ValueError(f'duplicate {label} IDs')
    return result


def content_hash(plan):
    payload = copy.deepcopy({k: plan.get(k) for k in ('audience', 'purpose', 'locale', 'contentVersion',
                                                    'mainClaim', 'facts', 'blocks', 'diagrams', 'charts')})
    # Storage location is not content; Renderer adds the actual source image bytes.
    for block in payload.get('blocks') or []:
        if 'image' in block:
            block['image'].pop('path', None)
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def luminance(color):
    rgb = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return sum(w * (v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4)
               for v, w in zip(rgb, (.2126, .7152, .0722)))


def contrast(first, second):
    a, b = sorted((luminance(first), luminance(second)))
    return (b + .05) / (a + .05)


def load_style(plan):
    style = read_json(ASSETS / 'styles' / f'{plan["styleId"]}.json')
    if style['version'] != plan['styleVersion']:
        raise ValueError('styleVersion does not match installed style')
    brand = plan.get('brand') or {}
    style['colors'].update(brand.get('colors', {}))
    style['fonts'] = brand.get('fonts', {})
    checks = {}
    for fg in ('text', 'muted', 'accent'):
        for bg in ('background', 'surface'):
            ratio = contrast(style['colors'][fg], style['colors'][bg])
            checks[f'{fg}/{bg}'] = round(ratio, 2)
            if ratio < 4.5:
                raise ValueError(f'contrast {fg}/{bg}={ratio:.2f} < 4.5; choose a readable brand variant')
    for series in style['chartSeries']:
        if min(contrast(series, style['colors'][bg]) for bg in ('background', 'surface')) < 3:
            raise ValueError('chart boundary contrast < 3')
    return style, checks


def validate_plan(plan):
    validate(plan, read_json(ASSETS / 'plan.schema.json'))
    facts = index(plan['facts'], 'fact')
    diagrams = index(plan.get('diagrams', []), 'diagram')
    charts = index(plan.get('charts', []), 'chart')
    index(plan['blocks'], 'block')

    def refs(ids):
        if set(ids) - facts.keys():
            raise ValueError(f'unresolved claimIds: {set(ids) - facts.keys()}')

    refs(plan['mainClaim']['claimIds'])
    main_ids = set(plan['mainClaim']['claimIds'])
    for diagram in diagrams.values():
        nodes = index(diagram['nodes'], 'node')
        occupied = set()
        if len(nodes) > 20:
            raise ValueError('split diagrams with more than 20 nodes')
        for node in nodes.values():
            refs(node['claimIds'])
            cell = (node['row'], node['column'])
            if cell in occupied or node['row'] > 20:
                raise ValueError('overlapping or excessive diagram rows')
            occupied.add(cell)
        for edge in diagram['edges']:
            refs(edge['claimIds'])
            if edge['from'] not in nodes or edge['to'] not in nodes or edge['from'] == edge['to']:
                raise ValueError('invalid diagram edge')
    for chart in charts.values():
        units = set()
        for point in chart['points']:
            refs([point['claimId']])
            fact = facts[point['claimId']]
            quantity = fact.get('quantity')
            if not quantity or fact['kind'] != 'fact' or quantity['value'] < 0:
                raise ValueError('bar charts require sourced, non-negative factual quantities')
            units.add(quantity['unit'])
        if len(units) != 1:
            raise ValueError('chart quantities must have the same unit')
    for block in plan['blocks']:
        refs(block['claimIds'])
        ids = set(block['claimIds'])
        if block['role'] == 'decision' and plan['purpose'] != 'decision_brief':
            raise ValueError('decision blocks require purpose=decision_brief')
        if sum(key in block for key in ('diagramId', 'chartId', 'scene', 'image')) > 1:
            raise ValueError('one primary visual per block; split the block')
        for key, collection in (('diagramId', diagrams), ('chartId', charts)):
            if key in block:
                if block[key] not in collection:
                    raise ValueError(f'unresolved {key}')
                item = collection[block[key]]
                if key == 'diagramId':
                    for node in item['nodes'] + item['edges']:
                        ids.update(node['claimIds'])
                else:
                    ids.update(p['claimId'] for p in item['points'])
        if 'scene' in block:
            refs(block['scene']['claimIds'])
            ids.update(block['scene']['claimIds'])
        if not block.get('appendix'):
            main_ids.update(ids)
    absent = [f['id'] for f in facts.values() if f.get('required') and f['id'] not in main_ids]
    if absent:
        raise ValueError(f'required facts absent from main reading path: {absent}')
    style, checks = load_style(plan)
    return facts, diagrams, charts, style, checks


def split_ranges(units, max_height):
    """Pack whole semantic units; never cut a figure or its conditions."""
    groups = []
    for top, bottom in units:
        if bottom - top > max_height:
            raise ValueError('a semantic block exceeds export limits; edit/split that block first')
        if groups and bottom - groups[-1][0] <= max_height:
            groups[-1] = (groups[-1][0], bottom)
        else:
            groups.append((top, bottom))
    return groups
