#!/usr/bin/env python3
"""Actual GLES tests for source-driven growth, color transport and fourth-knob drift."""
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
    r=Renderer(128,128)
    try:
        src,mask=disk(128,128)
        empty=np.zeros_like(src)
        for name in NAMES:
            r.load(ROOT/'Fx'/(name+'.frag'))
            black=run(r,empty,60)
            assert black.max()==0, name+': spontaneous pattern without a video seed'
            frame=run(r,src,40)
            bright=(frame.max(2)>64)&~mask
            assert bright.sum()>100, name+': front did not leave the source object'
            colors=frame[bright].astype(float);colors/=colors.max(1,keepdims=True)
            error=float(abs(colors-[1,96/255,32/255]).max())
            assert error<.075,name+': colored growth became a neutral mask'
            # Front remains colored after the video object is removed.
            tail=run(r,empty,12,reset=False)
            tail_mask=(tail.max(2)>64)&~mask
            assert tail_mask.sum()>100,name+': no independent propagated front'
            tc=tail[tail_mask].astype(float);tc/=tc.max(1,keepdims=True)
            assert abs(tc-[1,96/255,32/255]).max()<.075
            # No screen-centred vector field: translating a source translates its fronts.
            shifted,_=disk(128,128,71.5,63.5)
            moved=run(r,shifted,40)
            translation_error=float(abs(moved[:,8:].astype(float)-frame[:,:-8]).mean())
            assert translation_error<1.0,(name,'translation',translation_error)
            record=dict(transported_pixels=int(bright.sum()),transported_chroma_error=error,
                        translation_mean_error=translation_error,black_input_max=int(black.max()))
            if name.startswith('04'):
                y,x=np.mgrid[:128,:128];angle=np.arctan2(y-63.5,x-63.5)
                sector=np.floor((angle+np.pi)/(np.pi/4)).astype(int)%8
                counts=[int((bright&(sector==i)).sum()) for i in range(8)]
                assert min(counts)>15,('diffusion missing a direction',counts)
                symmetry=float(abs(frame.astype(float)-np.rot90(frame)).mean())
                assert symmetry<2.0,('directional bias',symmetry)
                record.update(eight_sector_pixels=counts,rotation_mean_error=symmetry)
            report[name]=record
            print('PASS source, transport, recovery and translation:',name,flush=True)
        r.load(ROOT/'Fx/04_reaction_diffusion.frag')
        # Independent source texture with features over the whole image for drift tests.
        source=fixture(128,128,40)
        no_left=run(r,source,70,(1,.35,.6,0),(.25,.35))
        no_right=run(r,source,70,(1,.35,.6,0),(.75,.65))
        assert np.array_equal(no_left,no_right),'Knob 3 at zero must remove displacement'
        high_left=run(r,source,70,(1,.35,.6,1),(.25,.35))
        high_right=run(r,source,70,(1,.35,.6,1),(.75,.65))
        amount_delta=float(abs(high_left.astype(float)-no_left).mean())
        centre_delta=float(abs(high_left.astype(float)-high_right).mean())
        assert amount_delta>5,('fourth knob has no visible range',amount_delta)
        assert centre_delta>5,('moving centre has no effect',centre_delta)
        # Unpatched hosts must not pretend to expose a raw fourth control.
        stock=[]
        for knob in [0,1]:
            r.reset();r.upload(source)
            for i in range(70):r.draw((1,.35,.6,knob),i/30)
            stock.append(r.pixels())
        assert np.array_equal(*stock)
        report['fourth_knob']=dict(zero_centre_independent=True,amount_mean_delta=amount_delta,
            moving_centre_mean_delta=centre_delta,stock_fallback_ignores_unavailable_knob=True)
        print('PASS fourth-knob displacement and stock-host fallback',flush=True)
    finally:r.close()
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
                    r.draw((1,.35,.55,.45),i/30,host_controls=True)
                    if i%6==0:clip.append(Image.fromarray(r.pixels()[::-1]))
                row.append(clip)
            clips.append(row)
    finally:r.close()
    animation=[]
    for i in range(30):
        image=Image.new('RGB',(576,336),(12,12,12));draw=ImageDraw.Draw(image)
        for row in range(2):
            for col,title in enumerate(['Input','Differential growth','Reaction + displacement']):
                image.paste(clips[row][col][i],(192*col,168*row+24))
                draw.text((192*col+4,168*row+5),title,fill='white')
        animation.append(image)
    animation[0].save(out/'video-fronts.gif',save_all=True,append_images=animation[1:],duration=200,loop=0)
    (out/'fronts-validation.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
