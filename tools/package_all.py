#!/usr/bin/env python3
"""Build a device bundle: collection/*.frag only, with no nested Fx/ or docs."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile


def collect_shaders(archives):
    entries = {}
    collections = set()
    for path in archives:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            assert len(names) == len(set(names)), 'Duplicate ZIP member'
            assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
            manifest = json.loads(z.read('manifest.json'))
            name = manifest['collection']
            assert re.fullmatch(r'[a-z0-9_-]+', name), 'Invalid collection name'
            assert name not in collections, 'Duplicate collection'
            collections.add(name)
            hashes = {}
            for line in z.read('SHA256SUMS').decode().splitlines():
                digest, item = line.split('  ', 1)
                assert hashlib.sha256(z.read(item)).hexdigest() == digest
                hashes[item] = digest
            declared = [e['file'] for e in manifest['effects']]
            assert declared and len(declared) == len(set(declared))
            assert set(declared) == {n for n in names if n.endswith('.frag')}
            for item in declared:
                p = PurePosixPath(item)
                assert len(p.parts) == 2 and p.parts[0] == 'Fx' and p.suffix == '.frag'
                assert item in hashes, 'Missing shader checksum'
                target = f'{name}/{p.name}'
                assert target not in entries, 'Duplicate shader path'
                entries[target] = z.read(item)
    assert entries, 'No shaders to package'
    return entries


def verify_bundle(path, archives):
    expected = collect_shaders(archives)
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        assert len(names) == len(set(names)) and set(names) == set(expected), 'Bundle must contain only collection/*.frag'
        for name, data in expected.items():
            assert z.read(name) == data, f'Changed shader: {name}'
    return len(expected)


def build(archives, output, version):
    # Version belongs to the release filename; do not add metadata to device folders.
    entries = collect_shaders(archives)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(entries.items()):
            info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, data)
    verify_bundle(output, archives)
    print(output)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--version', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('archives', type=Path, nargs='+')
    a = p.parse_args()
    build(a.archives, a.output, a.version)
