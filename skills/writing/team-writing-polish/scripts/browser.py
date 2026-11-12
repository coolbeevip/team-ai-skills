"""Optional local Chrome PNG export; needs an existing websocket-client install."""
import base64
import json
import math
import shutil
import struct
import subprocess
import tempfile
import time
import urllib.request
import zlib
from pathlib import Path

from contracts import split_ranges


def png_size(data):
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('export is not PNG')
    cursor, size, image_data, end = 8, None, False, False
    while cursor + 12 <= len(data):
        length = struct.unpack('>I', data[cursor:cursor + 4])[0]
        chunk = data[cursor + 4:cursor + 8 + length]
        crc = data[cursor + 8 + length:cursor + 12 + length]
        if len(crc) != 4 or zlib.crc32(chunk) != struct.unpack('>I', crc)[0]:
            raise ValueError('PNG chunk integrity failed')
        if chunk[:4] == b'IHDR':
            size = struct.unpack('>II', chunk[4:12])
        if chunk[:4] == b'IDAT' and length:
            image_data = True
        if chunk[:4] == b'IEND':
            end = True
            break
        cursor += length + 12
    if not size or not image_data or not end:
        raise ValueError('incomplete PNG')
    return size


def executable(requested):
    candidates = [requested] if requested else [shutil.which('google-chrome'), shutil.which('chromium'),
        shutil.which('chromium-browser'), '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(Path(candidate).resolve())
    raise ValueError('local Chrome/Chromium unavailable; HTML is usable, PNG not generated')


class CDP:
    def __init__(self, socket):
        self.socket, self.sequence, self.requests = socket, 0, []

    def send(self, method, params=None):
        self.sequence += 1
        current = self.sequence
        self.socket.send(json.dumps(dict(id=current, method=method, params=params or {})))
        while True:
            response = json.loads(self.socket.recv())
            if response.get('method') == 'Network.requestWillBeSent':
                self.requests.append(response['params']['request']['url'])
            if response.get('id') == current:
                if 'error' in response:
                    raise RuntimeError(str(response['error']))
                return response.get('result', {})

    def evaluate(self, expression):
        result = self.send('Runtime.evaluate', dict(expression=expression, awaitPromise=True, returnByValue=True))
        if 'exceptionDetails' in result:
            raise RuntimeError(str(result['exceptionDetails']))
        return result['result'].get('value')


METRICS = r'''(() => {
 const main=document.querySelector('main');
 const all=[...document.querySelectorAll('body *')];
 const overflow=all.filter(e=> {const b=e.getBoundingClientRect();
   return b.width>0 && (b.left < -1 || b.right>innerWidth+1);}).map(e=>e.id||e.tagName);
 const labelErrors=[];
 for(const t of document.querySelectorAll('svg text')) {
   const svg=t.ownerSVGElement, b=t.getBBox(), v=svg.viewBox.baseVal;
   const scale=t.getScreenCTM().a;
   if(b.x < v.x-1 || b.y < v.y-1 || b.x+b.width>v.width+1 || b.y+b.height>v.height+1)
     labelErrors.push('clipped SVG label: '+t.textContent);
   if(parseFloat(getComputedStyle(t).fontSize)*scale<14)
     labelErrors.push('small SVG label: '+t.textContent);
 }
 const missingImages=[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.alt);
 const tiny=[...document.querySelectorAll('p,figcaption,.chart-label,.chart-axis')].filter(e=>
   parseFloat(getComputedStyle(e).fontSize)<13).map(e=>e.tagName);
 const rect=main.getBoundingClientRect();
 const children=[...main.children];
 const unitTops=children.filter(e=>e.classList.contains('unit')).map(e=>e.getBoundingClientRect().top+scrollY);
 return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,overflow,labelErrors,missingImages,tiny,
   fontStatus:document.fonts.status,mainHeight:Math.ceil(rect.bottom+scrollY),
   unitTops,outlineBottom:Math.ceil((document.querySelector('.preview-outline')||main).getBoundingClientRect().bottom+scrollY),
   heroBottom:Math.ceil(document.querySelector('header').getBoundingClientRect().bottom+scrollY)};
})()'''


def export(html, output, plan, preview=False, browser=None):
    try:
        import websocket
    except ImportError as exc:
        raise ImportError('websocket-client is not installed for this Python; PNG not generated, no dependency was installed') from exc
    binary = executable(browser)
    with tempfile.TemporaryDirectory(prefix='editorial-chrome-') as work:
        profile = Path(work) / 'profile'
        with (Path(work) / 'chrome.log').open('w') as log:
            process = subprocess.Popen([binary, '--headless=new', '--disable-gpu', '--no-first-run',
                '--no-default-browser-check', '--disable-background-networking', '--disable-extensions',
                '--remote-debugging-port=0', f'--user-data-dir={profile}', 'about:blank'], stdout=log, stderr=log)
            socket = None
            try:
                deadline = time.monotonic() + 20
                while not (profile / 'DevToolsActivePort').exists():
                    if process.poll() is not None or time.monotonic() > deadline:
                        raise RuntimeError('Chrome startup failed or timed out')
                    time.sleep(.1)
                port = (profile / 'DevToolsActivePort').read_text().splitlines()[0]
                opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
                targets = json.load(opener.open(f'http://127.0.0.1:{port}/json', timeout=10))
                target = next(t for t in targets if t['type'] == 'page')
                socket = websocket.create_connection(target['webSocketDebuggerUrl'], suppress_origin=True, timeout=20)
                cdp = CDP(socket)
                for domain in ('Page', 'Network', 'DOM', 'CSS'):
                    cdp.send(domain + '.enable')
                cdp.send('Network.setBlockedURLs', {'urls': ['http://*', 'https://*']})
                version = cdp.send('Browser.getVersion')
                measurements = []
                for width in sorted({360, 400, 430, plan['canvas']['cssWidth']}):
                    cdp.send('Emulation.setDeviceMetricsOverride', dict(width=width, height=844, deviceScaleFactor=1, mobile=True))
                    cdp.send('Page.navigate', {'url': html.as_uri()})
                    deadline = time.monotonic() + 15
                    while not cdp.evaluate('document.readyState === "complete" && !!document.querySelector("main")'):
                        if time.monotonic() > deadline:
                            raise RuntimeError('page load timed out')
                        time.sleep(.05)
                    cdp.evaluate('Promise.all([document.fonts.ready,...[...document.images].map(i=>i.decode())]).then(()=>true)')
                    metrics = cdp.evaluate(METRICS)
                    if any(metrics[k] for k in ('overflow', 'labelErrors', 'missingImages', 'tiny')) or metrics['fontStatus'] != 'loaded':
                        raise ValueError('layout/font/image gate failed: ' + json.dumps(metrics, ensure_ascii=False))
                    doc = cdp.send('DOM.getDocument')['root']['nodeId']
                    fonts = {}
                    for selector in ('h1', '.body-copy p', '.deck'):
                        node = cdp.send('DOM.querySelector', {'nodeId': doc, 'selector': selector})['nodeId']
                        if node:
                            fonts[selector] = cdp.send('CSS.getPlatformFontsForNode', {'nodeId': node})['fonts']
                    all_fonts = [f for items in fonts.values() for f in items]
                    if not all_fonts or any('lastresort' in f['familyName'].lower() for f in all_fonts):
                        raise ValueError('actual font unavailable or missing-glyph fallback detected')
                    brand_fonts = (plan.get('brand') or {}).get('fonts', {})
                    for role, actual in (('heading', fonts.get('h1', [])),
                                         ('body', fonts.get('.body-copy p') or fonts.get('.deck', []))):
                        if role in brand_fonts and not any(f['familyName'].lower() == brand_fonts[role].lower() for f in actual):
                            raise ValueError(f'brand font {role} did not load; choose an available licensed font')
                    metrics['actualFonts'] = fonts
                    measurements.append(metrics)
                width, scale = plan['canvas']['cssWidth'], plan['canvas']['scale']
                cdp.send('Emulation.setDeviceMetricsOverride', dict(width=width, height=844, deviceScaleFactor=scale, mobile=True))
                cdp.evaluate('document.fonts.ready.then(()=>true)')
                metrics = cdp.evaluate(METRICS)
                limits = plan['canvas'].get('targetChannelLimits', {})
                pixels = min(plan['canvas'].get('maxExportPixels', 24_000_000), limits.get('maxTotalPixels', math.inf))
                out_width = math.ceil(width * scale)
                if out_width > limits.get('maxWidthPx', 16384):
                    raise ValueError('export width exceeds channel limit; choose a permitted canvas/scale')
                max_height = math.floor(min(limits.get('maxHeightPx', 32760) / scale,
                                            pixels / out_width / scale))

                def capture(name, top, bottom):
                    height = bottom - top
                    if height <= 0 or height > max_height:
                        raise ValueError('capture exceeds pixel budget; use semantic segments')
                    shot = cdp.send('Page.captureScreenshot', {'format': 'png', 'captureBeyondViewport': True,
                        'clip': dict(x=0, y=top, width=width, height=height, scale=1)})
                    data = base64.b64decode(shot['data'], validate=True)
                    size = png_size(data)
                    if abs(size[0] - width * scale) > 1 or abs(size[1] - height * scale) > 1:
                        raise ValueError('PNG dimensions differ from requested canvas')
                    if size[0] > limits.get('maxWidthPx', 16384) or size[1] > limits.get('maxHeightPx', 32760) or size[0] * size[1] > pixels:
                        raise ValueError('actual PNG dimensions exceed export limits')
                    (output / name).write_bytes(data)
                    return dict(file=name, top=top, bottom=bottom, pixels=size)

                captures = []
                if preview:
                    captures.append(capture('cover-preview.png', 0, metrics['heroBottom']))
                    # Use the actual outline, not appendix/source-map screenshot.
                    if metrics['outlineBottom'] <= max_height:
                        captures.append(capture('layout-preview.png', 0, metrics['outlineBottom']))
                    else:
                        raise ValueError('preview exceeds limits; shorten outline or use a larger permitted preview budget')
                else:
                    tops = [0] + [math.floor(t) for t in metrics['unitTops'][1:]]
                    ends = tops[1:] + [metrics['mainHeight']]
                    groups = split_ranges(list(zip(tops, ends)), max_height)
                    for i, (top, bottom) in enumerate(groups, 1):
                        filename = 'longform.png' if len(groups) == 1 else f'part-{i:02}.png'
                        captures.append(capture(filename, top, bottom))
                external = [url for url in cdp.requests if url.startswith(('http://', 'https://'))]
                if external:
                    raise ValueError('page attempted external requests')
                return dict(status='automatic-checks-passed', environment=version, viewports=measurements,
                            fontVersion='not exposed by CDP; actual family/PostScript names recorded',
                            captures=captures, externalRequests=external,
                            splitReminder=metrics['mainHeight'] > 844 * 4,
                            manualReview='required: actual glyphs, hierarchy, figures and all split boundaries')
            finally:
                if socket:
                    socket.close()
                process.terminate()
                try:
                    process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
