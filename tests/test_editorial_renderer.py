import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import struct
import sys
import tempfile
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/writing/team-writing-polish'
SCRIPT = SKILL / 'scripts/render.py'
FIXTURE = ROOT / 'tests/fixtures/editorial/plan.json'
spec = importlib.util.spec_from_file_location('editorial_contracts', SKILL / 'scripts/contracts.py')
contracts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contracts)


class EditorialTests(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads(FIXTURE.read_text())

    def cli(self, plan, *arguments):
        with tempfile.TemporaryDirectory() as work:
            path = Path(work) / 'plan.json'
            path.write_text(json.dumps(plan))
            return subprocess.run([sys.executable, str(SCRIPT), '--plan', str(path), *arguments],
                                  capture_output=True, text=True)

    def test_all_profiles_have_readable_colors_and_preserve_content_identity(self):
        identity = contracts.content_hash(self.plan)
        for style in contracts.STYLE_IDS:
            self.plan['styleId'] = style
            *_, profile, ratios = contracts.validate_plan(self.plan)
            self.assertEqual(profile['id'], style)
            self.assertGreaterEqual(min(ratios.values()), 4.5)
            self.assertEqual(contracts.content_hash(self.plan), identity)
        self.plan['blocks'][0]['paragraphs'][0] += ' 内容已变。'
        self.assertNotEqual(contracts.content_hash(self.plan), identity)

    def test_request_mapping_and_unknown_enum_rejection(self):
        plans = contracts.resolve_request({'sources': ['source.md'], 'audience': 'both',
                                           'visual_style': {'ceo': 'modern-minimal', 'cto': 'swiss-rational'}})
        self.assertEqual([p['audience'] for p in plans], ['ceo', 'cto'])
        self.assertEqual([p['styleId'] for p in plans], ['modern-minimal', 'swiss-rational'])
        self.assertEqual(plans[0]['canvas']['scale'], 2.7)
        self.assertEqual(plans[0]['selection']['preview'], 'skip')
        default = contracts.resolve_request({'sources': ['source.md'], 'audience': 'ceo'})[0]
        self.assertEqual(default['styleId'], 'tech-magazine')
        self.assertEqual(default['selection']['preview'], 'auto')
        with self.assertRaises(ValueError):
            contracts.resolve_request({'sources': ['source.md'], 'visual_style': 'swiss'})
        with self.assertRaises(ValueError):
            contracts.resolve_request({'sources': ['source.md'], 'canvas': {'scale': 2}})
        self.plan['audience'] = 'both'
        with self.assertRaises(ValueError):
            contracts.validate_plan(self.plan)

    def test_unsourced_chart_values_and_required_fact_hiding_are_rejected(self):
        self.plan['charts'][0]['points'][0]['value'] = 999
        with self.assertRaises(ValueError):
            contracts.validate_plan(self.plan)
        self.plan = json.loads(FIXTURE.read_text())
        self.plan['charts'][0]['points'][0]['claimId'] = 'c4'
        with self.assertRaises(ValueError):
            contracts.validate_plan(self.plan)
        self.plan = json.loads(FIXTURE.read_text())
        self.plan['blocks'][1]['appendix'] = True
        with self.assertRaisesRegex(ValueError, 'required facts'):
            contracts.validate_plan(self.plan)

    def test_low_contrast_brand_and_unresolved_edges_are_rejected(self):
        self.plan['brand'] = {'colors': {'text': '#F6F4EE'}}
        with self.assertRaisesRegex(ValueError, 'contrast'):
            contracts.validate_plan(self.plan)
        self.plan['brand'] = None
        self.plan['diagrams'][0]['edges'][0]['to'] = 'absent'
        with self.assertRaisesRegex(ValueError, 'edge'):
            contracts.validate_plan(self.plan)

    def test_semantic_split_keeps_whole_units(self):
        units = [(0, 240), (240, 650), (650, 900), (900, 1200)]
        self.assertEqual(contracts.split_ranges(units, 700), [(0, 650), (650, 1200)])
        with self.assertRaisesRegex(ValueError, 'semantic block'):
            contracts.split_ranges(units, 300)

    def test_preview_gate_and_explicit_skip(self):
        self.plan['selection'].update(preview='auto', confirmed=False)
        result = self.cli(self.plan)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('confirmation pending', result.stderr)
        self.assertEqual(self.cli(self.plan, '--preview').returncode, 0)
        self.plan['selection']['confirmed'] = True
        self.assertEqual(self.cli(self.plan).returncode, 0)

    def test_dry_run_writes_nothing_and_existing_outputs_are_protected(self):
        with tempfile.TemporaryDirectory() as work:
            out = Path(work) / 'output'
            result = self.cli(self.plan, '--output', str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(out.exists())
            out.mkdir()
            (out / 'keep.txt').write_text('existing')
            result = self.cli(self.plan, '--output', str(out), '--apply')
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((out / 'keep.txt').read_text(), 'existing')

    def test_offline_html_and_markdown_share_facts_and_assets(self):
        self.plan['outputs'] = ['html', 'markdown']
        self.plan['blocks'][0]['paragraphs'].append('<script>alert(1)</script>')
        with tempfile.TemporaryDirectory() as work:
            out = Path(work) / 'output'
            result = self.cli(self.plan, '--output', str(out), '--apply')
            self.assertEqual(result.returncode, 0, result.stderr)
            page = (out / 'index.html').read_text()
            self.assertIn('&lt;script&gt;', page)
            self.assertNotIn('<script>', page)
            self.assertNotIn('<script>', (out / 'editorial.md').read_text())
            self.assertIn('Content-Security-Policy', page)
            self.assertIn('推广判断仍有两个缺口', (out / 'editorial.md').read_text())
            self.assertTrue((out / 'assets/mechanism-evidence-path.svg').is_file())
            report = json.loads((out / 'qa-report.json').read_text())
            self.assertIn(report['contentSHA256'], page)
            self.assertTrue(report['manualChecks'])

    def test_no_illustration_is_required_and_repeated_diagrams_have_unique_ids(self):
        self.plan['outputs'] = ['html']
        self.plan['styleId'] = 'data-journalism'
        for block in self.plan['blocks']:
            for key in ('scene', 'diagramId', 'chartId'):
                block.pop(key, None)
        with tempfile.TemporaryDirectory() as work:
            out = Path(work) / 'plain'
            result = self.cli(self.plan, '--output', str(out), '--apply')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn('<figure', (out / 'index.html').read_text())
        self.plan = json.loads(FIXTURE.read_text())
        self.plan['outputs'] = ['html']
        repeat = copy.deepcopy(self.plan['blocks'][2])
        repeat['id'] = 'repeat'
        self.plan['blocks'].append(repeat)
        with tempfile.TemporaryDirectory() as work:
            out = Path(work) / 'repeated'
            result = self.cli(self.plan, '--output', str(out), '--apply')
            self.assertEqual(result.returncode, 0, result.stderr)
            from html.parser import HTMLParser
            class IDs(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.ids = []
                def handle_starttag(self, tag, attrs):
                    self.ids.extend(v for k,v in attrs if k=='id')
            parser = IDs()
            parser.feed((out / 'index.html').read_text())
            self.assertEqual(len(parser.ids), len(set(parser.ids)))

    def test_missing_browser_is_honest_partial_delivery(self):
        with tempfile.TemporaryDirectory() as work:
            out = Path(work) / 'output'
            result = self.cli(self.plan, '--output', str(out), '--apply', '--browser', '/no/such/browser')
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertTrue((out / 'index.html').exists())
            self.assertTrue((out / 'editorial.md').exists())
            self.assertFalse((out / 'longform.png').exists())
            report = json.loads((out / 'qa-report.json').read_text())
            self.assertEqual(report['browser']['status'], 'incomplete')

    def test_external_or_escaping_image_paths_rejected_without_fetch(self):
        block = self.plan['blocks'][0]
        block.pop('scene')
        block['image'] = dict(path='https://example.invalid/image.png', alt='原图',
                              caption='原始材料', identity='evidence', source='source.md')
        result = self.cli(self.plan)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('local file', result.stderr)

    def test_packaged_images_are_reproducible_and_content_changes_are_detected(self):
        def png(color):
            def chunk(kind, value):
                data = kind + value
                return struct.pack('>I', len(value)) + data + struct.pack('>I', zlib.crc32(data))
            return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(b'\x00' + color)) + chunk(b'IEND', b'')
        self.plan['outputs'] = ['html', 'markdown']
        block = self.plan['blocks'][0]
        block.pop('scene')
        block['image'] = dict(path='original.png', alt='合成像素', caption='测试素材', identity='explanation', source='fixture')
        with tempfile.TemporaryDirectory() as work:
            base = Path(work)
            source = base / 'original.png'
            source.write_bytes(png(b'\x00\x00\x00'))
            plan = base / 'plan.json'
            plan.write_text(json.dumps(self.plan))
            def run(input_path, destination):
                result = subprocess.run([sys.executable, str(SCRIPT), '--plan', str(input_path),
                                         '--output', str(destination), '--apply'], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                return json.loads((destination / 'qa-report.json').read_text())['contentSHA256']
            first = run(plan, base / 'first')
            saved = json.loads((base / 'first/design-plan.json').read_text())
            packaged = base / 'first' / saved['blocks'][0]['image']['path']
            self.assertEqual(packaged.read_bytes(), source.read_bytes())
            self.assertEqual(first, run(base / 'first/design-plan.json', base / 'replay'))
            source.write_bytes(png(b'\xff\xff\xff'))
            self.assertNotEqual(first, run(plan, base / 'changed'))


if __name__ == '__main__':
    unittest.main()
