#!/usr/bin/env python3
"""Build one documented kit plus a flat, shader-only all-patterns archive."""
import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.1.0'


def write_zip(path, files):
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, source in sorted(files.items()):
            entry = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, source.read_bytes())
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == set(files)
        for name, source in files.items():
            assert archive.read(name) == source.read_bytes()


def main():
    output = ROOT / 'dist'
    output.mkdir(exist_ok=True)
    shaders = sorted((ROOT / 'Shaders').glob('*.frag'))
    assert len(shaders) == 1, 'This prototype release contains exactly one shader'
    documented = {'README.md': ROOT / 'README.md'}
    for directory in ['Shaders', 'host', 'docs']:
        for path in sorted((ROOT / directory).rglob('*')):
            if path.is_file():
                documented[path.relative_to(ROOT).as_posix()] = path
    kit = output / f'recurboy-pattern-cv-matrix-v{VERSION}.zip'
    combined = output / f'recurboy-all-patterns-v{VERSION}.zip'
    write_zip(kit, documented)
    write_zip(combined, {f'cv-matrix/{shader.name}': shader for shader in shaders})
    checksums = '\n'.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}'
                          for p in [kit, combined]) + '\n'
    (output / 'SHA256SUMS').write_text(checksums)
    print(checksums, end='')


if __name__ == '__main__':
    main()
