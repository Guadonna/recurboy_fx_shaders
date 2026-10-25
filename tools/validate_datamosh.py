#!/usr/bin/env python3
"""Compile/render the datamosh collection with motion, cuts and real RGB8 feedback."""
import argparse
import itertools
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from gles import ROOT, Renderer, fixture

COLLECTION=ROOT

def movie(w,h,i):
    frame=fixture(w,h,i)
    y,x=np.mgrid[:h,:w]
    if i>=90:
        frame=frame[:,:,[2,0,1]].copy()
        frame=np.uint8(np.clip(255-frame.astype(float)*.8,0,255))
    if i>=180:
        frame=frame[:,::-1,[1,2,0]].copy()
    bar=(abs(x/w-(.15+.7*((i%75)/75)))<.035)&(y/h>.15)&(y/h<.85)
    frame[bar]=[235,235,235]
    return frame

def clock(frame,knob):
    # conjur::getTime uses previousElapsed-currentElapsed; setSpeed maps -2..2.
    return -(4*knob-2)*frame/30

def run(r,frames,knobs=(1,.55,.9,.65),seed=None,record=False):
    r.reset()
    if seed is not None:
        r.upload(seed);r.draw((0,0,0),0)
    snapshots=[]
    for i,src in enumerate(frames):
        r.upload(src);r.draw(knobs,clock(i,knobs[3]))
        if record and i%6==0:snapshots.append(r.pixels())
    return r.pixels(),snapshots

def gray(frame):
    y=np.uint8(np.rint(frame.astype(float)@np.array([.299,.587,.114])))
    return np.repeat(y[:,:,None],3,axis=2)

