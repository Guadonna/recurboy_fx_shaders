#!/usr/bin/env python3
"""PAL-size GLES stress; reports completion, not Raspberry Pi throughput."""
import itertools,json
from pathlib import Path
from gles import ROOT,Renderer,fixture

def main():
 r=Renderer(720,576);records=[]
 try:
  m=json.loads((ROOT/'manifest.json').read_text());frames=[fixture(720,576,i*9) for i in range(8)]
  for effect in m['effects']:
   r.load(ROOT/effect['file']);count=0
   for a,b in itertools.product([0,1],repeat=2):
    r.reset(1)
    for i in range(64):
     r.upload(frames[i%len(frames)]);r.draw((1,a,b),-i/30)
     if i%8==0:r.pixels()
     count+=1
   r.pixels();records.append(dict(file=effect['file'],resolution=[720,576],frames=count,passed=True))
   print('PASS PAL stress',effect['file'],count,'frames',flush=True)
 finally:r.close()
 out=ROOT/'artifacts';out.mkdir(exist_ok=True)
 (out/'sorting-stress.json').write_text(json.dumps({'hardware_validation':False,'effects':records},indent=2)+'\n')
if __name__=='__main__':main()
