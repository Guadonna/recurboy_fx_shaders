#!/usr/bin/env python3
"""Real GLES tests for native controls, feedback, color and bounded shader cost."""
import itertools,json,re,tempfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from gles import ROOT,Renderer,fixture

def delta(a,b):return float(abs(a.astype(float)-b).mean())
def run(r,frames,knobs,seed=None,record=False):
 r.reset()
 if seed is not None:r.upload(seed);r.draw((0,0,0))
 shots=[]
 for i,src in enumerate(frames):
  r.upload(src);r.draw(knobs,-(4*knobs[3]-2)*i/30)
  if record and i%6==0:shots.append(r.pixels())
 return r.pixels(),shots

def semantics(manifest):
 key=manifest['collection'];report={}
 if key not in ['pixel-sorting','bitwise']:return report
 source=(ROOT/manifest['effects'][0]['file']).read_text();common=source.split('void main()')[0]
 with tempfile.TemporaryDirectory() as td:
  p=Path(td)/'probe.frag'
  if key=='pixel-sorting':
   perms=np.array(list(itertools.permutations([20,65,110,180,240])),np.uint8)
   image=np.repeat(perms[:,:,None],3,axis=2)
   calls=''.join(f'vec3 v{i}=video(vec2({(i+.5)/5},v_texcoord.y));' for i in range(5))
   network=source[source.index('order(v0,v1);'):source.index('float gate=')]
   p.write_text(common+'void main(){float index=floor(v_texcoord.x*5.);'+calls+network+'gl_FragColor=vec4(selected,1.);}')
   r=Renderer(5,120)
   try:
    r.load(p);r.upload(image);r.draw();out=r.pixels()
    expected=np.repeat(np.sort(perms,axis=1)[:,:,None],3,axis=2)
    assert abs(out.astype(int)-expected).max()<=1,'GPU sorting network incorrect'
    report['sorted_permutations']=120
   finally:r.close()
  else:
   r=Renderer(16,16)
   try:
    y,x=np.mgrid[:16,:16]
    for mode,name in [(0,'xor'),(1,'and'),(2,'or')]:
     p.write_text(common+'void main(){vec3 a=vec3(floor(v_texcoord.x*16.)/15.);vec3 b=vec3(floor(v_texcoord.y*16.)/15.);gl_FragColor=vec4(logic4(a,b,'+str(mode)+'.),1.);}')
     r.load(p);r.upload(np.zeros((16,16,3),np.uint8));r.draw();out=r.pixels()[:,:,0]
     expected=([x^y,x&y,x|y][mode]*17).astype(np.uint8)
     assert abs(out.astype(int)-expected).max()<=1,name+' truth table failed'
     report[name+'_pairs_verified']=256
   finally:r.close()
 return report

