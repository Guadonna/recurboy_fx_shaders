#!/usr/bin/env python3
"""Build and verify a pinned release: individual ZIPs plus a separated bundle."""
import argparse,hashlib,json,shutil,subprocess,sys,zipfile
from pathlib import Path
from package_all import build

def check(path):
 with zipfile.ZipFile(path) as z:
  names=z.namelist();assert len(names)==len(set(names))
  assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in names)
  m=json.loads(z.read('manifest.json'))
  if 'collections' in m:
   declared={c['directory']+'/'+e['file'] for c in m['collections'] for e in c['effects']}
   assert not any(n.startswith('Fx/') for n in names)
   for c in m['collections']:
    base=c['directory']+'/'
    for line in z.read(base+'SHA256SUMS').decode().splitlines():
     h,n=line.split('  ',1);assert hashlib.sha256(z.read(base+n)).hexdigest()==h
  else:declared={e['file'] for e in m['effects']}
  assert declared=={n for n in names if n.endswith('.frag')}
  for line in z.read('SHA256SUMS').decode().splitlines():
   h,n=line.split('  ',1);assert hashlib.sha256(z.read(n)).hexdigest()==h
 return m

def main():
 p=argparse.ArgumentParser();p.add_argument('config',type=Path);p.add_argument('--build-root',type=Path,default=Path('build'));p.add_argument('--output',type=Path,default=Path('release-assets'));a=p.parse_args()
 spec=json.loads(a.config.read_text());out=a.output;out.mkdir(parents=True,exist_ok=True)
 assert not list(out.glob('*.zip')),'Use an empty output directory to avoid stale assets'
 archives=[];total=0
 for c in spec['collections']:
  checkout=a.build_root/c['name']
  actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=checkout,text=True).strip();assert actual==c['ref'],(c['name'],'wrong commit')
  manifest=json.loads((checkout/'manifest.json').read_text())
  assert manifest['collection']==c['name'] and manifest['version']==c['version'] and len(manifest['effects'])==c['count']
  subprocess.run([sys.executable,str((checkout/'tools/package.py').resolve())],check=True)
  filename=f"recurboy-{c['name']}-v{c['version']}.zip"
  matches=list((checkout/'dist').rglob(filename));assert len(matches)==1
  dest=out/filename;shutil.copyfile(matches[0],dest);check(dest);archives.append(dest);total+=c['count']
 combined=out/f"recurboy-all-collections-v{spec['version']}.zip"
 build(archives,combined,spec['version']);m=check(combined)
 assert len(m['collections'])==len(spec['collections']) and sum(len(c['effects']) for c in m['collections'])==total
 # The bundle must preserve every original collection file, including its checksums.
 with zipfile.ZipFile(combined) as bundle:
  for archive in archives:
   with zipfile.ZipFile(archive) as single:
    base=json.loads(single.read('manifest.json'))['collection']+'/'
    assert {n[len(base):] for n in bundle.namelist() if n.startswith(base)}==set(single.namelist())
    for n in single.namelist():assert bundle.read(base+n)==single.read(n)
 (out/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in sorted(out.glob('*.zip'))))
 print(f'Verified {len(archives)} collections, {total} shaders, {len(archives)+1} ZIPs')
if __name__=='__main__':main()
