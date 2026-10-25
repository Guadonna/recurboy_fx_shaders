#!/usr/bin/env python3
"""Bundle collection ZIP contents in separate collection directories."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def build(archives, output, version):
    entries = {}
    collections = []
    for path in archives:
        with zipfile.ZipFile(path) as z:
            manifest = json.loads(z.read('manifest.json'))
            name = manifest['collection']
            assert name not in [c['collection'] for c in collections]
            assert name and all(c.isalnum() or c in "_-" for c in name)
            collections.append(dict(manifest, directory=name))
            for line in z.read('SHA256SUMS').decode().splitlines():
                digest, item = line.split('  ', 1)
                assert hashlib.sha256(z.read(item)).hexdigest() == digest
            for item in z.namelist():
                assert not Path(item).is_absolute() and '..' not in Path(item).parts
                target = f'{name}/{item}'
                assert target not in entries, f'Duplicate file: {target}'
                entries[target] = z.read(item)
    collections.sort(key=lambda c: c['collection'])
    shaders = {p for p in entries if p.endswith('.frag')}
    declared = [c['directory']+'/'+e['file'] for c in collections for e in c['effects']]
    assert len(declared) == len(set(declared)) and set(declared) == shaders
    entries['manifest.json'] = (json.dumps({'version': version, 'collections': collections}, ensure_ascii=False, indent=2)+'\n').encode()
    entries['README.md'] = (f'# RecurBoy FX Collections {version}\n\n'
        f'Все {len(shaders)} шейдеров разделены по подборкам: feedback/Fx/ и datamosh/Fx/.\n\n'
        'Каждая папка содержит полную подборку с собственными README, manifest.json, docs/ и SHA256SUMS. '
        'Для установки выбранной подборки скопируйте содержимое её Fx/ в ~/Fx/ на Pi или Fx в корне USB.\n\n'
        'Перед включением эффекта сбросьте Wet в ноль на несколько кадров. '
        'GLES-проверки выполнены; FPS и температура на Raspberry Pi пока не измерены.\n').encode()
    entries['SHA256SUMS'] = ''.join(hashlib.sha256(data).hexdigest()+'  '+name+'\n' for name,data in sorted(entries.items())).encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(entries.items()):
            info = zipfile.ZipInfo(name, (2026,1,1,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info,data)
    print(output)

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--version',required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('archives',type=Path,nargs='+')
    a=p.parse_args()
    build(a.archives,a.output,a.version)
