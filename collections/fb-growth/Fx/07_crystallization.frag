// RecurBoy Organic FX - original GLSL ES 1.00, one pass, RGB8 feedback.
// Кристаллизация
// Input 1: Размер граней; input 2: Удержание.
// Budget: 3 texture reads per pixel at wet > 0.
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

    // Rotate the lattice to make diamond facets rather than square pixels.
    float size = 2.0 + 110.0 * a * a;
    vec2 p = uv / px;
    vec2 grid = vec2(p.x + p.y, p.y - p.x) * 0.707107 / size;
    vec2 center = (floor(grid) + 0.5) * size;
    vec2 q = vec2(center.x - center.y, center.x + center.y) * 0.707107 * px;
    vec3 crystal = texture2D(u_tex0, safeUV(q)).rgb;
    vec3 old = past(uv);
    vec2 facet = fract(grid);
    float light = 0.35 + 0.65 * step(facet.x, facet.y) + 0.35 * abs(facet.x - facet.y);
    float levels = 12.0 - 10.0 * b;
    crystal = floor(crystal * levels + 0.5) / levels * light;
    float disruption = smoothstep(0.15, 0.8, length(src - old));
    vec3 result = mix(crystal, old, 0.97 * b * (1.0 - disruption));
    gl_FragColor = vec4(clamp(mix(src, result, wet), 0.0, 1.0), 1.0);
}
