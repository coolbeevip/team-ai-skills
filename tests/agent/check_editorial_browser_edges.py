#!/usr/bin/env python3
"""Exercise real PNG splitting, missing-font fallback and oversized semantic units."""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='editorial-browser-edges-'))
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        parser.error('output must be empty')
    original = json.loads((ROOT / 'tests/fixtures/editorial/plan.json').read_text())
    reports = []
    cases = [('split', 0), ('explicit-split', 0), ('missing-font', 2), ('oversize', 2)]
    for name, code in cases:
        plan = copy.deepcopy(original)
        if name == 'split':
            plan['canvas']['targetChannelLimits'] = {'maxWidthPx': 1080, 'maxHeightPx': 3000}
            appendix = copy.deepcopy(plan['blocks'][-1])
            appendix.update(id='appendix', title='不应进入图片的附录', appendix=True)
            plan['blocks'].append(appendix)
        if name == 'missing-font':
            plan['brand'] = {'fonts': {'heading': 'Missing Editorial Font 123456'}}
        if name == 'explicit-split':
            plan['blocks'][2]['breakBefore'] = True
        if name == 'oversize':
            plan['canvas']['targetChannelLimits'] = {'maxHeightPx': 900}
        path = out / (name + '.json')
        path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
        destination = out / name
        result = subprocess.run([sys.executable, str(ROOT / 'skills/writing/team-writing-polish/scripts/render.py'),
                                 '--plan', str(path), '--output', str(destination), '--apply'], capture_output=True, text=True)
        assert result.returncode == code, (name, result.stdout, result.stderr)
        qa = json.loads((destination / 'qa-report.json').read_text())
        if name in ('split', 'explicit-split'):
            captures = qa['browser']['captures']
            assert len(captures) > 1 and not (destination / 'longform.png').exists()
            assert captures[0]['top'] == 0
            assert all(c['pixels'][0] == 1080 for c in captures)
            if name == 'split':
                assert all(c['pixels'][1] <= 3000 for c in captures)
            assert all(a['bottom'] == b['top'] for a,b in zip(captures,captures[1:]))
            metrics = next(m for m in qa['browser']['viewports'] if m['width']==400)['imageLayout']
            assert captures[-1]['bottom'] == metrics['mainHeight']
            boundaries = {int(y) for y in metrics['unitTops']}
            assert all(c['top'] in boundaries for c in captures[1:])
            if name == 'explicit-split':
                assert len(captures) == 2 and captures[1]['top'] == metrics['breakTops'][0]
        else:
            assert qa['browser']['status'] == 'incomplete'
            assert (destination / 'index.html').exists() and (destination / 'editorial.md').exists()
            assert not list(destination.glob('*.png'))
        reports.append(dict(case=name,result='passed',report=qa))
        print(name + ': passed', flush=True)
    (out / 'checks.json').write_text(json.dumps(reports, ensure_ascii=False, indent=2) + '\n')
    print(out)


if __name__ == '__main__':
    main()
