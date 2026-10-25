// RecurBoy Organic FX - original GLSL ES 1.00, one pass, RGB8 feedback.
// Капиллярная акварель
// Input 1: Растекание; input 2: Пигмент по краям.
// Budget: 6 texture reads per pixel at wet > 0.
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

    vec2 d = px * (0.75 + 25.0 * a * a);
    vec3 old = past(uv);
    vec3 n = past(uv + vec2(0.0, d.y));
    vec3 s = past(uv - vec2(0.0, d.y));
    vec3 e = past(uv + vec2(d.x, 0.0));
    vec3 w = past(uv - vec2(d.x, 0.0));
    vec3 spread = (n + s + e + w) * 0.25;
    float rim = clamp(length(spread - old) * 3.0, 0.0, 1.0);
    vec3 pigment = mix(old, spread, 0.12 + 0.85 * a) * (1.0 - rim * b * 0.85);
    vec3 result = mix(src, pigment, 0.35 + 0.61 * b);
    gl_FragColor = vec4(clamp(mix(src, result, wet), 0.0, 1.0), 1.0);
}