def main():
 manifest=json.loads((ROOT/'manifest.json').read_text());outdir=ROOT/'artifacts';outdir.mkdir(exist_ok=True)
 w,h=192,144;frames=[fixture(w,h,i) for i in range(120)]
 for i in range(60,120):frames[i]=frames[i][:,:,[2,0,1]].copy()
 r=Renderer(w,h);report=dict(r.info,collection=manifest['collection'],hardware_validation=False,effects=[])
 outputs=[];panels=[];ranges=[];clips=[('Input',frames[::6])]
 try:
  for e in manifest['effects']:
   path=ROOT/e['file'];source=path.read_text();mainbody=source.split('void main()')[1]
   reads=len(re.findall(r'\b(?:video|past)\(',mainbody))
   assert reads==e['texture_reads'] and reads<=6,(path.name,reads,e['texture_reads'])
   assert not re.search(r'\b(?:while|for)\s*\(',source)
   assert not re.search(r'\bu_x3\b|\bu_fx_',source)
   r.load(path);r.reset(1);r.upload(frames[0]);r.draw((0,1,1),-100000.25)
   dry=int(abs(r.pixels().astype(int)-frames[0]).max());assert dry<=1
   for history in [0,1]:
    for a,b in itertools.product([0,1],repeat=2):
     r.reset(history)
     for t in [-100000.25,0,100000.75]:r.draw((1,a,b),t);r.pixels()
   default,clip=run(r,frames,e['default_knobs'],seed=frames[0],record=True)
   assert delta(default,frames[-1])>2,(path.name,'invisible',delta(default,frames[-1]))
   assert default.std(axis=(0,1)).mean()>3,(path.name,'collapsed')
   variants=[run(r,frames[:60],k,seed=frames[0])[0] for k in [(1,0,.75,.65),(1,1,.75,.65),(1,.55,0,.65),(1,.55,1,.65)]]
   da,db=delta(*variants[:2]),delta(*variants[2:]);assert da>1.5 and db>1.5,(path.name,'controls',da,db)
   _,stopped=run(r,frames[:60],(1,.55,.75,.5),seed=frames[0],record=True)
   _,running=run(r,frames[:60],(1,.55,.75,.85),seed=frames[0],record=True)
   clock=float(np.mean([delta(x,y) for x,y in zip(stopped,running)]));assert clock>.6,(path.name,'clock',clock)
   rec=dict(file=e['file'],dry_max_error=dry,texture_reads=reads,knob_a_delta=da,knob_b_delta=db,clock_delta=clock,difference_from_input=delta(default,frames[-1]),feedback_frames=120,boundary_draws=24)
   if e['feedback']:
    old=run(r,[frames[60]],e['default_knobs'],seed=frames[0])[0];new=run(r,[frames[60]],e['default_knobs'],seed=frames[60])[0]
    rec['history_delta']=delta(old,new);assert rec['history_delta']>1,(path.name,'feedback ignored')
   if e['grayscale']:
    gray=[np.repeat(np.uint8(np.rint(f.astype(float)@np.array([.299,.587,.114])))[:,:,None],3,axis=2) for f in frames[:48]]
    mono=run(r,gray,e['default_knobs'],seed=gray[0])[0]
    rec['gray_error']=int(np.ptp(mono.astype(int),axis=2).max());assert rec['gray_error']<=1,(path.name,'grayscale',rec['gray_error'])
   report['effects'].append(rec);outputs.append(default);panels.append((e['name'],clip[12]));ranges.append((e['name'],variants));clips.append((e['name'],clip))
   print('PASS',path.name,'controls',round(da,1),round(db,1),'clock',round(clock,1),flush=True)
  diffs=[delta(a,b) for a,b in itertools.combinations(outputs,2)];assert min(diffs)>2,('duplicate variants',min(diffs));report['min_pair_difference']=min(diffs)
 finally:r.close()
 for w2,h2 in [(63,47),(720,576)]:
  r=Renderer(w2,h2)
  try:
   frame=fixture(w2,h2,42)
   for e in manifest['effects']:
    r.load(ROOT/e['file']);r.upload(frame);r.reset();r.draw((0,1,1));assert abs(r.pixels().astype(int)-frame).max()<=1
    r.draw((1,1,1),-.37);r.pixels()
  finally:r.close()
 report['additional_resolutions']=[[63,47],[720,576]];report['semantics']=semantics(manifest)
 def montage(items):
  im=Image.new('RGB',(w*3,(h+24)*2),(14,14,14));d=ImageDraw.Draw(im)
  for i,(title,pixels) in enumerate(items):
   x,y=i%3*w,i//3*(h+24);im.paste(Image.fromarray(pixels[::-1]),(x,y+24));d.text((x+3,y+5),title,fill='white')
  return im
 montage([('Input',frames[72])]+panels).save(outdir/'contact-sheet.png')
 animation=[montage([(name,seq[i]) for name,seq in clips]) for i in range(20)]
 animation[0].save(outdir/'preview.gif',save_all=True,append_images=animation[1:],duration=200,loop=0)
 im=Image.new('RGB',(w*4,(h+24)*5),(14,14,14));d=ImageDraw.Draw(im)
 for row,(name,items) in enumerate(ranges):
  for col,(label,pixels) in enumerate(zip(['A=0','A=1','B=0','B=1'],items)):
   x,y=col*w,row*(h+24);im.paste(Image.fromarray(pixels[::-1]),(x,y+24));d.text((x+3,y+5),name+' '+label,fill='white')
 im.save(outdir/'controls.png');(outdir/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print('PASS collection',manifest['collection'],report['semantics'],flush=True)
if __name__=='__main__':main()
