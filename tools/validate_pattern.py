#!/usr/bin/env python3
"""Exercise CPU gate state and real GLES 2 rendering; no Pi performance claims."""
import json
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image
from gles import Renderer, GL

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts'


def main():
    OUT.mkdir(exist_ok=True)
    binary = OUT / 'cv_matrix_test'
    subprocess.run(['c++', '-std=c++11', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-fsanitize=undefined', '-fno-sanitize-recover=all',
                    '-I', str(ROOT / 'host'), str(ROOT / 'tests/cv_matrix_test.cpp'),
                    '-o', str(binary)], check=True)
    frames = [list(map(int, line.split())) for line in
              subprocess.check_output([str(binary)], text=True).splitlines()]
    assert len(frames) == 9
    assert frames[1] == frames[2] and frames[1] != frames[4]
    tested = 0
    previews = []
    for width, height in [(320, 240), (720, 576), (720, 480)]:
        renderer = Renderer(width, height)
        try:
            renderer.load(ROOT / 'Shaders/pt01_cv_matrix.frag')
            location = GL.glGetUniformLocation(renderer.program, 'u_cv_matrix_rows')
            assert location >= 0
            # Stock host / no uniform: safely black, never a fake time-based gate.
            renderer.draw()
            assert not renderer.pixels().any()
            # Every individual cell checks top-to-bottom row mapping and empty cells.
            single_cells = [[(1 << (i % 4)) if r == i // 4 else 0 for r in range(4)]
                            for i in range(16)]
            for index, masks in enumerate(frames + single_cells + [[15]*4]):
                GL.glUniform4f(location, *masks)
                renderer.draw(seconds=index * 1300, knobs=(0, .5, 1))
                pixels = np.flipud(renderer.pixels())
                assert np.array_equal(pixels[:, :, 0], pixels[:, :, 1])
                assert np.array_equal(pixels[:, :, 0], pixels[:, :, 2])
                for row in range(4):
                    for col in range(4):
                        cell = pixels[row*height//4:(row+1)*height//4,
                                      col*width//4:(col+1)*width//4, 0]
                        enabled = (masks[row] >> col) & 1
                        if enabled:
                            assert cell[cell.shape[0]//2, cell.shape[1]//2] == 255
                            assert 0.05 < np.mean(cell > 0) < .45
                        else:
                            assert not cell.any(), (masks, row, col)
                if width == 320 and index < len(frames):
                    previews.append(Image.fromarray(pixels))
                if index == len(frames) + 16:
                    Image.fromarray(pixels).save(OUT / f'geometry-{width}x{height}.png')
                tested += 1
                # Exact same mask at a different time and knob position: no flicker.
                renderer.draw(seconds=index * 2300 + 500, knobs=(1, 0, .2))
                assert np.array_equal(pixels, np.flipud(renderer.pixels()))
            info = renderer.info
        finally:
            renderer.close()
    previews[0].save(OUT / 'cv-sequence.gif', save_all=True,
                     append_images=previews[1:], duration=650, loop=0)
    report = {'cpu': '100 seeds, 30000 rising edges, hold/fall/union/reset: passed',
              'gles_cases': tested, 'resolutions': ['320x240', '720x576', '720x480'],
              'renderer': info, 'raspberry_pi_fps_temperature': 'not measured'}
    (OUT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
