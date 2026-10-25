#!/usr/bin/env python3
"""GPU regression checks for source color, monochrome, feedback and knob range."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from validate import ROOT, Renderer, fixture

GROWTH = ('02_', '04_', '11_')

def run(renderer, frames, knobs, reset=True):
    if reset:
        renderer.reset()
    for i, source in enumerate(frames):
        renderer.upload(source)
        renderer.draw(knobs, -i/30)
    return renderer.pixels()

def gray(source):
    value=np.uint8(np.rint(source.astype(float) @ np.array([.299,.587,.114])))
    return np.repeat(value[:,:,None],3,axis=2)

def chroma_error(output, source):
    # Quantization error increases near black; exclude pixels below 32/255.
    out=output.astype(float)
    src=source.astype(float)
    bright=(out.max(axis=2)>=32) & (src.max(axis=2)>=32)
    assert bright.sum()>100, 'No visible colored pattern to validate'
    a=out[bright]/out[bright].max(axis=1,keepdims=True)
    b=src[bright]/src[bright].max(axis=1,keepdims=True)
    return float(abs(a-b).max())

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'artifacts')
    parser.add_argument('--baseline',type=Path)
    args=parser.parse_args()
    args.output.mkdir(exist_ok=True,parents=True)
    manifest=json.loads((ROOT/'manifest.json').read_text())
    width,height=192,144
    frames=[fixture(width,height,i) for i in range(120)]
    grays=[gray(f) for f in frames]
    renderer=Renderer(width,height)
    baseline_version=json.loads((args.baseline/'manifest.json').read_text())['version'] if args.baseline else None
    report={'purpose':'Rendered image regressions, not Pi performance measurements','effects':[]}
    sheets=[]
    comparisons=[]
    animations=[]
    try:
        for item in manifest['effects']:
            path=ROOT/item['file']
            renderer.load(path)
            knobs=item['default_knobs'][:3]
            default=run(renderer,frames,knobs)
            results=[]
            for k in [(1,0,.7),(1,1,.7),(1,.55,0),(1,.55,1)]:
                results.append(run(renderer,frames,k))
            delta_a=float(abs(results[0].astype(float)-results[1]).mean())
            delta_b=float(abs(results[2].astype(float)-results[3]).mean())
            assert delta_a>4, f'{path.name}: knob 1 has too little visible range ({delta_a})'
            assert delta_b>4, f'{path.name}: knob 2 has too little visible range ({delta_b})'
            monochrome=run(renderer,grays,knobs)
            mono_error=int(np.ptp(monochrome.astype(int),axis=2).max())
            assert mono_error<=1, f'{path.name}: monochrome input became colored'
            record=dict(file=item['file'],knob_1_mean_delta=delta_a,knob_2_mean_delta=delta_b,
                        monochrome_channel_error=mono_error)
            if path.name.startswith("02_"):
                # Hue of the current image, even when feedback held another palette.
                hue_errors=[]
                for wet in [0.35,1]:
                    colored=run(renderer,frames,(wet,*knobs[1:]))
                    hue_errors.append(chroma_error(colored,frames[-1]))
                    source=frames[-1][:,:,[2,0,1]].copy()
                    renderer.upload(source);renderer.draw((wet,*knobs[1:]))
                    hue_errors.append(chroma_error(renderer.pixels(),source))
                    renderer.upload(grays[-1]);renderer.draw((wet,*knobs[1:]))
                    error=int(np.ptp(renderer.pixels().astype(int),axis=2).max())
                    assert error<=1, f'{path.name}: colored feedback leaked into grayscale input'
                assert max(hue_errors)<=.035, f'{path.name}: source hue mismatch {max(hue_errors)}'
                # Same value field with two very different hues must give the same dynamics.
                value=np.max(frames[-1],axis=2)
                peak_outputs=[]
                for tint in [(1,0,0),(0,1,1)]:
                    source=np.uint8(value[:,:,None]*np.array(tint)[None,None,:])
                    peak_outputs.append(run(renderer,[source]*120,knobs).max(axis=2))
                state_error=int(abs(peak_outputs[0].astype(int)-peak_outputs[1]).max())
                assert state_error<=1, f'{path.name}: growth depends on RGB channel choice'
                record.update(source_chroma_error=max(hue_errors),
                              palette_transition_passed=True,color_independent_state_error=state_error)
            if path.name.startswith(GROWTH):
                # Actual renders for a six-panel animated RGB/mono preview.
                clips=[]
                for inputs in [frames,grays]:
                    renderer.reset();clip=[]
                    for i,source in enumerate(inputs):
                        renderer.upload(source);renderer.draw(knobs,-i/30)
                        if i%4==0: clip.append(renderer.pixels())
                    clips.append(clip)
                animations.append((path.stem,clips))
            if args.baseline:
                renderer.load(args.baseline/item['file'])
                before=run(renderer,frames,knobs)
                before_diff=float(abs(before.astype(float)-frames[-1]).mean())
                after_diff=float(abs(default.astype(float)-frames[-1]).mean())
                record.update(baseline_version=baseline_version,baseline_difference_from_input=before_diff,current_difference_from_input=after_diff)
                comparisons.append((path.stem,[frames[-1],before,default]))
            sheets.append((path.stem,[results[0],results[1],default,results[2],results[3],monochrome]))
            report['effects'].append(record)
            print('PASS',path.name,'knob deltas',round(delta_a,1),round(delta_b,1),flush=True)
    finally:
        renderer.close()
    def sheet(rows, labels, name):
        image=Image.new('RGB',(width*len(labels),(height+34)*len(rows)),(12,12,12))
        draw=ImageDraw.Draw(image)
        for r,(title,panels) in enumerate(rows):
            for c,frame in enumerate(panels):
                x,y=c*width,r*(height+34)
                image.paste(Image.fromarray(frame[::-1]),(x,y+34))
                draw.text((x+3,y+2),title,fill='white')
                draw.text((x+3,y+17),labels[c],fill='white')
        image.save(args.output/name)
    sheet(sheets,['A=0','A=1','Default .55 / .70','B=0','B=1','Monochrome'],'control-ranges.png')
    if comparisons:
        sheet(comparisons,['Input',f'v{baseline_version} / same knobs',f'v{manifest["version"]} / same knobs'],'before-after.png')
    gif=[]
    for i in range(30):
        image=Image.new('RGB',(width*3,(height+24)*2),(12,12,12))
        draw=ImageDraw.Draw(image)
        for col,(name,clips) in enumerate(animations):
            for row,clip in enumerate(clips):
                x,y=col*width,row*(height+24)
                image.paste(Image.fromarray(clip[i][::-1]),(x,y+24))
                draw.text((x+3,y+5),name+(' RGB' if row==0 else ' B/W'),fill='white')
        gif.append(image)
    gif[0].save(args.output/'growth-colors.gif',save_all=True,append_images=gif[1:],duration=133,loop=0)
    (args.output/'color-controls.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Monochrome and both knob ranges passed for all 11 effects; mycelium palette tests passed.')

if __name__=='__main__': main()
