// Tile Inception — Каждая плитка содержит уменьшенное видео и собственную копию памяти.
// A: Количество плиток; B: Вложенность
// Budget: 3 texture reads.
// Original RecurBoy GLSL ES 1.00 FX. One pass; native controls only.
// u_tex1 must be the completed previous frame, not the current render target.
#ifdef GL_ES
precision mediump float;
#endif
#ifdef GL_FRAGMENT_PRECISION_HIGH
#define C highp
#else
#define C mediump
#endif
uniform sampler2D u_tex0;
uniform sampler2D u_tex1;
uniform vec2 u_resolution;
uniform float u_x0, u_x1, u_x2, ftime;
varying C vec2 v_texcoord;
const float TAU=6.2831853;
C vec2 safeUV(C vec2 p) { C vec2 h=.5/max(u_resolution,vec2(1.));return clamp(p,h,1.-h); }
C vec2 mirrorUV(C vec2 p) { return 1.-abs(mod(p,2.)-1.); }
vec3 video(C vec2 p) { return texture2D(u_tex0,safeUV(p)).rgb; }
vec3 past(C vec2 p) { return texture2D(u_tex1,safeUV(p)).rgb; }
float lum(vec3 c) { return dot(c,vec3(.299,.587,.114)); }
float wave(float x) { return sin(TAU*fract(x)); }
float tri(float x) { return 1.-4.*abs(fract(x)-.5); }
mat2 rot(float x) { float s=sin(x),c=cos(x);return mat2(c,-s,s,c); }
float hash21(vec2 p) { vec3 q=fract(vec3(p.xyx)*vec3(.1031,.1137,.1379));q+=dot(q,q.yzx+3.33);return fract((q.x+q.y)*q.z); }
C vec2 polarFold(C vec2 uv,vec2 center,float slices,float twist,float zoom) {
 C vec2 p=uv-center;float r=length(p);float angle=atan(p.y,p.x)+twist;
 float sector=TAU/slices;angle=abs(mod(angle+sector*.5,sector)-sector*.5);
 return mirrorUV(.5+vec2(cos(angle),sin(angle))*r*zoom);
}

void main() {
 C vec2 uv=safeUV(v_texcoord), px=1./max(u_resolution,vec2(1.));
    
 vec3 src=video(uv);
    
 float wet=clamp(u_x0,0.,1.),a=clamp(u_x1,0.,1.),b=clamp(u_x2,0.,1.);
    
 float t=fract(ftime);
    
 if(wet<.003) {gl_FragColor=vec4(src,1.);
    return;
    }
float n=2.+floor(10.*a);
    vec2 cell=fract(uv*n);
    vec2 q=mirrorUV((cell-.5)*(1.+2.*b)+.5+vec2(.1*wave(t),0.));
    vec3 tiny=video(q);
    vec3 old=past(mirrorUV((uv-.5)*1.06+.5));
    float border=smoothstep(.25,.48,max(abs(cell.x-.5),abs(cell.y-.5)));
    vec3 result=mix(tiny,old,border*(.2+.77*b));
    
 gl_FragColor=vec4(clamp(mix(src,result,wet),0.,1.),1.);
    
}
