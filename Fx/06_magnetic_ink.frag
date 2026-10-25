// RecurBoy Organic FX - original GLSL ES 1.00, one pass, RGB8 feedback.
// Магнитные чернила
// Input 1: Направление поля; input 2: Длина штрихов.
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

    vec3 sx = texture2D(u_tex0, safeUV(uv + vec2(px.x * 2.0, 0.0))).rgb;
    vec3 sy = texture2D(u_tex0, safeUV(uv + vec2(0.0, px.y * 2.0))).rgb;
    vec2 grad = vec2(lum(sx) - lum(src), lum(sy) - lum(src));
    vec2 tangent = vec2(-grad.y, grad.x) / max(length(grad), 0.05);
    vec2 field = vec2(cos(a * 5.5), sin(a * 5.5));
    vec2 d = (field + tangent * 0.8) * px * (0.5 + 64.0 * b * b);
    vec3 ink = past(uv + d) * 0.75 + past(uv - d) * 0.25;
    // Contrast the fresh pigment, not the feedback: repeated gain would bleach it.
    vec3 pigment = smoothstep(vec3(0.12), vec3(0.88), src);
    vec3 result = mix(pigment, ink * 0.995, 0.35 + 0.63 * b);
    gl_FragColor = vec4(clamp(mix(src, result, wet), 0.0, 1.0), 1.0);
}
