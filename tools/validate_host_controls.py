#!/usr/bin/env python3
"""Compile the patched upstream control code against a small OF test double.
This tests uniform plumbing and old speed semantics, not an ARM/openFrameworks build.
"""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
REV='00dc93725073b1cf5bfc5d4a56e8d3256a995d81'
STUB=r'''
#pragma once
#include <algorithm>
#include <cmath>
#include <map>
#include <sstream>
#include <string>
#include <utility>
#include <vector>
using namespace std;
extern float testClock;
inline float ofGetElapsedTimef(){return testClock;}
inline int ofGetWidth(){return 320;}
inline int ofGetHeight(){return 240;}
inline float ofClamp(float x,float a,float b){return max(a,min(x,b));}
inline string ofToString(int x){return to_string(x);}
inline ostringstream ofLog(){return ostringstream();}
inline void ofClear(int,int,int,int){}
inline void ofDrawRectangle(int,int,int,int){}
const int GL_RGB=0x1907;
struct ofTexture{void draw(int,int,int,int){}};
struct ofFbo{
 bool allocated=false;
 void allocate(int,int,int){allocated=true;}
 bool isAllocated(){return allocated;}
 void begin(){} void end(){}
};
struct ofShader{
 map<string,float> one;
 map<string,pair<float,float>> two;
 void load(string){} void load(string,string){}
 void begin(){} void end(){}
 void setUniform1f(string s,float x){one[s]=x;}
 void setUniform1i(string,int){}
 void setUniform2f(string s,float x,float y){two[s]={x,y};}
 void setUniform4f(string,float,float,float,float){}
 void setUniform4i(string,int,int,int,int){}
 void setUniformTexture(string,ofTexture,int){}
};
'''
CHECK=r'''
#include "conjur.h"
#include <cassert>
#include <iostream>
float testClock=0;
int main(){
 conjur player;player.setup();
 for(float knob: {0.0f,0.25f,0.5f,0.75f,1.0f}){
  player.setSpeed(knob);player.setDefaultParams({},0);
  assert(abs(player.shader.one["u_x3"]-knob)<0.00001f);
  assert(abs(player.speed-(-2.0f+4.0f*knob))<0.00001f);
  assert(player.shader.one["u_fx_knob3_available"]==1.0f);
 }
 player.setSpeed(0.5f); // legacy scaled time is stopped
 float minX=1,maxX=0,minY=1,maxY=0;
 for(int i=0;i<=400;i++){
  testClock=i;player.setDefaultParams({},0);
  auto centre=player.shader.two["u_fx_drift"];
  assert(centre.first>=0.059f && centre.first<=0.941f);
  assert(centre.second>=0.059f && centre.second<=0.941f);
  minX=min(minX,centre.first);maxX=max(maxX,centre.first);
  minY=min(minY,centre.second);maxY=max(maxY,centre.second);
 }
 assert(maxX-minX>0.87f && maxY-minY>0.87f);
 assert(player.speed==0.0f && player.shader.one["u_x3"]==0.5f);
 player.setPlay(false);testClock=500;player.setDefaultParams({},0);
 assert(player.shader.one["u_x3"]==0.5f);
 std::cout<<"PASS patched upstream: raw knob, legacy speed, independent moving centre\n";
}
'''

def main():
    p=argparse.ArgumentParser();p.add_argument('--addon',type=Path,required=True);args=p.parse_args()
    revision=subprocess.check_output(['git','-C',str(args.addon),'rev-parse','HEAD'],text=True).strip()
    if revision!=REV:p.error('Expected the documented upstream revision '+REV)
    compiler=shutil.which('g++')
    if not compiler:raise RuntimeError('g++ is required for the host control unit test')
    with tempfile.TemporaryDirectory(prefix='fx-host-') as temp:
        folder=Path(temp);(folder/'src').mkdir()
        for name in ['conjur.cpp','conjur.h']:
            data=subprocess.check_output(['git','-C',str(args.addon),'show','HEAD:src/'+name])
            (folder/'src'/name).write_bytes(data)
        for patch in ['fx-fourth-knob.patch','feedback-pingpong.patch']:
            subprocess.run(['git','apply',str(ROOT/'docs'/patch)],cwd=folder,check=True)
        (folder/'src/ofMain.h').write_text(STUB)
        (folder/'src/check.cpp').write_text(CHECK)
        subprocess.run([compiler,'-std=c++11','-I'+str(folder/'src'),str(folder/'src/conjur.cpp'),
                        str(folder/'src/check.cpp'),'-o',str(folder/'check')],check=True)
        subprocess.run([str(folder/'check')],check=True)

if __name__=='__main__':main()
