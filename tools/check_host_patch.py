#!/usr/bin/env python3
"""Check patches against exact upstream sources in disposable checkouts."""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    'recurboy': ('https://github.com/cyberboy666/recurBOY.git',
                '5f5ebf6da25111edaecda4a1db6b6f62a11481a3'),
    'ofxVideoArtTools': ('https://github.com/cyberboy666/ofxVideoArtTools.git',
                       '00dc93725073b1cf5bfc5d4a56e8d3256a995d81'),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--recurboy', help='Optional local upstream clone')
    parser.add_argument('--addon', help='Optional local upstream clone')
    args = parser.parse_args()
    sources = {'recurboy': args.recurboy, 'ofxVideoArtTools': args.addon}
    with tempfile.TemporaryDirectory() as directory:
        for name, (url, revision) in PINS.items():
            checkout = Path(directory) / name
            subprocess.run(['git', 'clone', '--quiet', '--no-checkout',
                            sources[name] or url, str(checkout)], check=True)
            subprocess.run(['git', 'checkout', '--quiet', '--detach', revision],
                           cwd=checkout, check=True)
            patch = ROOT / 'host' / f'{name}-cv-matrix.patch'
            subprocess.run(['git', 'apply', '--check', str(patch)], cwd=checkout, check=True)
            subprocess.run(['git', 'apply', str(patch)], cwd=checkout, check=True)
            if name == 'recurboy':
                target = checkout / 'software/ofRecurBoy/src/CvMatrix.h'
                shutil.copy2(ROOT / 'host/CvMatrix.h', target)
            print(f'{name}: patch applies to {revision}')


if __name__ == '__main__':
    main()