def delta(a,b):return float(abs(a.astype(float)-b).mean())

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'artifacts/datamosh');args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((COLLECTION/'manifest.json').read_text())
    w,h=192,144
    frames=[movie(w,h,i) for i in range(240)]
    r=Renderer(w,h)
    report=dict(r.info,collection='datamosh',collection_version=manifest['version'],hardware_validation=False,effects=[])
    clips=[('Input / scene cuts',frames[::6])];panels=[];ranges=[]
    outputs=[]
    try:
        for effect in manifest['effects']:
            path=COLLECTION/effect['file'];r.load(path)
            r.upload(frames[0]);r.draw((0,.5,.5))
            error=int(abs(r.pixels().astype(int)-frames[0]).max())
            assert error<=1,(path.name,'dry path',error)
            # Boundaries include fresh black/white feedback and signed/long clocks.
            for background in [0,1]:
                r.reset(background)
                for a,b in itertools.product([0,1],repeat=2):
                    for t in [-100000.25,0,100000.75]:
                        r.draw((1,a,b),t);r.pixels()
            default,clip=run(r,frames,effect['default_knobs'],seed=frames[0],record=True)
            outputs.append(default)
            assert delta(default,frames[-1])>2,(path.name,'effect not visible')
            assert default.std(axis=(0,1)).mean()>3,(path.name,'collapsed output')
            assert delta(clip[10],clip[-1])>2,(path.name,'video did not evolve')
            variants=[]
            for k in [(1,0,.9,.65),(1,1,.9,.65),(1,.55,0,.65),(1,.55,1,.65)]:
                variants.append(run(r,frames[:150],k,seed=frames[0])[0])
            a_delta,b_delta=delta(variants[0],variants[1]),delta(variants[2],variants[3])
            assert a_delta>2,(path.name,'knob 1',a_delta)
            assert b_delta>2,(path.name,'knob 2',b_delta)
            stopped=run(r,frames[:150],(1,.55,.9,.5),seed=frames[0])[0]
            running=run(r,frames[:150],(1,.55,.9,.85),seed=frames[0])[0]
            time_delta=delta(stopped,running)
            assert time_delta>1,(path.name,'fourth knob has no effect',time_delta)
            # Same new frame after different histories proves use of feedback.
            with_old=run(r,[frames[100]],seed=frames[0])[0]
            with_new=run(r,[frames[100]],seed=frames[100])[0]
            history_delta=delta(with_old,with_new)
            assert history_delta>2,(path.name,'history is ignored')
            # Gray video must not synthesize a tint. Chroma Bleed deliberately has no gray-only glitch.
            gs=[gray(f) for f in frames[:120]]
            mono=run(r,gs,seed=gs[0])[0]
            mono_error=int(np.ptp(mono.astype(int),axis=2).max())
            assert mono_error<=1,(path.name,'artificial color on grayscale',mono_error)
            record=dict(file=effect['file'],dry_max_error=error,frames=240,boundary_draws=24,
                knob_1_delta=a_delta,knob_2_delta=b_delta,clock_knob_delta=time_delta,
                history_delta=history_delta,grayscale_channel_error=mono_error,
                difference_from_input=delta(default,frames[-1]))
            if path.name.startswith('dm02'):
                assert delta(mono,gs[-1])<1, 'Chroma-only effect changed grayscale luminance'
                lum_error=float(abs((default.astype(float)-frames[-1])@np.array([.299,.587,.114])).mean())
                assert lum_error<10,('chroma bleed lost luminance',lum_error)
                record['mean_luminance_error']=lum_error
            if path.name.startswith('dm05'):
                red=np.full((h,w,3),[220,0,0],dtype=np.uint8)
                blue=np.full_like(red,[0,0,220]);green=np.full_like(red,[0,220,0])
                r.reset();r.upload(red);r.draw((0,0,0))
                r.upload(blue);r.draw((1,.45,.7),.1);held=r.pixels()
                frozen=(held[:,:,0]>210)&(held[:,:,2]<5)
                updated=(held[:,:,2]>210)&(held[:,:,0]<5)
                assert frozen.sum()>w*h*.2 and updated.sum()>w*h*.02
                r.upload(green);r.draw((1,.45,.7),.1);next_frame=r.pixels()
                assert abs(next_frame[frozen].astype(int)-red[frozen]).max()<=1
                assert abs(next_frame[updated].astype(int)-green[updated]).max()<=1
                record.update(exact_tile_hold=True,frozen_pixels=int(frozen.sum()),refreshed_pixels=int(updated.sum()))
            report['effects'].append(record)
            clips.append((effect['name'],clip));panels.append((effect['name'],clip[18]))
            ranges.append((effect['name'],variants))
            print('PASS',path.name,'ranges',round(a_delta,1),round(b_delta,1),'clock',round(time_delta,1),flush=True)
        # Five different mechanisms must not silently produce duplicate imagery.
        distances=[delta(a,b) for a,b in itertools.combinations(outputs,2)]
        assert min(distances)>3,('duplicate-looking effects',min(distances))
        report['minimum_pairwise_difference']=min(distances)
    finally:r.close()
    for width,height in [(63,47),(720,576)]:
        r=Renderer(width,height)
        try:
            src=movie(width,height,99)
            for effect in manifest['effects']:
                r.load(COLLECTION/effect['file']);r.upload(src);r.draw((0,1,1))
                assert abs(r.pixels().astype(int)-src).max()<=1
                r.draw((1,1,1),-.37);r.pixels()
        finally:r.close()
    report['additional_resolutions']=[[63,47],[720,576]]
    def montage(entries):
        image=Image.new('RGB',(w*3,(h+24)*2),(15,15,15));draw=ImageDraw.Draw(image)
        for i,(title,pixels) in enumerate(entries):
            x,y=(i%3)*w,(i//3)*(h+24)
            image.paste(Image.fromarray(pixels[::-1]),(x,y+24));draw.text((x+4,y+5),title,fill='white')
        return image
    montage([('Input / 0.6s after cut',frames[108])]+panels).save(args.output/'contact-sheet.png')
    animation=[montage([(name,clip[i]) for name,clip in clips]) for i in range(len(clips[0][1]))]
    animation[0].save(args.output/'datamosh.gif',save_all=True,append_images=animation[1:],duration=200,loop=0)
    sheet=Image.new('RGB',(w*4,(h+24)*5),(15,15,15));draw=ImageDraw.Draw(sheet)
    for row,(name,variants) in enumerate(ranges):
        for col,(label,pixels) in enumerate(zip(['A=0','A=1','B=0','B=1'],variants)):
            x,y=col*w,row*(h+24);sheet.paste(Image.fromarray(pixels[::-1]),(x,y+24))
            draw.text((x+4,y+5),name+' '+label,fill='white')
    sheet.save(args.output/'controls.png')
    (args.output/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Five datamosh shaders passed actual GLES rendering, motion/history and control checks.')

if __name__=='__main__':main()
