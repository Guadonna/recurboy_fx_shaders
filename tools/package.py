#!/usr/bin/env python3
"""Package each native PATTERN collection plus a flat shader-only common ZIP."""
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.2.1'

def write_zip(path, files):
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            entry = zipfile.ZipInfo(name,date_time=(2026,1,1,0,0,0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry,data)
    verify_zip(path,files)

def verify_zip(path, expected):
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None: raise ValueError('ZIP integrity failure')
        if len(archive.namelist()) != len(expected) or set(archive.namelist()) != set(expected):
            raise ValueError('Extra, missing, duplicate or nested ZIP entries')
        for name,data in expected.items():
            if archive.read(name) != data: raise ValueError(f'Content mismatch: {name}')

def build(root=ROOT, output=None):
    spec=json.loads((root/'manifest.json').read_text())
    if spec['version'] != VERSION or spec['host'] != 'stock' or spec['mode'] != 'PATTERN':
        raise ValueError('Unexpected manifest target or version')
    if not spec['collections']: raise ValueError('Refusing an empty release')
    output = output or root/'dist'/f'patterns-v{VERSION}'
    output.mkdir(parents=True,exist_ok=True)
    all_shaders={}
    assets=[]
    ids=set()
    for collection in spec['collections']:
        name=collection['id']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',name) or name in ids:
            raise ValueError(f'Invalid or repeated collection id: {name}')
        ids.add(name)
        declared=[item['file'] for item in collection['shaders']]
        if not declared or len(declared)!=len(set(declared)):
            raise ValueError('Empty or repeated shader list')
        folder=root/'Shaders'/name
        actual={p.name for p in folder.iterdir() if p.is_file()}
        if actual!=set(declared): raise ValueError(f'Unexpected collection files: {name}')
        files={'README.md':(root/'collections'/f'{name}.md').read_bytes()}
        for filename in declared:
            if Path(filename).name != filename or not filename.endswith('.frag'):
                raise ValueError(f'Invalid shader filename: {filename}')
            data=(folder/filename).read_bytes()
            files[f'Shaders/{name}/{filename}']=data
            all_shaders[f'{name}/{filename}']=data
        path=output/f'recurboy-patterns-{name}-v{collection["version"]}.zip'
        write_zip(path,files)
        assets.append(path)
    actual={p.relative_to(root/'Shaders').as_posix() for p in (root/'Shaders').rglob('*.frag')}
    if actual!=set(all_shaders): raise ValueError('Unlisted shader files')
    combined=output/f'recurboy-all-patterns-v{VERSION}.zip'
    write_zip(combined,all_shaders)
    assets.append(combined)
    checksums=''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in assets)
    (output/'SHA256SUMS').write_text(checksums)
    return assets

if __name__=='__main__':
    for path in build(): print(path)
