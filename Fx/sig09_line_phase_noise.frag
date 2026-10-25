// Line Phase Noise — Фаза каждой группы строк меняется независимо.
// Budget: 2 reads. A: Число групп; B: Размах фазового шума.
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
float angleOf(C vec2 p) { return dot(p,p)>0.0 ? atan(p.y,p.x) : 0.0; }
C vec2 polarFold(C vec2 uv,vec2 center,float slices,float twist,float zoom) {
 C vec2 p=uv-center;float r=length(p);float angle=angleOf(p)+twist;
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
float row=floor(uv.y*(3.+80.*a));
    float phase=hash21(vec2(row,floor(t*12.)));
    float d=wave(uv.x*5.+phase)*b*.16;
    vec3 result=video(mirrorUV(uv+vec2(d,0.)));

 gl_FragColor=vec4(clamp(mix(src,result,wet),0.,1.),1.);

}
