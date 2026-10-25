#!/usr/bin/env python3
"""Render every stock PATTERN with no textures and exercise all exposed controls."""
import itertools
import json
from pathlib import Path
import re
import time
import numpy as np
from PIL import Image, ImageDraw
from gles import Renderer

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts'

def delta(first, second):
    return float(np.abs(first.astype(float)-second.astype(float)).mean() / 255)

def check_budget(path):
    code = re.sub(r'//[^\n]*', '', path.read_text())
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.S)
    assert not re.search(r'\b(for|while|do|sampler2D|samplerCube)\b|\btexture\w*\s*\(', code), path
    assert not re.search(r'\b(pow|exp|log|log2|atan|tan)\s*\(', code), path
    transcendental = len(re.findall(r'\b(?:sin|cos)\s*\(', code))
    assert transcendental <= 3, (path, transcendental)
    assert path.stat().st_size < 5000
    return {'texture_reads':0, 'loops':0, 'sin_cos_calls':transcendental, 'bytes':path.stat().st_size}

def main():
    OUT.mkdir(exist_ok=True)
    spec = json.loads((ROOT/'manifest.json').read_text())
    paths = [(c, s, ROOT/'Shaders'/c['id']/s['file']) for c in spec['collections'] for s in c['shaders']]
    assert len(paths) == 46 and len(spec['collections']) == 5
    report = {'shader_count':len(paths), 'host':'stock PATTERN; zero input textures', 'cases':0,
              'hardware_fps_temperature':'not measured', 'shaders':{}}
    previews = {}
    failures = []
    for width, height in [(320,240), (720,576), (720,480)]:
        renderer = Renderer(width, height)
        try:
            for collection, shader, path in paths:
                try:
                    budget = check_budget(path)
                    renderer.load(path)
                    renderer.draw(seconds=2.3)
                    base = renderer.pixels()
                    assert base.std() > 8 and base.max() > 150, 'Blank or nearly flat default'
                    if width == 320:
                        previews[path.name] = Image.fromarray(base)
                    renderer.draw(seconds=2.3)
                    assert np.array_equal(base, renderer.pixels()), 'Pause is not stable'
                    report['cases'] += 2
                    effects = []
                    for knob in range(3):
                        low = [.5]*3; high = [.5]*3
                        low[knob] = 0; high[knob] = 1
                        renderer.draw(low, 2.3); first = renderer.pixels()
                        renderer.draw(high, 2.3); second = renderer.pixels()
                        difference = delta(first, second)
                        assert difference > .018, ('Weak knob response', knob+1, difference)
                        effects.append(round(difference,4))
                        report['cases'] += 2
                    for knobs in itertools.product([0,1], repeat=3):
                        renderer.draw(knobs, 2.3)
                        frame = renderer.pixels()
                        assert frame.std() > 3, ('Flat corner', knobs)
                        if knobs[2] == 0:
                            assert np.array_equal(frame[:,:,0], frame[:,:,1])
                            assert np.array_equal(frame[:,:,0], frame[:,:,2])
                        report['cases'] += 1
                    motion = []
                    for seconds in [-86400.3, -7.1, 0, 13.7, 86400.3]:
                        renderer.draw(seconds=seconds)
                        frame = renderer.pixels()
                        assert frame.std() > 3, ('Flat clock sample', seconds)
                        motion.append(delta(base, frame))
                        report['cases'] += 1
                    assert max(motion) > .025, 'Animation does not move'
                    if width == 320:
                        report['shaders'][path.name] = dict(budget, knob_delta=effects, motion_delta=round(max(motion),4))
                    if width == 720 and height == 576:
                        begin = time.perf_counter()
                        for frame in range(30): renderer.draw(seconds=frame/30)
                        renderer.pixels()
                        report['shaders'][path.name]['mesa_pal_ms_per_frame'] = round((time.perf_counter()-begin)*1000/30,3)
                    print(f'{width}x{height}: {path.name} OK', flush=True)
                except Exception as error:
                    failure = f'{width}x{height} {path.name}: {error}'
                    failures.append(failure)
                    print('FAIL: '+failure, flush=True)
            report['renderer'] = renderer.info
        finally:
            renderer.close()
    report['failures'] = failures
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    assert not failures, '\n'.join(failures)
    for collection in spec['collections']:
        thumbs = [previews[s['file']] for s in collection['shaders']]
        columns = 2
        sheet = Image.new('RGB',(columns*320, ((len(thumbs)+1)//2)*267),(12,12,16))
        draw = ImageDraw.Draw(sheet)
        for i,(thumb,s) in enumerate(zip(thumbs,collection['shaders'])):
            x,y = (i%columns)*320,(i//columns)*267
            sheet.paste(thumb,(x,y))
            draw.text((x+7,y+245),s['title'],fill=(235,235,235))
        sheet.save(OUT/(collection['id']+'.jpg'), quality=92)
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f"PASS: {len(paths)} shaders, {report['cases']} render cases; no Pi performance claim")

if __name__ == '__main__': main()
