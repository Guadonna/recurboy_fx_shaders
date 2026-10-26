#!/usr/bin/env python3
"""Package one collection independently, with installable Fx/ at the archive root."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def build(name='bitwise'):
    if not re.fullmatch(r'[a-z0-9_-]+',name):
        raise ValueError('Use a simple collection name')
    base=ROOT
    manifest=json.loads((base/'manifest.json').read_text())
    if manifest['collection']!=name:raise ValueError('Collection identity mismatch')
    if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?',manifest['version']):
        raise ValueError('Invalid collection version')
    declared=[e['file'] for e in manifest['effects']]
    actual={p.relative_to(base).as_posix() for p in (base/'Fx').glob('*.frag')}
    if not declared or len(declared)!=len(set(declared)) or set(declared)!=actual:
        raise ValueError('Shader files do not match the manifest')
    entries=[(base/'README.md','README.md'),(base/'manifest.json','manifest.json')]
    for relative in sorted(actual):entries.append((base/relative,relative))
    for p in sorted((base/'docs').rglob('*')):
        if p.is_file():
            if not p.resolve().is_relative_to(base.resolve()):raise ValueError('File outside collection')
            entries.append((p,p.relative_to(base).as_posix()))
    entries.append((ROOT/'tools/pi_health.py','tools/pi_health.py'))
    names=[name for _,name in entries]
    if len(names)!=len(set(names)):raise ValueError('Duplicate archive path')
    out=ROOT/'dist'/manifest['collection'];out.mkdir(exist_ok=True,parents=True)
    archive=out/f"recurboy-{manifest['collection']}-v{manifest['version']}.zip"
    hashes=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for path,relative in sorted(entries,key=lambda entry:entry[1]):
            data=path.read_bytes();hashes.append(hashlib.sha256(data).hexdigest()+'  '+relative)
            info=zipfile.ZipInfo(relative,date_time=(2026,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            z.writestr(info,data)
        info=zipfile.ZipInfo('SHA256SUMS',date_time=(2026,1,1,0,0,0))
        z.writestr(info,'\n'.join(hashes)+'\n')
    (out/'SHA256SUMS').write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'  '+archive.name+'\n')
    print(archive)
    return archive

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('collection',nargs='?',default='bitwise');args=p.parse_args();build(args.collection)
