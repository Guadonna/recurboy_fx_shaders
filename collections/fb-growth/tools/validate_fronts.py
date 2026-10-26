#!/usr/bin/env python3
"""Actual GLES tests for source-driven growth, color transport and particle scale and absence of displacement."""
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from validate import ROOT, Renderer, fixture

NAMES=['11_differential_growth','04_reaction_diffusion']

def disk(w,h,cx=None,cy=None,color=(255,96,32)):
    y,x=np.mgrid[:h,:w]
    cx=(w-1)/2 if cx is None else cx
    cy=(h-1)/2 if cy is None else cy
    mask=(x-cx)**2+(y-cy)**2<25
    out=np.zeros((h,w,3),np.uint8);out[mask]=color
    return out,mask

def run(r,source,frames=40,knobs=(1,0,.7,0),centre=(.5,.5),reset=True):
    if reset:r.reset()
    r.upload(source)
    for i in range(frames):r.draw(knobs,i/30,host_controls=True,drift=centre)
    return r.pixels()

def main():
    out=ROOT/'artifacts';out.mkdir(exist_ok=True)
    report={}
    for name in NAMES:
        n=129 if name.startswith('04') else 128
        shift=9 if name.startswith('04') else 8
        r=Renderer(n,n)
        try:
            src,mask=disk(n,n)
            empty=np.zeros_like(src)
            r.load(ROOT/'Fx'/(name+'.frag'))
            black=run(r,empty,60)
            assert black.max()==0, name+': spontaneous pattern without a video seed'
            frame=run(r,src,40)
            bright=(frame.max(2)>64)&~mask
            assert bright.sum()>100, name+': front did not leave the source object'
            colors=frame[bright].astype(float);colors/=colors.max(1,keepdims=True)
            error=float(abs(colors-[1,96/255,32/255]).max())
            assert error<.075,name+': colored growth became a neutral mask'
            tail=run(r,empty,12,reset=False)
            tail_mask=(tail.max(2)>64)&~mask
            assert tail_mask.sum()>100,name+': no independent propagated front'
            tc=tail[tail_mask].astype(float);tc/=tc.max(1,keepdims=True)
            assert abs(tc-[1,96/255,32/255]).max()<.075
            # Coarse diffusion lattice: translate by an integer number of cells.
            shifted,_=disk(n,n,(n-1)/2+shift,(n-1)/2)
            moved=run(r,shifted,40)
            translation_error=float(abs(moved[:,shift:].astype(float)-frame[:,:-shift]).mean())
            assert translation_error<1.0,(name,'translation',translation_error)
            record=dict(transported_pixels=int(bright.sum()),transported_chroma_error=error,
                        translation_mean_error=translation_error,black_input_max=int(black.max()))
            if name.startswith('04'):
                y,x=np.mgrid[:n,:n];angle=np.arctan2(y-(n-1)/2,x-(n-1)/2)
                sector=np.floor((angle+np.pi)/(np.pi/4)).astype(int)%8
                counts=[int((bright&(sector==i)).sum()) for i in range(8)]
                assert min(counts)>15,('diffusion missing a direction',counts)
                symmetry=float(abs(frame.astype(float)-np.rot90(frame)).mean())
                assert symmetry<2.0,('directional bias',symmetry)
                record.update(eight_sector_pixels=counts,rotation_mean_error=symmetry)
            report[name]=record
            print('PASS source, transport, recovery and translation:',name,flush=True)
        finally:r.close()
    r=Renderer(128,128)
    try:
        r.load(ROOT/'Fx/04_reaction_diffusion.frag')
        source=fixture(128,128,40)
        results=[]
        for knob,patched,centre,speed in [(0,False,(.2,.2),0),(1,False,(.8,.8),-2),
                                          (0,True,(.1,.9),2),(1,True,(.9,.1),10000)]:
            r.reset();r.upload(source)
            for i in range(70):r.draw((1,.35,.6,knob),speed*i,host_controls=patched,drift=centre)
            results.append(r.pixels())
        assert all(np.array_equal(results[0],v) for v in results[1:]),'Displacement or clock still affects diffusion'
        report['displacement_removed']=dict(stock_and_patched_hosts_identical=True,clock_independent=True)
    finally:r.close()
    scales=[]
    states=[]
    for a,size in [(0,3),(.5,17),(1,31)]:
        n=19*size
        r=Renderer(n,n)
        try:
            r.load(ROOT/'Fx/04_reaction_diffusion.frag')
            source=np.zeros((n,n,3),np.uint8)
            source[n//2,n//2]=(255,96,32)
            frame=run(r,source,12,(1,a,.7,0))
            bright=frame.max(2)>64
            yy,xx=np.where(bright)
            assert len(xx)>0
            extent=int(xx.max()-xx.min()+1)
            states.append(frame[size//2::size,size//2::size])
            scales.append(dict(knob=a,cell_size=size,front_width=extent))
        finally:r.close()
    # Changing size rescales the same wave dynamics, instead of adding fine noise.
    assert all(abs(v.astype(int)-states[0]).max()<=4 for v in states[1:]),'Size changed cell dynamics'
    widths=[s['front_width'] for s in scales]
    assert widths[1]>widths[0]*4 and widths[2]>widths[1]*1.5,scales
    report['particle_size']=scales
    print('PASS displacement absent and particle/front sizes:',scales,flush=True)
    # Six-panel real-render preview: input, differential, reaction; video and isolated seed.
    r=Renderer(192,144)
    streams=[[fixture(192,144,i) for i in range(180)], [disk(192,144)[0]]*180]
    clips=[]
    try:
        for sources in streams:
            row=[[Image.fromarray(s[::-1]) for s in sources[::6]]]
            for name in NAMES:
                r.load(ROOT/'Fx'/(name+'.frag'));r.reset();clip=[]
                for i,source in enumerate(sources):
                    r.upload(source)
                    r.draw((1,.2 if name.startswith("04") else .35,.55,.45),i/30)
                    if i%6==0:clip.append(Image.fromarray(r.pixels()[::-1]))
                row.append(clip)
            clips.append(row)
    finally:r.close()
    animation=[]
    for i in range(30):
        image=Image.new('RGB',(576,336),(12,12,12));draw=ImageDraw.Draw(image)
        for row in range(2):
            for col,title in enumerate(['Input','Differential growth','Reaction / size .20']):
                image.paste(clips[row][col][i],(192*col,168*row+24))
                draw.text((192*col+4,168*row+5),title,fill='white')
        animation.append(image)
    animation[0].save(out/'video-fronts.gif',save_all=True,append_images=animation[1:],duration=200,loop=0)
    (out/'fronts-validation.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
