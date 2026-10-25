#!/usr/bin/env python3
"""Build a deterministic release ZIP; no generated files enter the shader menu."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def build():
    manifest = json.loads((ROOT/'manifest.json').read_text())
    files = sorted([*ROOT.glob('Fx/*.frag'), *ROOT.glob('docs/*'),
                    ROOT/'README.md', ROOT/'manifest.json', ROOT/'tools/pi_health.py'])
    assert len(list(ROOT.glob('Fx/*.frag'))) == 11
    out = ROOT/'dist'
    out.mkdir(exist_ok=True)
    archive = out / ('recurboy-feedback-v' + manifest['version'] + '.zip')
    sums = []
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path in files:
            name = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            sums.append(hashlib.sha256(data).hexdigest() + '  ' + name)
            info = zipfile.ZipInfo(name, date_time=(2026,1,1,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, data)
        z.writestr(zipfile.ZipInfo('SHA256SUMS', date_time=(2026,1,1,0,0,0)), '\n'.join(sums)+'\n')
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (out/'SHA256SUMS').write_text(digest + '  ' + archive.name + '\n')
    print(archive)
    print(digest)
    return archive

if __name__ == '__main__':
    build()
