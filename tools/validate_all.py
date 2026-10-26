#!/usr/bin/env python3
"""Run existing category checks from their relocated directories."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from package import ROOT, catalog

def main():
    spec=catalog()
    parser=argparse.ArgumentParser()
    parser.add_argument('--collection',choices=[c['name'] for c in spec['collections']])
    args=parser.parse_args()
    output=ROOT/'artifacts';output.mkdir(exist_ok=True)
    tested=[]
    for category in spec['collections']:
        name=category['name']
        if args.collection and args.collection!=name: continue
        base=ROOT/'collections'/name
        scripts=['validate.py','validate_color_controls.py','validate_fronts.py'] if name=='fb-growth' else ['validate_collection.py']
        log=output/f'{name}.log'
        print(f'Checking {name}: {category["count"]} shaders',flush=True)
        with log.open('w') as stream:
            commands=[[sys.executable,str(base/'tools'/script)] for script in scripts]
            commands.append([sys.executable,'-m','unittest','discover','-s','tests','-v'])
            for command in commands:
                result=subprocess.run(command,cwd=base,stdout=stream,stderr=subprocess.STDOUT)
                if result.returncode:
                    stream.flush()
                    print(log.read_text()[-10000:],file=sys.stderr)
                    raise SystemExit(f'{name} failed; see {log}')
        tested.append(dict(collection=name,shaders=category['count'],result='passed'))
    subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,check=True)
    (output/'validation.json').write_text(json.dumps({'categories':tested,'raspberry_pi_fps_temperature':'not measured'},indent=2)+'\n')
    print(f'PASS: {len(tested)} categories, {sum(c["shaders"] for c in tested)} shaders')

if __name__=='__main__': main()
