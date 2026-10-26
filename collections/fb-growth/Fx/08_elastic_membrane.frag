// RecurBoy Organic FX - original GLSL ES 1.00, one pass, RGB8 feedback.
// Эластичная мембрана
// Input 1: Упругость; input 2: Затухание.
// Budget: 5 texture reads per pixel at wet > 0.
// Input 0: wet amount (0 = dry/reset); input 1/2: effect controls below.
// u_tex1 must contain a completed previous frame, never the render target.
#ifdef GL_ES
precision mediump float;
#endif
uniform sampler2D u_tex0;
uniform sampler2D u_tex1;
uniform vec2 u_resolution;
uniform float u_x0;
uniform float u_x1;
uniform float u_x2;
uniform float ftime; // host's bounded fractional time; safe for long sessions
// Keep sampling coordinates precise; color arithmetic remains mediump.
#ifdef GL_FRAGMENT_PRECISION_HIGH
#define FX_COORD highp
#else
#define FX_COORD mediump
#endif
varying FX_COORD vec2 v_texcoord;
FX_COORD vec2 safeUV(FX_COORD vec2 p) {
    FX_COORD vec2 h = 0.5 / max(u_resolution, vec2(1.0));
    return clamp(p, h, 1.0 - h);
}
vec3 past(FX_COORD vec2 p) { return texture2D(u_tex1, safeUV(p)).rgb; }
float lum(vec3 c) { return dot(c, vec3(0.299, 0.587, 0.114)); }
void main() {
    FX_COORD vec2 uv = safeUV(v_texcoord);
    FX_COORD vec2 px = 1.0 / max(u_resolution, vec2(1.0));
    vec3 src = texture2D(u_tex0, uv).rgb;
    float wet = clamp(u_x0, 0.0, 1.0);
    float a = clamp(u_x1, 0.0, 1.0);
    float b = clamp(u_x2, 0.0, 1.0);
    if (wet < 0.003) { gl_FragColor = vec4(src, 1.0); return; }

    vec3 old = past(uv);
    float h = lum(old);
    vec2 slope = vec2(lum(past(uv + vec2(px.x * 3.0, 0.0))) - h,
                      lum(past(uv + vec2(0.0, px.y * 3.0))) - h);
    float impulse = lum(src) - h;
    vec2 wobble = vec2(sin(ftime * 6.283 + uv.y * 9.0), cos(ftime * 6.283 - uv.x * 9.0));
    vec2 displacement = (slope * 2.5 + wobble * (0.12 + impulse * 1.8))
                       * px * (0.5 + 150.0 * a * a);
    vec3 stretched = texture2D(u_tex0, safeUV(uv + displacement)).rgb;
    vec3 result = mix(stretched, old, 0.05 + 0.92 * b);
    gl_FragColor = vec4(clamp(mix(src, result, wet), 0.0, 1.0), 1.0);
}
