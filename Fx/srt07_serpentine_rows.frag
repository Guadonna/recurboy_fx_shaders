// Serpentine Rows — Направление рангов чередуется в соседних полосах.
// Budget: 4 reads. A: Длина сегмента; B: Включённые яркости.
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
void main() {
 C vec2 uv=safeUV(v_texcoord), px=1./max(u_resolution,vec2(1.));

 vec3 src=video(uv);

 float wet=clamp(u_x0,0.,1.),a=clamp(u_x1,0.,1.),b=clamp(u_x2,0.,1.);

 float t=fract(ftime);

 if(wet<.003) {gl_FragColor=vec4(src,1.);
    return;
    }
vec3 v0,v1,v2;
    vec2 z=uv;
    float span=.02+.6*a*a;
    float anchor=floor((z.x+t*span)/span)*span-t*span;
    float index=floor(clamp((z.x-anchor)/span,0.,.999)*3.);
    index=mix(index,2.-index,mod(floor(uv.y*24.),2.));
    {float q=anchor+span*0.16666666666666666;
    vec2 zq=vec2(q,z.y);
    v0=video(zq);
    }{float q=anchor+span*0.5;
    vec2 zq=vec2(q,z.y);
    v1=video(zq);
    }{float q=anchor+span*0.8333333333333334;
    vec2 zq=vec2(q,z.y);
    v2=video(zq);
    }// SORT3_BEGIN
float k0=lum(v0),k1=lum(v1),k2=lum(v2);

float swap01=step(k1,k0);

vec3 low=mix(v0,v1,swap01),high=mix(v1,v0,swap01);

float klo=mix(k0,k1,swap01),khi=mix(k1,k0,swap01);

vec3 smallest=mix(low,v2,1.-step(klo,k2));

vec3 largest=mix(high,v2,1.-step(k2,khi));

vec3 middle=v0+v1+v2-smallest-largest;

vec3 selected=mix(smallest,middle,step(1.,index));

selected=mix(selected,largest,step(2.,index));

// SORT3_END
float gate=smoothstep(1.-b-.12,1.-b,lum(src));
    vec3 result=mix(src,selected,gate);

 gl_FragColor=vec4(clamp(mix(src,result,wet),0.,1.),1.);

}
