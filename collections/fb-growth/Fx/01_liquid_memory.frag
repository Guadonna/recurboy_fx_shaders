// RecurBoy Organic FX - original GLSL ES 1.00, one pass, RGB8 feedback.
// Жидкая память
// Input 1: Вязкость / размер потока; input 2: Длина следа.
// Budget: 4 texture reads per pixel at wet > 0.
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

    vec2 flow = vec2(sin(uv.y * 15.0 + ftime * 6.283),
                     1.2 + 0.65 * cos(uv.x * 11.0 - ftime * 6.283));
    vec2 drift = flow * px * (0.3 + 36.0 * a * a);
    vec2 q = (uv - 0.5) * (1.0 - 0.055 * a) + 0.5 - drift;
    vec2 smear = vec2(px.x * (0.5 + 6.0 * a), 0.0);
    vec3 old = past(q);
    vec3 fluid = (old * 2.0 + past(q + smear) + past(q - smear)) * 0.25;
    float memory = 0.32 + 0.668 * b;
    vec3 result = mix(src, fluid * 0.998, memory);
    gl_FragColor = vec4(clamp(mix(src, result, wet), 0.0, 1.0), 1.0);
}
