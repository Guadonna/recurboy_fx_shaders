#!/usr/bin/env python3
"""Build FX category archives and a shader-only common ZIP from this checkout."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile
from package_all import build as build_common, verify_bundle

ROOT = Path(__file__).resolve().parents[1]
VERSION = '1.3.0'

def catalog():
    spec=json.loads((ROOT/'manifest.json').read_text())
    if spec['version']!=VERSION or spec['mode']!='FX': raise ValueError('Wrong release manifest')
    names=[c['name'] for c in spec['collections']]
    if not names or len(names)!=len(set(names)): raise ValueError('Empty or duplicate categories')
    for category in spec['collections']:
        name=category['name']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',name): raise ValueError('Invalid category id')
        base=ROOT/'collections'/name
        manifest=json.loads((base/'manifest.json').read_text())
        if (manifest['collection'],manifest['version'],len(manifest['effects']))!=(name,category['version'],category['count']):
            raise ValueError(f'Category manifest mismatch: {name}')
        declared={e['file'] for e in manifest['effects']}
        actual={p.relative_to(base).as_posix() for p in (base/'Fx').glob('*.frag')}
        if len(declared)!=category['count'] or declared!=actual: raise ValueError(f'Unexpected shader files: {name}')
    return spec

def build():
    spec=catalog()
    output=ROOT/'dist'/f'fx-v{VERSION}'
    output.mkdir(parents=True,exist_ok=True)
    paths=[]
    for category in spec['collections']:
        base=ROOT/'collections'/category['name']
        subprocess.run([sys.executable,str(base/'tools/package.py')],cwd=base,check=True,stdout=subprocess.DEVNULL)
        filename=f'recurboy-{category["name"]}-v{category["version"]}.zip'
        candidates=list((base/'dist').rglob(filename))
        if len(candidates)!=1: raise ValueError(f'Ambiguous category archive: {filename}')
        dest=output/filename
        shutil.copyfile(candidates[0],dest)
        with zipfile.ZipFile(dest) as archive:
            for item in category_manifest(base)['effects']:
                if archive.read(item['file'])!=(base/item['file']).read_bytes():
                    raise ValueError(f'Changed shader in {filename}')
        paths.append(dest)
    combined=output/f'recurboy-all-fx-v{VERSION}.zip'
    build_common(paths,combined,VERSION)
    expected=sum(c['count'] for c in spec['collections'])
    if verify_bundle(combined,paths)!=expected: raise ValueError('Wrong common archive count')
    paths.append(combined)
    if set(output.glob('*.zip'))!=set(paths): raise ValueError('Stale ZIPs in release directory')
    (output/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in paths))
    print(f'Verified {len(spec["collections"])} categories, {expected} shaders, {len(paths)} ZIPs in {output}')
    return paths

def category_manifest(base):
    return json.loads((base/'manifest.json').read_text())

if __name__=='__main__': build()
